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
# yardstick/benchmark/core/task.py

""" Handler for vnftest command 'task' """

from __future__ import absolute_import
from __future__ import print_function

import atexit
import collections
import copy
import logging
import sys
import time
import uuid
from collections import OrderedDict

import ipaddress
import os
import yaml
from jinja2 import Environment
from six.moves import filter
from vnftest.runners import base as base_runner

from vnftest.contexts.base import Context
from vnftest.contexts.csar import CSARContext
from vnftest.runners import base as base_runner
from vnftest.runners.duration import DurationRunner
from vnftest.runners.iteration import IterationRunner
from vnftest.common.constants import CONF_FILE
from vnftest.common.html_template import report_template
from vnftest.common.task_template import TaskTemplate
from vnftest.common.yaml_loader import yaml_load
from vnftest.contexts.base import Context
from vnftest.dispatcher.base import Base as DispatcherBase
from vnftest.common.task_template import TaskTemplate
from vnftest.common import utils
from vnftest.common import constants
from vnftest.common.html_template import report_template

output_file_default = "/tmp/vnftest.out"
LOG = logging.getLogger(__name__)


class Task(object):     # pragma: no cover
    """Task commands.

       Set of commands to manage benchmark tasks.
    """

    def __init__(self):
        self.context = None
        self.outputs = {}

    def _set_dispatchers(self, output_config):
        dispatchers = output_config.get('DEFAULT', {}).get('dispatcher',
                                                           'file')
        out_types = [s.strip() for s in dispatchers.split(',')]
        output_config['DEFAULT']['dispatcher'] = out_types

    def start(self, args, **kwargs):
        Context.initialize(args.vnfdescriptor, args.environment)
        atexit.register(self.atexit_handler)

        task_id = getattr(args, 'task_id')
        self.task_id = task_id if task_id else str(uuid.uuid4())

        self._set_log()

        try:
            output_config = utils.parse_ini_file(CONF_FILE)
        except Exception:
            # all error will be ignore, the default value is {}
            output_config = {}

        self._init_output_config(output_config)
        self._set_output_config(output_config, args.output_file)
        LOG.debug('Output configuration is: %s', output_config)

        self._set_dispatchers(output_config)

        # update dispatcher list
        if 'file' in output_config['DEFAULT']['dispatcher']:
            result = {'status': 0, 'result': {}}
            utils.write_json_to_file(args.output_file, result)

        total_start_time = time.time()
        parser = TaskParser(args.inputfile)

        if args.suite:
            # 1.parse suite, return suite_params info
            task_files, task_args, task_args_fnames = \
                parser.parse_suite()
        else:
            task_files = [parser.path]
            task_args = [args.task_args]
            task_args_fnames = [args.task_args_file]

        LOG.debug("task_files:%s, task_args:%s, task_args_fnames:%s",
                  task_files, task_args, task_args_fnames)

        if args.parse_only:
            sys.exit(0)

        testcases = {}
        # parse task_files
        for i in range(0, len(task_files)):
            one_task_start_time = time.time()
            # the output of the previous task is the input of the new task
            inputs = copy.deepcopy(self.outputs)
            parser.path = task_files[i]
            steps, run_in_parallel, meet_precondition, ret_context = \
                parser.parse_task(self.task_id, task_args[i],
                                  task_args_fnames[i], inputs)

            self.context = ret_context

            if not meet_precondition:
                LOG.info("meet_precondition is %s, please check envrionment",
                         meet_precondition)
                continue

            case_name = os.path.splitext(os.path.basename(task_files[i]))[0]
            try:
                data = self._run(steps, run_in_parallel, args.output_file)
            except KeyboardInterrupt:
                raise
            except Exception:
                LOG.error('Testcase: "%s" FAILED!!!', case_name, exc_info=True)
                testcases[case_name] = {'criteria': 'FAIL', 'tc_data': []}
            else:
                criteria = self.evaluate_task_criteria(data)
                testcases[case_name] = {'criteria': criteria, 'tc_data': data, 'output': self.outputs}

            if args.keep_deploy:
                # keep deployment, forget about stack
                # (hide it for exit handler)
                self.context = None
            else:
                self.context.undeploy()
                self.context = None
            one_task_end_time = time.time()
            LOG.info("Task %s finished in %d secs", task_files[i],
                     one_task_end_time - one_task_start_time)

        result = self._get_format_result(testcases)

        self._do_output(output_config, result)
        self._generate_reporting(result)

        total_end_time = time.time()
        LOG.info("Total finished in %d secs",
                 total_end_time - total_start_time)

        step = steps[0]
        LOG.info("To generate report, execute command "
                 "'vnftest report generate %(task_id)s %(tc)s'", step)
        LOG.info("Task ALL DONE, exiting")
        return result

    def _generate_reporting(self, result):
        env = Environment()
        with open(constants.REPORTING_FILE, 'w') as f:
            f.write(env.from_string(report_template).render(result))

        LOG.info("Report can be found in '%s'", constants.REPORTING_FILE)

    def _set_log(self):
        log_format = '%(asctime)s %(name)s %(filename)s:%(lineno)d %(levelname)s %(message)s'
        log_formatter = logging.Formatter(log_format)

        utils.makedirs(constants.TASK_LOG_DIR)
        log_path = os.path.join(constants.TASK_LOG_DIR, '{}.log'.format(self.task_id))
        log_handler = logging.FileHandler(log_path)
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.DEBUG)

        logging.root.addHandler(log_handler)

    def _init_output_config(self, output_config):
        output_config.setdefault('DEFAULT', {})
        output_config.setdefault('dispatcher_http', {})
        output_config.setdefault('dispatcher_file', {})
        output_config.setdefault('dispatcher_influxdb', {})

    def _set_output_config(self, output_config, file_path):
        try:
            out_type = os.environ['DISPATCHER']
        except KeyError:
            output_config['DEFAULT'].setdefault('dispatcher', 'file')
        else:
            output_config['DEFAULT']['dispatcher'] = out_type

        output_config['dispatcher_file']['file_path'] = file_path

        try:
            target = os.environ['TARGET']
        except KeyError:
            pass
        else:
            k = 'dispatcher_{}'.format(output_config['DEFAULT']['dispatcher'])
            output_config[k]['target'] = target

    def _get_format_result(self, testcases):
        criteria = self._get_task_criteria(testcases)

        info = {
            'deploy_step': os.environ.get('DEPLOY_STEP', 'unknown'),
            'installer': os.environ.get('INSTALLER_TYPE', 'unknown'),
            'pod_name': os.environ.get('NODE_NAME', 'unknown'),
            'version': os.environ.get('VNFTEST_BRANCH', 'unknown')
        }

        result = {
            'status': 1,
            'result': {
                'criteria': criteria,
                'task_id': self.task_id,
                'info': info,
                'testcases': testcases
            }
        }

        return result

    def _get_task_criteria(self, testcases):
        criteria = any(t.get('criteria') != 'PASS' for t in testcases.values())
        if criteria:
            return 'FAIL'
        else:
            return 'PASS'

    def evaluate_task_criteria(self, steps_result_list):
        for step_result in steps_result_list:
            errors_list = step_result['errors']
            if errors_list is not None and len(errors_list) > 0:
                return 'FAIL'
        return 'PASS'

    def _do_output(self, output_config, result):
        dispatchers = DispatcherBase.get(output_config)

        for dispatcher in dispatchers:
            dispatcher.flush_result_data(result)

    def _run(self, steps, run_in_parallel, output_file):
        """Deploys context and calls runners"""
        if self.context:
            self.context.deploy()
        background_runners = []

        result = []
        # Start all background steps
        for step in filter(_is_background_step, steps):
            step["runner"] = dict(type="Duration", duration=1000000000)
            runner = self.run_one_step(step, output_file)
            background_runners.append(runner)

        runners = []
        if run_in_parallel:
            for step in steps:
                if not _is_background_step(step):
                    runner = self.run_one_step(step, output_file)
                    runners.append(runner)

            # Wait for runners to finish
            for runner in runners:
                status = runner_join(runner, background_runners, self.outputs, result)
                if status != 0:
                    raise RuntimeError(
                        "{0} runner status {1}".format(runner.__execution_type__, status))
                LOG.info("Runner ended, output in %s", output_file)
        else:
            # run serially
            for step in steps:
                if not _is_background_step(step):
                    runner = self.run_one_step(step, output_file)
                    status = runner_join(runner, background_runners, self.outputs, result)
                    if status != 0:
                        LOG.error('Step NO.%s: "%s" ERROR!',
                                  steps.index(step) + 1,
                                  step.get('type'))
                        raise RuntimeError(
                            "{0} runner status {1}".format(runner.__execution_type__, status))
                    LOG.info("Runner ended, output in %s", output_file)

        # Abort background runners
        for runner in background_runners:
            runner.abort()

        # Wait for background runners to finish
        for runner in background_runners:
            status = runner.join(self.outputs, result)
            if status is None:
                # Nuke if it did not stop nicely
                base_runner.Runner.terminate(runner)
                runner.join(self.outputs, result)
            base_runner.Runner.release(runner)

            print("Background task ended")
        return result

    def atexit_handler(self):
        """handler for process termination"""
        base_runner.Runner.terminate_all()

        if self.context:
            LOG.info("Undeploying context")
            self.context.undeploy()

    def _parse_options(self, op):
        if isinstance(op, dict):
            return {k: self._parse_options(v) for k, v in op.items()}
        elif isinstance(op, list):
            return [self._parse_options(v) for v in op]
        elif isinstance(op, str):
            return self.outputs.get(op[1:]) if op.startswith('$') else op
        else:
            return op

    def run_one_step(self, step_cfg, output_file):
        """run one step using context"""
        # default runner is Iteration
        if 'runner' not in step_cfg:
            step_cfg['runner'] = dict(type="Iteration", iterations=1)
        runner_cfg = step_cfg['runner']
        runner_cfg['output_filename'] = output_file
        options = step_cfg.get('options', {})
        step_cfg['options'] = self._parse_options(options)
        runner = base_runner.Runner.get(runner_cfg)

        LOG.info("Starting runner of type '%s'", runner_cfg["type"])
        # Previous steps output is the input of the next step.
        input_params = copy.deepcopy(self.outputs)
        runner.run(step_cfg, self.context, input_params)
        return runner


class TaskParser(object):       # pragma: no cover
    """Parser for task config files in yaml format"""

    def __init__(self, path):
        self.path = path

    def _meet_constraint(self, task, cur_pod, cur_installer):
        if "constraint" in task:
            constraint = task.get('constraint', None)
            if constraint is not None:
                tc_fit_pod = constraint.get('pod', None)
                tc_fit_installer = constraint.get('installer', None)
                LOG.info("cur_pod:%s, cur_installer:%s,tc_constraints:%s",
                         cur_pod, cur_installer, constraint)
                if (cur_pod is None) or (tc_fit_pod and cur_pod not in tc_fit_pod):
                    return False
                if (cur_installer is None) or (tc_fit_installer and cur_installer
                                               not in tc_fit_installer):
                    return False
        return True

    def _get_task_para(self, task, cur_pod):
        task_args = task.get('task_args', None)
        if task_args is not None:
            task_args = task_args.get(cur_pod, task_args.get('default'))
        task_args_fnames = task.get('task_args_fnames', None)
        if task_args_fnames is not None:
            task_args_fnames = task_args_fnames.get(cur_pod, None)
        return task_args, task_args_fnames

    def parse_suite(self):
        """parse the suite file and return a list of task config file paths
           and lists of optional parameters if present"""
        LOG.info("\nParsing suite file:%s", self.path)

        try:
            with open(self.path) as stream:
                cfg = yaml_load(stream)
        except IOError as ioerror:
            sys.exit(ioerror)

        self._check_schema(cfg["schema"], "suite")
        LOG.info("\nStarting step:%s", cfg["name"])

        cur_pod = os.environ.get('NODE_NAME', None)
        cur_installer = os.environ.get('INSTALLER_TYPE', None)

        valid_task_files = []
        valid_task_args = []
        valid_task_args_fnames = []

        for task in cfg["test_cases"]:
            # 1.check file_name
            if "file_name" in task:
                task_fname = task.get('file_name', None)
                if task_fname is None:
                    continue
            else:
                continue
            # 2.check constraint
            if self._meet_constraint(task, cur_pod, cur_installer):
                valid_task_files.append(task_fname)
            else:
                continue
            # 3.fetch task parameters
            task_args, task_args_fnames = self._get_task_para(task, cur_pod)
            valid_task_args.append(task_args)
            valid_task_args_fnames.append(task_args_fnames)

        return valid_task_files, valid_task_args, valid_task_args_fnames

    def parse_task(self, task_id, task_args=None, task_args_file=None, inputs=None):
        """parses the task file and return an context and step instances"""
        LOG.info("Parsing task config: %s", self.path)

        try:
            kw = {}
            kw.update(inputs)
            if task_args_file:
                with open(task_args_file) as f:
                    kw.update(parse_task_args("task_args_file", f.read()))
            kw.update(parse_task_args("task_args", task_args))
            kw['vnf_descriptor'] = Context.vnf_descriptor
        except TypeError:
            raise TypeError()

        try:
            with utils.load_resource(self.path) as f:
                try:
                    input_task = f.read()
                    rendered_task = TaskTemplate.render(input_task, **kw)
                except Exception as e:
                    LOG.exception('Failed to render template:\n%s\n', input_task)
                    raise e
                LOG.debug("Input task is:\n%s\n", rendered_task)

                cfg = yaml_load(rendered_task)
        except IOError as ioerror:
            sys.exit(ioerror)

        self._check_schema(cfg["schema"], "task")
        meet_precondition = self._check_precondition(cfg)

        if "context" in cfg:
            context_cfg = cfg["context"]
        else:
            context_cfg = {"type": "Dummy"}

        name_suffix = '-{}'.format(task_id[:8])
        try:
            context_cfg['name'] = '{}{}'.format(context_cfg['name'],
                                              name_suffix)
        except KeyError:
            pass
        # default to CSAR context
        context_type = context_cfg.get("type", "CSAR")
        context = Context.get(context_type)
        context.init(context_cfg)

        run_in_parallel = cfg.get("run_in_parallel", False)

        # add tc and task id for influxdb extended tags
        for step in cfg["steps"]:
            task_name = os.path.splitext(os.path.basename(self.path))[0]
            step["tc"] = task_name
            step["task_id"] = task_id
            # embed task path into step so we can load other files
            # relative to task path
            step["task_path"] = os.path.dirname(self.path)

        # TODO we need something better here, a class that represent the file
        return cfg["steps"], run_in_parallel, meet_precondition, context

    def _check_schema(self, cfg_schema, schema_type):
        """Check if config file is using the correct schema type"""

        if cfg_schema != "vnftest:" + schema_type + ":0.1":
            sys.exit("error: file %s has unknown schema %s" % (self.path,
                                                               cfg_schema))

    def _check_precondition(self, cfg):
        """Check if the environment meet the precondition"""

        if "precondition" in cfg:
            precondition = cfg["precondition"]
            installer_type = precondition.get("installer_type", None)
            deploy_steps = precondition.get("deploy_steps", None)
            tc_fit_pods = precondition.get("pod_name", None)
            installer_type_env = os.environ.get('INSTALL_TYPE', None)
            deploy_step_env = os.environ.get('DEPLOY_STEP', None)
            pod_name_env = os.environ.get('NODE_NAME', None)

            LOG.info("installer_type: %s, installer_type_env: %s",
                     installer_type, installer_type_env)
            LOG.info("deploy_steps: %s, deploy_step_env: %s",
                     deploy_steps, deploy_step_env)
            LOG.info("tc_fit_pods: %s, pod_name_env: %s",
                     tc_fit_pods, pod_name_env)
            if installer_type and installer_type_env:
                if installer_type_env not in installer_type:
                    return False
            if deploy_steps and deploy_step_env:
                deploy_steps_list = deploy_steps.split(',')
                for deploy_step in deploy_steps_list:
                    if deploy_step_env.startswith(deploy_step):
                        return True
                return False
            if tc_fit_pods and pod_name_env:
                if pod_name_env not in tc_fit_pods:
                    return False
        return True


def is_ip_addr(addr):
    """check if string addr is an IP address"""
    try:
        addr = addr.get('public_ip_attr', addr.get('private_ip_attr'))
    except AttributeError:
        pass

    try:
        ipaddress.ip_address(addr.encode('utf-8'))
    except ValueError:
        return False
    else:
        return True


def _is_background_step(step):
    if "run_in_background" in step:
        return step["run_in_background"]
    else:
        return False


def runner_join(runner, background_runners, outputs, result):
    """join (wait for) a runner, exit process at runner failure
    :param background_runners:
    :type background_runners:
    :param outputs:
    :type outputs: dict
    :param result:
    :type result: list
    """
    while runner.poll() is None:
        outputs.update(runner.get_output())
        result.extend(runner.get_result())
        # drain all the background runner queues
        for background in background_runners:
            outputs.update(background.get_output())
            result.extend(background.get_result())
    status = runner.join(outputs, result)
    base_runner.Runner.release(runner)
    return status


def print_invalid_header(source_name, args):
    print("Invalid %(source)s passed:\n\n %(args)s\n"
          % {"source": source_name, "args": args})


def parse_task_args(src_name, args):
    if isinstance(args, collections.Mapping):
        return args

    try:
        kw = args and yaml_load(args)
        kw = {} if kw is None else kw
    except yaml.parser.ParserError as e:
        print_invalid_header(src_name, args)
        print("%(source)s has to be YAML. Details:\n\n%(err)s\n"
              % {"source": src_name, "err": e})
        raise TypeError()

    if not isinstance(kw, dict):
        print_invalid_header(src_name, args)
        print("%(src)s had to be dict, actually %(src_type)s\n"
              % {"src": src_name, "src_type": type(kw)})
        raise TypeError()
    return kw