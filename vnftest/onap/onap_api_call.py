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
from __future__ import absolute_import

import copy
import logging
import time

import os
import yaml

from vnftest.common import constants as consts
from vnftest.common import rest_client
from vnftest.common.utils import dotdict
from vnftest.common.exceptions import MandatoryKeyException, InputParameterMissing
from vnftest.crawlers.base import Crawler
from vnftest.onap.common.vf_module_crawler import VfModuleCrawler
from vnftest.steps import base
import jinja2
import jinja2.meta

LOG = logging.getLogger(__name__)


class OnapApiCall(base.Step):
    """Call ONAP API
    """
    __step_type__ = "OnapApiCall"

    def __init__(self, step_cfg, context, input_params):
        self.step_cfg = step_cfg
        self.context = context
        self.input_params = input_params
        self.input_cfg = None
        self.output_cfg = None
        self.rest_def_file = None
        self.delay = None
        self.setup_done = False
        self.curr_path = os.path.dirname(os.path.abspath(__file__))

    def setup(self):
        options = self.step_cfg['options']
        self.rest_def_file = options.get("file")
        self.delay = options.get("delay", 0)
        self.input_cfg = options.get("input", {})
        self.output_cfg = options.get("output", {})
        self.sla_cfg = self.step_cfg.get('sla', {'retries': 0})
        context_dict = {}
        context_dict['creds'] = dotdict(self.context.creds)
        context_dict['vnf_descriptor'] = dotdict(self.context.vnf_descriptor)
        self.input_params['context'] = dotdict(context_dict)
        self.setup_done = True

    def eval_input(self, params):
        for input_parameter in self.input_cfg:
            param_name = input_parameter['parameter_name']
            value = None
            if 'value' in input_parameter:
                value_def = input_parameter['value']
                value = self.format_string(value_def, self.input_params)
            if value is None or value == "":
                raise InputParameterMissing(param_name=param_name, source="task configuration")
            params[param_name] = value

    def run(self, result, attempt=0):
        LOG.info("** Handling: " + str(self.rest_def_file))
        output = self.run_impl(result)
        try:
            self.handle_sla(output)
        except AssertionError as e:
            LOG.info(str(e))
            if attempt < self.sla_cfg['retries']:
                time.sleep(self.sla_cfg['interval'])
                LOG.info("retry operation")
                attempt = attempt + 1
                return self.run(result, attempt)
            else:
                raise e
        return output

    def run_impl(self, result):
        if not self.setup_done:
            self.setup()
        output = {}
        params = copy.deepcopy(consts.component_constants)
        self.eval_input(params)
        execution_result = self.execute_operation(params)
        result_body = execution_result['body']
        for output_parameter in self.output_cfg:
            param_name = output_parameter['parameter_name']
            param_value = output_parameter.get('value', "[]")
            if param_value.find("[") > -1:
                crawler_type = output_parameter.get('type', 'default')
                crawler_class = Crawler.get_cls(crawler_type)
                crawler = crawler_class()
                param_value = crawler.crawl(result_body, param_value)
            if param_value is None:
                raise MandatoryKeyException(key_name='param_path', class_name=str(result_body))
            result[param_name] = param_value
            output[param_name] = param_value
        return output

    def execute_operation(self, params, attempt=0):
        if self.delay > 0:
            time.sleep(self.delay)
        try:
            return self.execute_operation_impl(params)
        except Exception as e:
            LOG.info(str(e))
            if attempt < 3:
                time.sleep(15)
                LOG.info("############# retry operation ##########")
                attempt = attempt + 1
                return self.execute_operation(params, attempt)
            else:
                raise e

    def execute_operation_impl(self, params):
        operation = self.load_file(params)
        url = operation['url']
        headers = operation['headers']
        body = {}
        if 'body' in operation:
            body = operation['body']
        LOG.info(url)
        LOG.info(headers)
        LOG.info(body)
        if 'file' in operation:
            file_path = operation['file']
            LOG.info(file_path)
            files = {'upload': open(file_path)}
            result = rest_client.upload_file(url, headers, files, LOG)
        else:
            result = rest_client.call(url,
                                      operation['method'],
                                      headers,
                                      body,
                                      LOG)
        if result['return_code'] >= 300:
            raise RuntimeError(
                "Operation failed. return_code:{}, message:{}".format(result['return_code'], result['body']))
        LOG.info("Results: " + str(result))
        return result

    @staticmethod
    def format_string(st, params):
        if not isinstance(st, basestring):
            return st
        try:
            return st.format(**params)
        except Exception as e:
            s = str(e)
            s = s.replace("'", "")
            LOG.info(s)
            params[s] = ""
            LOG.info("param" + params[s])
            return st.format(**params)

    def handle_sla(self, output):
        if self.sla_cfg.get('action', "") == 'assert' and 'equals' in self.sla_cfg:
            value_def = self.sla_cfg['value']
            value = self.format_string(value_def, output)
            expected_value = self.sla_cfg['equals']
            assert value == expected_value

    def load_file(self, params):
        yaml_path = os.path.join(self.curr_path, self.rest_def_file)
        with open(yaml_path) as f:
            operation_template = f.read()
            operation = jinja2.Template(operation_template).render(**params)
            return yaml.load(operation)
