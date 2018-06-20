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
# yardstick/tests/unit/benchmark/core/test_task.py

import unittest

import mock
import os

from vnftest.common import constants as consts
from vnftest.core import task


class TaskTestCase(unittest.TestCase):

    def test_set_dispatchers(self):
        t = task.Task()
        output_config = {"DEFAULT": {"dispatcher": "file, http"}}
        t._set_dispatchers(output_config)
        self.assertEqual(output_config, output_config)

    @mock.patch.object(task, 'DispatcherBase')
    def test__do_output(self, mock_dispatcher):
        t = task.Task()
        output_config = {"DEFAULT": {"dispatcher": "file, http"}}

        dispatcher1 = mock.MagicMock()
        dispatcher1.__dispatcher_type__ = 'file'

        dispatcher2 = mock.MagicMock()
        dispatcher2.__dispatcher_type__ = 'http'

        mock_dispatcher.get = mock.MagicMock(return_value=[dispatcher1,
                                                           dispatcher2])
        self.assertIsNone(t._do_output(output_config, {}))

    @mock.patch.object(task, 'Context')
    @mock.patch.object(task, 'base_runner')
    def test_run(self, mock_base_runner, *args):
        step = {
            'runner': {
                'duration': 60,
                'interval': 1,
                'type': 'Duration'
            },
            'type': 'Dummy'
        }

        t = task.Task()
        runner = mock.Mock()
        runner.join.return_value = 0
        runner.get_output.return_value = {}
        runner.get_result.return_value = []
        mock_base_runner.Runner.get.return_value = runner
        t._run([step], False, "vnftest.out")
        self.assertTrue(runner.run.called)

    def test_parse_suite_no_constraint_no_args(self):
        SAMPLE_step_PATH = "no_constraint_no_args_step_sample.yaml"
        t = task.TaskParser(self._get_file_abspath(SAMPLE_step_PATH))
        with mock.patch.object(os, 'environ',
                        new={'NODE_NAME': 'huawei-pod1', 'INSTALLER_TYPE': 'compass'}):
            task_files, task_args, task_args_fnames = t.parse_suite()

        self.assertIsNone(task_args[0])
        self.assertIsNone(task_args[1])
        self.assertIsNone(task_args_fnames[0])
        self.assertIsNone(task_args_fnames[1])

    def test_parse_suite_no_constraint_with_args(self):
        SAMPLE_step_PATH = "no_constraint_with_args_step_sample.yaml"
        t = task.TaskParser(self._get_file_abspath(SAMPLE_step_PATH))
        with mock.patch.object(os, 'environ',
                        new={'NODE_NAME': 'huawei-pod1', 'INSTALLER_TYPE': 'compass'}):
            task_files, task_args, task_args_fnames = t.parse_suite()

        self.assertIsNone(task_args[0])
        self.assertEqual(task_args[1],
                         '{"host": "node1.LF","target": "node2.LF"}')
        self.assertIsNone(task_args_fnames[0])
        self.assertIsNone(task_args_fnames[1])

    def test_parse_suite_with_constraint_no_args(self):
        SAMPLE_step_PATH = "with_constraint_no_args_step_sample.yaml"
        t = task.TaskParser(self._get_file_abspath(SAMPLE_step_PATH))
        with mock.patch.object(os, 'environ',
                        new={'NODE_NAME': 'huawei-pod1', 'INSTALLER_TYPE': 'compass'}):
            task_files, task_args, task_args_fnames = t.parse_suite()

        self.assertIsNone(task_args[0])
        self.assertIsNone(task_args[1])
        self.assertIsNone(task_args_fnames[0])
        self.assertIsNone(task_args_fnames[1])

    def test_parse_suite_with_constraint_with_args(self):
        SAMPLE_step_PATH = "with_constraint_with_args_step_sample.yaml"
        t = task.TaskParser(self._get_file_abspath(SAMPLE_step_PATH))
        with mock.patch('os.environ',
                        new={'NODE_NAME': 'huawei-pod1', 'INSTALLER_TYPE': 'compass'}):
            task_files, task_args, task_args_fnames = t.parse_suite()

        self.assertIsNone(task_args[0])
        self.assertEqual(task_args[1],
                         '{"host": "node1.LF","target": "node2.LF"}')
        self.assertIsNone(task_args_fnames[0])
        self.assertIsNone(task_args_fnames[1])

    @mock.patch('six.moves.builtins.open', side_effect=mock.mock_open())
    @mock.patch.object(task, 'utils')
    @mock.patch('logging.root')
    def test_set_log(self, mock_logging_root, *args):
        task_obj = task.Task()
        task_obj.task_id = 'task_id'
        task_obj._set_log()
        mock_logging_root.addHandler.assert_called()

    def _get_file_abspath(self, filename):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(curr_path, filename)
        return file_path

    def change_to_abspath(self, filepath):
        return os.path.join(consts.VNFTEST_ROOT_PATH, filepath)
