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
# yardstick/common/constants.py
from __future__ import absolute_import
import os
import errno

from functools import reduce

import pkg_resources

# this module must only import other modules that do
# not require loggers to be created, so this cannot
# include vnftest.common.utils
from vnftest.common.yaml_loader import yaml_load

dirname = os.path.dirname
abspath = os.path.abspath
join = os.path.join
sep = os.path.sep

CONF = {}
CONF_FILE = None
VNFTEST_ROOT_PATH = dirname(
    dirname(abspath(pkg_resources.resource_filename(__name__, "")))) + sep


def get_param(key, default=''):
    # don't re-parse yaml for each lookup
    if not CONF:
        # we have to defer this to runtime so that we can mock os.environ.get in unittests
        default_path = os.path.join(VNFTEST_ROOT_PATH, "etc/vnftest/vnftest.yaml")
        conf_file = os.environ.get('CONF_FILE', default_path)

        # do not use vnftest.common.utils.parse_yaml
        # since vnftest.common.utils creates a logger
        # and so it cannot be imported before this code
        try:
            with open(conf_file) as f:
                value = yaml_load(f)
        except IOError:
            pass
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        else:
            CONF.update(value)
    try:
        return reduce(lambda a, b: a[b], key.split('.'), CONF)
    except KeyError:
        if not default:
            raise
        return default


try:
    SERVER_IP = get_param('api.server_ip')
except KeyError:
    try:
        from pyroute2 import IPDB
    except ImportError:
        SERVER_IP = '172.17.0.1'
    else:
        with IPDB() as ip:
            try:
                SERVER_IP = ip.routes['default'].gateway
            except KeyError:
                # during unittests ip.routes['default'] can be invalid
                SERVER_IP = '127.0.0.1'

if not SERVER_IP:
    SERVER_IP = '127.0.0.1'


# dir
CONF_DIR = get_param('dir.conf', join(VNFTEST_ROOT_PATH, 'etc/vnftest'))
CONF_FILE = join(CONF_DIR, 'vnftest.conf')
REPOS_DIR = get_param('dir.repos', join(VNFTEST_ROOT_PATH, 'home/onap/repos/vnftest'))
LOG_DIR = get_param('dir.log', join(VNFTEST_ROOT_PATH, 'tmp/vnftest/'))

TASK_LOG_DIR = get_param('dir.tasklog', join(VNFTEST_ROOT_PATH, 'var/log/vnftest/'))
CONF_SAMPLE_DIR = join(REPOS_DIR, 'etc/vnftest/')
SAMPLE_CASE_DIR = join(REPOS_DIR, 'samples')
TESTCASE_DIR = join(VNFTEST_ROOT_PATH, 'tests/onap/test_cases/')
TESTSUITE_DIR = join(VNFTEST_ROOT_PATH, 'tests/onap/test_suites/')

# file
DEFAULT_OUTPUT_FILE = get_param('file.output_file', join(VNFTEST_ROOT_PATH, 'tmp/vnftest.out'))
DEFAULT_HTML_FILE = get_param('file.html_file', join(VNFTEST_ROOT_PATH, 'tmp/vnftest.htm'))
REPORTING_FILE = get_param('file.reporting_file', join(VNFTEST_ROOT_PATH, 'tmp/report.html'))

# components
AAI_IP = get_param('component.aai_ip')
AAI_PORT = get_param('component.aai_port')
AAI_SSL_PORT = get_param('component.aai_ssl_port')
MSO_IP = get_param('component.mso_ip')
SDC_IP = get_param('component.sdc_ip')
SDC_PORT = get_param('component.sdc_port')
SDC_CATALOG_PORT = get_param('component.sdc_catalog_port')
SDC_DESIGNER_USER = get_param('component.sdc_designer_user')
SDC_TESTER_USER = get_param('component.sdc_tester_user')
SDC_GOVERNANCE_USER = get_param('component.sdc_governance_user')
SDC_OPERATIONS_USER = get_param('component.sdc_operations_user')

component_constants = {}
component_constants['aai_ip'] = AAI_IP
component_constants['aai_port'] = AAI_PORT
component_constants['aai_ssl_port'] = AAI_SSL_PORT
component_constants['mso_ip'] = MSO_IP
component_constants['sdc_ip'] = SDC_IP
component_constants['sdc_port'] = SDC_PORT
component_constants['sdc_catalog_port'] = SDC_CATALOG_PORT
component_constants['sdc_designer_user'] = SDC_DESIGNER_USER
component_constants['sdc_tester_user'] = SDC_TESTER_USER
component_constants['sdc_governance_user'] = SDC_GOVERNANCE_USER
component_constants['sdc_operations_user'] = SDC_OPERATIONS_USER


# api
API_PORT = 5000
DOCKER_URL = 'unix://var/run/docker.sock'
SQLITE = 'sqlite:////tmp/vnftest.db'

API_SUCCESS = 1
API_ERROR = 2
TASK_NOT_DONE = 0
TASK_DONE = 1
TASK_FAILED = 2

BASE_URL = 'http://localhost:5000'
ENV_ACTION_API = BASE_URL + '/vnftest/env/action'
ASYNC_TASK_API = BASE_URL + '/vnftest/asynctask'

# general
TESTCASE_PRE = 'onap_vnftest_'
TESTSUITE_PRE = 'onap_'
