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

LABEL image=onap/vnfsdk/vnftest

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

#For developers: To test your changes you must comment out the git clone for ${VNFTEST_REPO_DIR}.
#You must also uncomment the RUN and COPY commands below.
#You must run docker build from your vnftest directory on the host.
RUN git clone --depth 1 -b $BRANCH https://gerrit.onap.org/r/vnfsdk/dovetail-integration ${VNFTEST_REPO_DIR}
#RUN mkdir ${VNFTEST_REPO_DIR}
#COPY ./ ${VNFTEST_REPO_DIR}
WORKDIR ${VNFTEST_REPO_DIR}

RUN ${VNFTEST_REPO_DIR}/install.sh
COPY ./exec_tests.sh /usr/local/bin/
ENV VNFTEST_ROOT_PATH="/"
ADD startup.sh /startup.sh
RUN chmod 755 /startup.sh
ENTRYPOINT /startup.sh
