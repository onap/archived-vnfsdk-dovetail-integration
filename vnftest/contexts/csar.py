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

import logging

from vnftest.contexts.base import Context

LOG = logging.getLogger(__name__)


class CSARContext(Context):
    """Class that handle sdc info"""

    __context_type__ = "CSAR"

    def __init__(self):
        super(CSARContext, self).__init__()

    def init(self, attrs):
        super(CSARContext, self).init(attrs)

    def deploy(self):
        """no need to deploy"""
        pass

    def undeploy(self):
        """no need to undeploy"""
        super(CSARContext, self).undeploy()
