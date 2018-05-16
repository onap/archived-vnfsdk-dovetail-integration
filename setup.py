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
# yardstick/setup.py
from __future__ import absolute_import
from setuptools import setup, find_packages


setup(
    name="vnftest",
    version="1.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'vnftest': [
            'onap/onboard/*.yaml',
            'onap/lifecycle/*.yaml'
        ],
        'etc': [
            'vnftest/*.yaml',
            'vnftest/*.conf',
            'vnftest/vnf_descriptors/*.yaml'
        ],
        'tests': [
            'onap/*/*.yaml'
        ]
    },
    url="https://www.onap.org",
    entry_points={
        'console_scripts': [
            'vnftest=vnftest.main:main'
        ],
    },
    scripts=[
        'tools/vnftest-img-modify',
        'tools/vnftest-img-lxd-modify',
        'tools/vnftest-img-dpdk-modify'
    ]
)
