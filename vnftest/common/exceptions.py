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
# yardstick/common/exceptions.py


class ProcessExecutionError(RuntimeError):
    def __init__(self, message, returncode):
        super(ProcessExecutionError, self).__init__(message)
        self.returncode = returncode


class VnftestException(Exception):
    message_tmplate = "An unknown exception occurred."

    def __init__(self, **kwargs):
        self.msg = self.message_tmplate.format(**kwargs)
        super(VnftestException, self).__init__()

    def __str__(self):
        return self.msg


class FunctionNotImplemented(VnftestException):
    message_tmplate = ('The function "{function_name}" is not implemented in '
               '"{class_name}" class.')


class MandatoryKeyException(VnftestException):
    message_tmplate = 'No value found for key "{key_name}" in "{dict_str}"'


class InputParameterMissing(VnftestException):
    message_tmplate = 'No value found for parameter "{param_name}" in "{source}"'


class ResourceNotFound(VnftestException):
    message_tmplate = 'Resource not found "{resource}"'
