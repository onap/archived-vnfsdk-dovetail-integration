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
# yardstick/benchmark/core/report.py
""" Handler for vnftest command 'report' """

from __future__ import absolute_import
from __future__ import print_function

import ast
import re
import uuid

from django.conf import settings
from django.template import Context
from django.template import Template
from oslo_utils import encodeutils
from oslo_utils import uuidutils

from vnftest.common import constants as consts
from vnftest.common.html_template import template
from vnftest.common.utils import cliargs

settings.configure()


class Report(object):
    """Report commands.

    Set of commands to manage benchmark tasks.
    """

    def __init__(self):
        self.Timestamp = []
        self.yaml_name = ""
        self.task_id = ""

    def _validate(self, yaml_name, task_id):
        if re.match("^[a-z0-9_-]+$", yaml_name):
            self.yaml_name = yaml_name
        else:
            raise ValueError("invalid yaml_name", yaml_name)

        if uuidutils.is_uuid_like(task_id):
            task_id = '{' + task_id + '}'
            task_uuid = (uuid.UUID(task_id))
            self.task_id = task_uuid
        else:
            raise ValueError("invalid task_id", task_id)

    # def _get_fieldkeys(self):
        # fieldkeys_cmd = "show field keys from \"%s\""
        # fieldkeys_query = fieldkeys_cmd % (self.yaml_name)
        # query_exec = influx.query(fieldkeys_query)
        # if query_exec:
        #     return query_exec
        # else:
        #     raise KeyError("Task ID or Test case not found..")

    #def _get_tasks(self):
        # task_cmd = "select * from \"%s\" where task_id= '%s'"
        # task_query = task_cmd % (self.yaml_name, self.task_id)
        # query_exec = influx.query(task_query)
        # if query_exec:
        #     return query_exec
        # else:
        #     raise KeyError("Task ID or Test case not found..")

    @cliargs("task_id", type=str, help=" task id", nargs=1)
    @cliargs("yaml_name", type=str, help=" Yaml file Name", nargs=1)
    def generate(self, args):
        """Start report generation."""
        self._validate(args.yaml_name[0], args.task_id[0])

        self.db_fieldkeys = self._get_fieldkeys()

        self.db_task = self._get_tasks()

        field_keys = []
        temp_series = []
        table_vals = {}

        field_keys = [encodeutils.to_utf8(field['fieldKey'])
                      for field in self.db_fieldkeys]

        for key in field_keys:
            self.Timestamp = []
            series = {}
            values = []
            for task in self.db_task:
                task_time = encodeutils.to_utf8(task['time'])
                if not isinstance(task_time, str):
                    task_time = str(task_time, 'utf8')
                    key = str(key, 'utf8')
                task_time = task_time[11:]
                head, sep, tail = task_time.partition('.')
                task_time = head + "." + tail[:6]
                self.Timestamp.append(task_time)
                if isinstance(task[key], float) is True:
                    values.append(task[key])
                else:
                    values.append(ast.literal_eval(task[key]))
            table_vals['Timestamp'] = self.Timestamp
            table_vals[key] = values
            series['name'] = key
            series['data'] = values
            temp_series.append(series)

        Template_html = Template(template)
        Context_html = Context({"series": temp_series,
                                "Timestamp": self.Timestamp,
                                "task_id": self.task_id,
                                "table": table_vals})
        with open(consts.DEFAULT_HTML_FILE, "w") as file_open:
            file_open.write(Template_html.render(Context_html))

        print("Report generated. View /tmp/vnftest.htm")
