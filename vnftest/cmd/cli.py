#!/usr/bin/env python
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
# yardstick/cmd/cli.py
"""
Command-line interface to vnftest
"""

from __future__ import absolute_import
import logging
import os
import sys

from pkg_resources import get_distribution
from argparse import RawDescriptionHelpFormatter
from oslo_config import cfg

from vnftest import _init_logging, _LOG_STREAM_HDLR
from vnftest.cmd.commands import task
from vnftest.cmd.commands import runner
from vnftest.cmd.commands import step
from vnftest.cmd.commands import testcase
from vnftest.cmd.commands import plugin
from vnftest.cmd.commands import env
from vnftest.cmd.commands import report

CONF = cfg.CONF
cli_opts = [
    cfg.BoolOpt('debug',
                short='d',
                default=False,
                help='increase output verbosity to debug')
]
CONF.register_cli_opts(cli_opts)

CONFIG_SEARCH_PATHS = [sys.prefix + "/etc/vnftest",
                       "~/.vnftest",
                       "/etc/vnftest"]


def find_config_files(path_list):
    for path in path_list:
        abspath = os.path.abspath(os.path.expanduser(path))
        confname = abspath + "/vnftest.conf"
        if os.path.isfile(confname):
            return [confname]

    return None


class VnftestCLI():   # pragma: no cover
    """Command-line interface to vnftest"""

    # Command categories
    categories = {
        'task': task.TaskCommands,
        'runner': runner.RunnerCommands,
        'step': step.StepCommands,
        'testcase': testcase.TestcaseCommands,
        'plugin': plugin.PluginCommands,
        'env': env.EnvCommand,
        'report': report.ReportCommands
    }

    def __init__(self):
        self.opts = []
        self._version = 'vnftest version %s ' % \
            get_distribution('vnftest').version

    def _find_actions(self, subparsers, actions_module):
        """find action methods"""
        # Find action methods inside actions_module and
        # add them to the command parser.
        # The 'actions_module' argument may be a class
        # or module. Action methods start with 'do_'
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            arguments = getattr(callback, 'arguments', [])
            subparser = subparsers.add_parser(
                command,
                description=desc
            )
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def _add_command_parsers(self, categories, subparsers):
        """add commands to command-line parser"""
        for category in categories:
            command_object = categories[category]()
            desc = command_object.__doc__ or ''
            subparser = subparsers.add_parser(
                category, description=desc,
                formatter_class=RawDescriptionHelpFormatter
            )
            subparser.set_defaults(command_object=command_object)
            cmd_subparsers = subparser.add_subparsers(title='subcommands')
            self._find_actions(cmd_subparsers, command_object)

    def _register_cli_opt(self):

        # register subcommands to parse additional command line arguments
        def parser(subparsers):
            self._add_command_parsers(VnftestCLI.categories, subparsers)

        category_opt = cfg.SubCommandOpt("category",
                                         title="Command categories",
                                         help="Available categories",
                                         handler=parser)
        self._register_opt(category_opt)

    def _register_opt(self, opt):

        CONF.register_cli_opt(opt)
        self.opts.append(opt)

    def _load_cli_config(self, argv):

        # load CLI args and config files
        CONF(argv, project="vnftest", version=self._version,
             default_config_files=find_config_files(CONFIG_SEARCH_PATHS))

    def _handle_global_opts(self):

        _init_logging()
        if CONF.debug:
            _LOG_STREAM_HDLR.setLevel(logging.DEBUG)

    def _dispatch_func_notask(self):

        # dispatch to category parser
        func = CONF.category.func
        func(CONF.category)

    def _dispatch_func_task(self, task_id):

        # dispatch to category parser
        func = CONF.category.func
        func(CONF.category, task_id=task_id)

    def _clear_config_opts(self):

        CONF.clear()
        CONF.unregister_opts(self.opts)

    def main(self, argv):    # pragma: no cover
        """run the command line interface"""
        try:
            self._register_cli_opt()

            self._load_cli_config(argv)

            self._handle_global_opts()

            self._dispatch_func_notask()
        finally:
            self._clear_config_opts()

    def api(self, argv, task_id):    # pragma: no cover
        """run the api interface"""
        try:
            self._register_cli_opt()

            self._load_cli_config(argv)

            self._handle_global_opts()

            self._dispatch_func_task(task_id)
        finally:
            self._clear_config_opts()
