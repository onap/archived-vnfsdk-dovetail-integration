#!/bin/bash
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
# yardstick/tools/cover.sh

if [[ -n $COVER_DIR_NAME ]]; then
    :
elif [[ -n $_ ]]; then
    COVER_DIR_NAME=$( dirname $_ )
else
    COVER_DIR_NAME=$( dirname $0 )
fi

run_coverage_test() {

    # enable debugging
    set -x

    coverage run -p -m unittest discover ./vnftest/tests/unit/core
    coverage run -p -m unittest discover ./vnftest/tests/unit/onap
    coverage run -p -m unittest discover ./vnftest/tests/unit/common
    coverage run -p -m unittest discover ./vnftest/tests/unit/context
    coverage combine
    coverage xml
    coverage erase

}
