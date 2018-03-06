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

import logging
import time
import os
import yaml
import copy

from vnftest.common.exceptions import MandatoryKeyException
from vnftest.onap.steps import base
from vnftest.common import rest_client
from vnftest.common import constants as consts

LOG = logging.getLogger(__name__)


class OnapApiCall(base.Step):

    __step_type__ = "OnapApiCall"

    def __init__(self, step_cfg, context_cfg):
        self.step_cfg = step_cfg
        self.context_cfg = context_cfg
        self.input = None
        self.output = None
        self.rest_def_file = None
        self.setup_done = False
        self.curr_path = os.path.dirname(os.path.abspath(__file__))

    def setup(self):
        options = self.step_cfg['options']
        self.rest_def_file = options.get("file")
        self.input = options.get("input")
        self.output = options.get("output")
        self.setup_done = True

    def run(self, result):
        if not self.setup_done:
            self.setup()
        result['output'] = {}
        params = copy.deepcopy(consts.component_constants)
        for input_parameter in self.input:
            param_name = input_parameter['parameter_name']
            param_value = input_parameter['value']
            params[param_name] = param_value
        execution_result = self.execute_operation(params)
        result_body = execution_result['body']
        for output_parameter in self.output:
            param_name = output_parameter['parameter_name']
            param_path = output_parameter['path']
            path_list = param_path.split("|")
            param_value = result_body
            for path_element in path_list:
                param_value = param_value[path_element]
            if param_value is None:
                raise MandatoryKeyException(
                    key_name='param_path', class_name=str(result_body))
            self.context_cfg[param_name] = param_value
            result['output'][param_name] = param_value
        result['status'] = 'PASS'

    def execute_operation(self, params, attempt=0):
        try:
            return self.execute_operation_impl(params)
        except Exception as e:
            LOG.info(str(e))
            if attempt < 2:
                time.sleep(15)
                LOG.info("############# retry operation ##########")
                attempt = attempt + 1
                return self.execute_operation(params, attempt)
            else:
                raise e

    def execute_operation_impl(self, params):
        input_yaml = self.rest_def_file
        LOG.info("########## processing " + input_yaml + "##########")
        yaml_path = os.path.join(self.curr_path, input_yaml)
        with open(yaml_path) as info:
            operation = yaml.load(info)
        operation = self.format(operation, params)
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

    def format(self, d, params):
        ret = None
        if isinstance(d, dict):
            ret = {}
            for k, v in d.iteritems():
                if isinstance(v, basestring):
                    v = self.format_string(v, params)
                else:
                    v = self.format(v, params)
                ret[k] = v
        if isinstance(d, list):
            ret = []
            for v in d:
                if isinstance(v, basestring):
                    v = self.format_string(v, params)
                else:
                    v = self.format(v, params)
                ret.append(v)
        if isinstance(d, basestring):
            ret = self.format_string(d, params)
        return ret

    def format_string(self, st, params):
        try:
            return st.format(**params)
        except Exception as e:
            s = str(e)
            s = s.replace("'", "")
            LOG.info(s)
            params[s] = ""
            LOG.info("param" + params[s])
            return st.format(**params)


