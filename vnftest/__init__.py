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
import os
import errno

# this module must only import other modules that do
# not require loggers to be created, so this cannot
# include vnftest.common.utils
from vnftest.common import constants

try:
    # do not use vnftest.common.utils.makedirs
    # since vnftest.common.utils creates a logger
    # and so it cannot be imported before this code
    os.makedirs(constants.LOG_DIR)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

LOG_FILE = os.path.join(constants.LOG_DIR, 'vnftest.log')
LOG_FORMATTER = '%(asctime)s [%(levelname)s] %(name)s %(filename)s:%(lineno)d %(message)s'

_LOG_FORMATTER = logging.Formatter(LOG_FORMATTER)
_LOG_STREAM_HDLR = logging.StreamHandler()
_LOG_FILE_HDLR = logging.FileHandler(LOG_FILE)

LOG = logging.getLogger(__name__)


def _init_logging():

    LOG.setLevel(logging.DEBUG)

    _LOG_STREAM_HDLR.setFormatter(_LOG_FORMATTER)
    if os.environ.get('CI_DEBUG', '').lower() in {'1', 'y', "yes", "true"}:
        _LOG_STREAM_HDLR.setLevel(logging.DEBUG)
    else:
        _LOG_STREAM_HDLR.setLevel(logging.INFO)

    # don't append to log file, clobber
    _LOG_FILE_HDLR.setFormatter(_LOG_FORMATTER)
    _LOG_FILE_HDLR.setLevel(logging.DEBUG)

    del logging.root.handlers[:]
    logging.root.addHandler(_LOG_STREAM_HDLR)
    logging.root.addHandler(_LOG_FILE_HDLR)
    logging.debug("logging.root.handlers = %s", logging.root.handlers)
