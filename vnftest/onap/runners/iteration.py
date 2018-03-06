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
# rally/rally/benchmark/runners/iteration.py

"""A runner that runs a configurable number of times before it returns
"""

from __future__ import absolute_import

import logging
import multiprocessing
import time
import traceback

import os

from vnftest.onap.runners import base

LOG = logging.getLogger(__name__)


QUEUE_PUT_TIMEOUT = 10


def _worker_process(queue, cls, method_name, step_cfg,
                    context_cfg, aborted, output_queue):

    sequence = 1

    runner_cfg = step_cfg['runner']

    interval = runner_cfg.get("interval", 1)
    iterations = runner_cfg.get("iterations", 1)
    run_step = runner_cfg.get("run_step", "setup,run,teardown")

    delta = runner_cfg.get("delta", 2)
    LOG.info("worker START, iterations %d times, class %s", iterations, cls)

    runner_cfg['runner_id'] = os.getpid()

    step = cls(step_cfg, context_cfg)
    if "setup" in run_step:
        step.setup()

    method = getattr(step, method_name)

    sla_action = None
    if "sla" in step_cfg:
        sla_action = step_cfg["sla"].get("action", "assert")
    if "run" in run_step:
        while True:

            LOG.debug("runner=%(runner)s seq=%(sequence)s START",
                      {"runner": runner_cfg["runner_id"],
                       "sequence": sequence})

            data = {}
            errors = []

            try:
                result = method(data)
                if result:
                    # add timeout for put so we don't block test
                    # if we do timeout we don't care about dropping individual KPIs
                    output_queue.put(result, True, QUEUE_PUT_TIMEOUT)
            except AssertionError as assertion:
                # SLA validation failed in step, determine what to do now
                if sla_action == "assert":
                    raise
                elif sla_action == "monitor":
                    LOG.warning("SLA validation failed: %s", assertion.args)
                    errors.append(assertion.args)
                elif sla_action == "rate-control":
                    try:
                        step_cfg['options']['rate']
                    except KeyError:
                        step_cfg.setdefault('options', {})
                        step_cfg['options']['rate'] = 100

                    step_cfg['options']['rate'] -= delta
                    sequence = 1
                    continue
            except Exception:
                errors.append(traceback.format_exc())
                LOG.exception("")

            time.sleep(interval)

            step_output = {
                'timestamp': time.time(),
                'sequence': sequence,
                'data': data,
                'errors': errors
            }

            queue.put(step_output, True, QUEUE_PUT_TIMEOUT)

            LOG.debug("runner=%(runner)s seq=%(sequence)s END",
                      {"runner": runner_cfg["runner_id"],
                       "sequence": sequence})

            sequence += 1

            if (errors and sla_action is None) or \
                    (sequence > iterations or aborted.is_set()):
                LOG.info("worker END")
                break
    if "teardown" in run_step:
        try:
            step.teardown()
        except Exception:
            # catch any exception in teardown and convert to simple exception
            # never pass exceptions back to multiprocessing, because some exceptions can
            # be unpicklable
            # https://bugs.python.org/issue9400
            LOG.exception("")
            raise SystemExit(1)

    LOG.debug("queue.qsize() = %s", queue.qsize())
    LOG.debug("output_queue.qsize() = %s", output_queue.qsize())


class IterationRunner(base.Runner):
    """Run a step for a configurable number of times

If the step ends before the time has elapsed, it will be started again.

  Parameters
    iterations - amount of times the step will be run for
        type:    int
        unit:    na
        default: 1
    interval - time to wait between each step invocation
        type:    int
        unit:    seconds
        default: 1 sec
    """
    __execution_type__ = 'Iteration'

    def _run_step(self, cls, method, step_cfg, context_cfg):
        name = "{}-{}-{}".format(self.__execution_type__, step_cfg.get("type"), os.getpid())
        self.process = multiprocessing.Process(
            name=name,
            target=_worker_process,
            args=(self.result_queue, cls, method, step_cfg,
                  context_cfg, self.aborted, self.output_queue))
        self.process.start()
