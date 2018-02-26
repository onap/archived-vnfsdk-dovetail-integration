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
# yardstick/docker/uwsgi.sh

: ${VNFTEST_REPO_DIR:='/home/onap/repos/vnftest'}

# generate uwsgi config file
mkdir -p /etc/vnftest

# create api log directory
mkdir -p /var/log/vnftest

# create vnftest.sock for communicating
touch /var/run/vnftest.sock

uwsgi_config='/etc/vnftest/vnftest.ini'
if [[ ! -e "${uwsgi_config}" ]];then

    cat << EOF > "${uwsgi_config}"
[uwsgi]
master = true
debug = true
chdir = ${VNFTEST_REPO_DIR}/api
module = server
plugins = python
processes = 10
threads = 5
async = true
max-requests = 5000
chmod-socket = 666
callable = app_wrapper
enable-threads = true
close-on-exec = 1
daemonize= /var/log/vnftest/uwsgi.log
socket = /var/run/vnftest.sock
EOF
    if [[ "${VNFTEST_VENV}" ]];then
        echo "virtualenv = ${VNFTEST_VENV}" >> "${uwsgi_config}"
    fi
fi
