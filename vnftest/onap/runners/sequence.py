##############################################################################
# Copyright 2018 EuropeanSoftwareMarketingLtd.
# ===================================================================
#  Licensed under the ApacheLicense, Version2.0 (the"License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License
##############################################################################
# vnftest comment: this is a modified copy of
# rally/rally/benchmark/runners/sequence.py

"""A runner that every run changes a specified input value to the step.
The input value in the sequence is specified in a list in the input file.
"""

from __future__ import absolute_import

import logging
import multiprocessing
import time
import traceback

import os

from vnftest.onap.runners import base

LOG = logging.getLogger(__name__)


def _worker_process(queue, cls, method_name, step_cfg,
                    context_cfg, aborted, output_queue):

    sequence = 1

    runner_cfg = step_cfg['runner']

    interval = runner_cfg.get("interval", 1)
    arg_name = runner_cfg.get('step_option_name')
    sequence_values = runner_cfg.get('sequence')

    if 'options' not in step_cfg:
        step_cfg['options'] = {}

    options = step_cfg['options']

    runner_cfg['runner_id'] = os.getpid()

    LOG.info("worker START, sequence_values(%s, %s), class %s",
             arg_name, sequence_values, cls)

    step = cls(step_cfg, context_cfg)
    step.setup()
    method = getattr(step, method_name)

    sla_action = None
    if "sla" in step_cfg:
        sla_action = step_cfg["sla"].get("action", "assert")

    for value in sequence_values:
        options[arg_name] = value

        LOG.debug("runner=%(runner)s seq=%(sequence)s START",
                  {"runner": runner_cfg["runner_id"], "sequence": sequence})

        data = {}
        errors = ""

        try:
            result = method(data)
        except AssertionError as assertion:
            # SLA validation failed in step, determine what to do now
            if sla_action == "assert":
                raise
            elif sla_action == "monitor":
                LOG.warning("SLA validation failed: %s", assertion.args)
                errors = assertion.args
        except Exception as e:
            errors = traceback.format_exc()
            LOG.exception(e)
        else:
            if result:
                output_queue.put(result)

        time.sleep(interval)

        step_output = {
            'timestamp': time.time(),
            'sequence': sequence,
            'data': data,
            'errors': errors
        }

        queue.put(step_output)

        LOG.debug("runner=%(runner)s seq=%(sequence)s END",
                  {"runner": runner_cfg["runner_id"], "sequence": sequence})

        sequence += 1

        if (errors and sla_action is None) or aborted.is_set():
            break

    try:
        step.teardown()
    except Exception:
        # catch any exception in teardown and convert to simple exception
        # never pass exceptions back to multiprocessing, because some exceptions can
        # be unpicklable
        # https://bugs.python.org/issue9400
        LOG.exception("")
        raise SystemExit(1)
    LOG.info("worker END")
    LOG.debug("queue.qsize() = %s", queue.qsize())
    LOG.debug("output_queue.qsize() = %s", output_queue.qsize())


class SequenceRunner(base.Runner):
    """Run a step by changing an input value defined in a list

  Parameters
    interval - time to wait between each step invocation
        type:    int
        unit:    seconds
        default: 1 sec
    step_option_name - name of the option that is increased each invocation
        type:    string
        unit:    na
        default: none
    sequence - list of values which are executed in their respective steps
        type:    [int]
        unit:    na
        default: none
    """

    __execution_type__ = 'Sequence'

    def _run_step(self, cls, method, step_cfg, context_cfg):
        name = "{}-{}-{}".format(self.__execution_type__, step_cfg.get("type"), os.getpid())
        self.process = multiprocessing.Process(
            name=name,
            target=_worker_process,
            args=(self.result_queue, cls, method, step_cfg,
                  context_cfg, self.aborted, self.output_queue))
        self.process.start()
