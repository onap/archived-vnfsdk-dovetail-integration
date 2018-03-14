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
# yardstick/benchmark/core/runner.py
""" Handler for vnftest command 'runner' """

from __future__ import absolute_import

import prettytable

from vnftest.runners.base import Runner


class Runners(object):  # pragma: no cover
    """Runner commands.

       Set of commands to discover and display runner types.
    """

    def list_all(self, *args):
        """List existing runner types"""
        types = Runner.get_types()
        runner_table = prettytable.PrettyTable(['Type', 'Description'])
        runner_table.align = 'l'
        for rtype in types:
            runner_table.add_row([rtype.__execution_type__,
                                  rtype.__doc__.split("\n")[0]])
        print(runner_table)

    def show(self, args):
        """Show details of a specific runner type"""
        rtype = Runner.get_cls(args.type[0])
        print(rtype.__doc__)
