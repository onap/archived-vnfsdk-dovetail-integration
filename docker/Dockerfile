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
# yardstick/docker/Dockerfile
FROM ubuntu:16.04

LABEL image=onap/vnftest

ARG BRANCH=master

# GIT repo directory
ENV REPOS_DIR="/home/onap/repos" \
    IMAGE_DIR="/home/onap/images/"

# Set work directory

# Vnftest repo
ENV VNFTEST_REPO_DIR="${REPOS_DIR}/vnftest" \
    RELENG_REPO_DIR="${REPOS_DIR}/releng" \
    STORPERF_REPO_DIR="${REPOS_DIR}/storperf"

RUN apt-get update && apt-get install -y git python-setuptools python-pip && apt-get -y autoremove && apt-get clean
RUN easy_install -U setuptools==30.0.0
RUN pip install appdirs==1.4.0 pyopenssl==17.5.0 python-openstackclient==3.11.0

RUN mkdir -p ${REPOS_DIR}

RUN git config --global http.sslVerify false
RUN git clone --depth 1 -b $BRANCH https://gerrit.onap.org/gerrit/vnftest ${VNFTEST_REPO_DIR}
RUN git clone --depth 1 https://gerrit.onap.org/gerrit/releng ${RELENG_REPO_DIR}
RUN git clone --depth 1 -b $BRANCH https://gerrit.onap.org/gerrit/storperf ${STORPERF_REPO_DIR}

WORKDIR ${VNFTEST_REPO_DIR}
RUN ${VNFTEST_REPO_DIR}/install.sh
RUN ${VNFTEST_REPO_DIR}/docker/supervisor.sh

RUN echo "daemon off;" >> /etc/nginx/nginx.conf

EXPOSE 5000

ADD http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img ${IMAGE_DIR}
ADD http://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img ${IMAGE_DIR}

COPY ./exec_tests.sh /usr/local/bin/

ENV NSB_DIR="/opt/nsb_bin" \
    PYTHONPATH="${PYTHONPATH}:${NSB_DIR}/trex_client:${NSB_DIR}/trex_client/stl"

WORKDIR ${REPOS_DIR}
CMD ["/usr/bin/supervisord"]
