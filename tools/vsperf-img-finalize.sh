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
# yardstick/tools/vsperf-img-finalize

# PREREQUISITES
# modified image (vnftest-vsperf) must be uploaded to OpenStack
# must have a proper flavor (vsperf-flavor) for the image e.g.
# nova flavor-create vsperf-flavor auto 8192 80 6
# nova flavor-key vsperf-flavor set hw:numa_nodes=1
# nova flavor-key vsperf-flavor set hw:mem_page_size=1GB
# nova flavor-key vsperf-flavor set hw:cpu_policy=dedicated
# nova flavor-key vsperf-flavor set hw:vif_multiqueue_enabled=true

stackname="vsperf-install-stack"
template=vsperf_install.yml
new_image_name="vnftest-vsperf-server"

openstack stack create $stackname -f yaml -t $template
progress="WARMING_UP"

while [ "$progress" != "CREATE_COMPLETE" ]
do
  sleep 10
  echo "check stack status......."
  show_output=$(openstack stack show $stackname)
  progress=$(echo $show_output | sed 's/^.*stack_status . \([^ ]*\).*$/\1/')
  echo "$progress"
  if [ "$progress" == "CREATE_FAILED" ];then
    echo "create $stackname failed"
    exit 1
  fi
done

# has to stop the instance before taking the snapshot
nova stop $stackname
sleep 10

status=$(nova image-create --poll $stackname $new_image_name)
if [[ "$status" =~ "Finished" ]];then
  echo "$new_image_name finished"
fi

nova delete $stackname
sleep 10
openstack stack delete --yes $stackname
