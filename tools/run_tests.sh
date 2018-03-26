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
# yardstick/tools/run_tests.sh

# Run vnftest's unit, coverage, functional test

getopts ":f" FILE_OPTION
opts=$@ # get other args

# don't write .pyc files this can cause odd unittest results
export PYTHONDONTWRITEBYTECODE=1

PY_VER="py$( python --version | sed 's/[^[:digit:]]//g' | cut -c-2 )"
export PY_VER

COVER_DIR_NAME="./tools/"
export COVER_DIR_NAME

run_tests() {
    echo "Get external libs needed for unit test"

    echo "Running unittest ... "
    if [ $FILE_OPTION == "f" ]; then
        python -m unittest discover -v -s vnftest/tests/unit > $logfile 2>&1
    else
        python -m unittest discover -v -s vnftest/tests/unit
    fi

    if [ $? -ne 0 ]; then
        if [ $FILE_OPTION == "f" ]; then
            echo "FAILED, results in $logfile"
        fi
        exit 1
    else
        if [ $FILE_OPTION == "f" ]; then
            echo "OK, results in $logfile"
        fi
    fi
}

run_coverage() {
    source $COVER_DIR_NAME/cover.sh
    run_coverage_test
}

run_functional_test() {

    mkdir -p .testrepository
    python -m subunit.run discover vnftest/tests/functional > .testrepository/subunit.log

    subunit2pyunit < .testrepository/subunit.log
    EXIT_CODE=$?
    subunit-stats < .testrepository/subunit.log

    if [ $EXIT_CODE -ne 0 ]; then
        exit 1
    else
        echo "OK"
    fi
}

if [[ $opts =~ "--unit" ]]; then
    run_tests
fi

if [[ $opts =~ "--coverage" ]]; then
    run_coverage
fi

if [[ $opts =~ "--functional" ]]; then
    run_functional_test
fi

if [[ -z $opts ]]; then
    echo "No tests to run!!"
    echo "Usage: run_tests.sh [--unit] [--coverage] [--functional]"
    exit 1
fi
