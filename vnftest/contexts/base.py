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
import abc
import six

import vnftest.common.utils as utils
import logging

from vnftest.common import constants

LOG = logging.getLogger(__name__)


class Flags(object):
    """Class to represent the status of the flags in a context"""

    _FLAGS = {'no_setup': False,
              'no_teardown': False,
              'os_cloud_config': constants.OS_CLOUD_DEFAULT_CONFIG}

    def __init__(self, **kwargs):
        for name, value in self._FLAGS.items():
            setattr(self, name, value)

        for name, value in ((name, value) for (name, value) in kwargs.items()
                            if name in self._FLAGS):
            setattr(self, name, value)

    def parse(self, **kwargs):
        """Read in values matching the flags stored in this object"""
        if not kwargs:
            return

        for name, value in ((name, value) for (name, value) in kwargs.items()
                            if name in self._FLAGS):
            setattr(self, name, value)


@six.add_metaclass(abc.ABCMeta)
class Context(object):
    """Class that represents a context in the logical model"""
    _list = []

    def __init__(self):
        Context._list.append(self)
        self._flags = Flags()
        self._task_id = None
        self._name = None
        self._name_task_id = None

    def init(self, attrs):
        self._task_id = attrs['task_id']
        self._name = attrs['name']
        self._flags.parse(**attrs.get('flags', {}))
        self._name_task_id = '{}-{}'.format(
            self._name, self._task_id[:8])

    @property
    def name(self):
        if self._flags.no_setup or self._flags.no_teardown:
            return self._name
        else:
            return self._name_task_id

    @property
    def assigned_name(self):
        return self._name

    @staticmethod
    def get_cls(context_type):
        """Return class of specified type."""
        for context in utils.findsubclasses(Context):
            if context_type == context.__context_type__:
                return context
        raise RuntimeError("No such context_type %s" % context_type)

    @staticmethod
    def get(context_type):
        """Returns instance of a context for context type.
        """
        return Context.get_cls(context_type)()

    def _delete_context(self):
        Context._list.remove(self)

    @abc.abstractmethod
    def deploy(self):
        """Deploy context."""

    @abc.abstractmethod
    def undeploy(self):
        """Undeploy context."""
        self._delete_context()
