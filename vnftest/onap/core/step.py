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
# yardstick/benchmark/core/step.py

""" Handler for vnftest command 'step' """

from __future__ import absolute_import
import prettytable

from vnftest.onap.steps.base import Step


class Steps(object):    # pragma: no cover
    """Step commands.

       Set of commands to discover and display step types.
    """

    def list_all(self, *args):
        """List existing step types"""
        types = Step.get_types()
        step_table = prettytable.PrettyTable(['Type', 'Description'])
        step_table.align = 'l'
        for step_class in types:
            step_table.add_row([step_class.get_step_type(),
                                    step_class.get_description()])
        print(step_table)

    def show(self, args):
        """Show details of a specific step type"""
        stype = Step.get_cls(args.type[0])
        print(stype.__doc__)
