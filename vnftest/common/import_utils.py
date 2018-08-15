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
import importlib

import os
import sys
import vnftest


def import_modules_from_package(package):
    """Import modules given a package name
    :param: package - Full package name. For example: rally.deploy.engines
    """
    vnftest_root = os.path.dirname(os.path.dirname(vnftest.__file__))
    path = os.path.join(vnftest_root, *package.split('.'))
    for root, _, files in os.walk(path):
        matches = (filename for filename in files if filename.endswith('.py')
                   and not filename.startswith('__'))
        new_package = os.path.relpath(root, vnftest_root).replace(os.sep,
                                                                    '.')
        module_names = set(
            '{}.{}'.format(new_package, filename.rsplit('.py', 1)[0])
            for filename in matches)
        # Find modules which haven't already been imported
        missing_modules = module_names.difference(sys.modules)
        for module_name in missing_modules:
            importlib.import_module(module_name)
