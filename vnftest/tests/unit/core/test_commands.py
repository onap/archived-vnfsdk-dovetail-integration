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
# yardstick/tests/functional/test_cli_runner.py

import unittest

from vnftest.cmd.commands.runner import RunnerCommands
from vnftest.cmd.commands.step import StepCommands
from vnftest.core import Param
from vnftest.core.runner import Runners
from vnftest.core.step import Steps
from vnftest.runners.iteration import IterationRunner
from vnftest.runners.duration import DurationRunner
from vnftest.onap.onap_api_call import OnapApiCall
from cStringIO import StringIO
import sys


class Capture(list):

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


class CommandsTestCase(unittest.TestCase):

    def setUp(self):
        super(CommandsTestCase, self).setUp()

    def test_runner_list(self):
        runner_cmd = RunnerCommands()
        with Capture() as output:
            runner_cmd.do_list(None)
        self.assert_text_in_lines(output, ["Duration", "Iteration"])

    def test_step_list(self):
        step_cmd = StepCommands()
        with Capture() as output:
            step_cmd.do_list(None)
        self.assert_text_in_lines(output, ["OnapApiCall"])

    def test_runner_show_Duration(self):
        param = Param({})
        setattr(param, 'type', ['Duration'])
        with Capture() as output:
            Runners().show(param)
        self.assert_text_in_lines(output, ["duration - amount of time"])

    def test_runner_show_Iteration(self):
        param = Param({})
        setattr(param, 'type', ['Iteration'])
        with Capture() as output:
            Runners().show(param)
        self.assert_text_in_lines(output, ["iterations - amount of times"])

    def test_step_show_OnapApiCall(self):
        param = Param({})
        setattr(param, 'type', ['OnapApiCall'])
        with Capture() as output:
            Steps().show(param)
        self.assert_text_in_lines(output, ["Call ONAP API"])

    def assert_text_in_lines(self, lines, texts):
        for text in texts:
            found = False
            for line in lines:
                if text in line:
                    found = True
                    break
            self.assertTrue(found, "Not Found: " + text)
