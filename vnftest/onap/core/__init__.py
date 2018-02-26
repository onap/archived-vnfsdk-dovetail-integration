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
# yardstick/benchmark/core/init.py
"""
Vnftest core.
"""

from __future__ import print_function


class Param(object):
    """This class converts a parameter dictionary to an object."""

    def __init__(self, kwargs):
        # list
        self.inputfile = kwargs.get('inputfile')
        self.task_args = kwargs.get('task-args')
        self.task_args_file = kwargs.get('task-args-file')
        self.keep_deploy = kwargs.get('keep-deploy')
        self.parse_only = kwargs.get('parse-only')
        self.output_file = kwargs.get('output-file', '/tmp/vnftest.out')
        self.suite = kwargs.get('suite')
        self.task_id = kwargs.get('task_id')
        self.yaml_name = kwargs.get('yaml_name')

        # list
        self.input_file = kwargs.get('input_file')

        # list
        self.casename = kwargs.get('casename')

        # list
        self.type = kwargs.get('type')
