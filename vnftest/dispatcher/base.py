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
# yardstick/dispatcher/base.py

from __future__ import absolute_import
import abc
import six

import vnftest.common.utils as utils


@six.add_metaclass(abc.ABCMeta)
class Base(object):

    def __init__(self, conf):
        self.conf = conf

    @staticmethod
    def get_cls(dispatcher_type):
        """Return class of specified type."""
        for dispatcher in utils.findsubclasses(Base):
            if dispatcher_type == dispatcher.__dispatcher_type__:
                return dispatcher
        raise RuntimeError("No such dispatcher_type %s" % dispatcher_type)

    @staticmethod
    def get(config):
        """Returns instance of a dispatcher for dispatcher type.
        """
        list_dispatcher = \
            [Base.get_cls(out_type.capitalize())(config)
             for out_type in config['DEFAULT']['dispatcher']]

        return list_dispatcher

    @abc.abstractmethod
    def flush_result_data(self, data):
        """Flush result data into permanent storage media interface."""
