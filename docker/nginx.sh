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
# yardstick/docker/nginx.sh

# nginx config
nginx_config='/etc/nginx/conf.d/vnftest.conf'

if [[ ! -e "${nginx_config}" ]];then

    cat << EOF > "${nginx_config}"
server {
    listen 5000;
    server_name localhost;
    index  index.htm index.html;
    location / {
        include uwsgi_params;
        client_max_body_size    2000m;
        uwsgi_pass unix:///var/run/vnftest.sock;
    }

    location /gui/ {
        alias /etc/nginx/vnftest/gui/;
    }

    location /report/ {
        alias /tmp/;
    }
}
EOF
fi
