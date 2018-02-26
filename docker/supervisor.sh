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
# yardstick/docker/supervisor.sh

# nginx service start when boot
supervisor_config='/etc/supervisor/conf.d/vnftest.conf'

if [[ ! -e "${supervisor_config}" ]];then
    cat << EOF > "${supervisor_config}"
[supervisord]
nodaemon = true

[program:nginx]
command = service nginx restart

[program:vnftest_uwsgi]
directory = /etc/vnftest
command = uwsgi -i vnftest.ini
EOF
fi
