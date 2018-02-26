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
# yardstick/dispatcher/__init__.py

from __future__ import absolute_import
from oslo_config import cfg

import vnftest.common.utils as utils

utils.import_modules_from_package("vnftest.dispatcher")

CONF = cfg.CONF
OPTS = [
    cfg.StrOpt('dispatcher',
               default='file',
               help='Dispatcher to store data.'),
]
CONF.register_opts(OPTS)
