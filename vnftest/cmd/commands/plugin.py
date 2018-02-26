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
# yardstick/cmd/commands/plugin.py
""" Handler for vnftest command 'plugin' """

from __future__ import print_function

from __future__ import absolute_import
from vnftest.onap.core.plugin import Plugin
from vnftest.common.utils import cliargs
from vnftest.cmd.commands import change_osloobj_to_paras


class PluginCommands(object):   # pragma: no cover
    """Plugin commands.

       Set of commands to manage plugins.
    """

    @cliargs("input_file", type=str, help="path to plugin configuration file",
             nargs=1)
    def do_install(self, args):
        """Install a plugin."""
        param = change_osloobj_to_paras(args)
        Plugin().install(param)

    @cliargs("input_file", type=str, help="path to plugin configuration file",
             nargs=1)
    def do_remove(self, args):
        """Remove a plugin."""
        param = change_osloobj_to_paras(args)
        Plugin().remove(param)
