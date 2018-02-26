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
# yardstick/tools/vnftest-img-dpmdk-finalize.sh

# installs dpdk and pktgen packages on modified image

# PREREQUISITES
# modified image (vnftest-wily-server) must be uploaded to OpenStack
# heat must be installed: apt-get install python-heatclient, python-glanceclient, python-nova
# must have a public vnftest-key uploaded in openstack
# must have a proper flavor for the image (i.e. m1.small)


stackname="vnftest-modify-stack"
template=dpdk_install.yml
new_image_name="vnftest-image-pktgen-ready"

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

# workaround: Without wait time, the file size of pktgen is zero in the snapshot.
sleep 60

status=$(nova image-create --poll $stackname $new_image_name)
if [[ "$status" =~ "Finished" ]];then
  echo "$new_image_name finished"
fi

nova delete $stackname
sleep 10
openstack stack delete --yes $stackname
