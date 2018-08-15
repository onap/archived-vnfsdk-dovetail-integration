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
# yardstick/install.sh

# fit for arm64
DOCKER_ARCH="$(uname -m)"

UBUNTU_PORTS_URL="http://ports.ubuntu.com/ubuntu-ports/"
UBUNTU_ARCHIVE_URL="http://archive.ubuntu.com/ubuntu/"

source /etc/os-release
source_file=/etc/apt/sources.list

if [[ "${DOCKER_ARCH}" == "aarch64" ]]; then
    sed -i -e 's/^deb \([^/[]\)/deb [arch=arm64] \1/g' "${source_file}"
    DOCKER_ARCH="arm64"
    DOCKER_REPO="${UBUNTU_PORTS_URL}"
    EXTRA_ARCH="amd64"
    EXTRA_REPO="${UBUNTU_ARCHIVE_URL}"
    dpkg --add-architecture amd64
else
    sed -i -e 's/^deb \([^/[]\)/deb [arch=amd64] \1/g' "${source_file}"
    DOCKER_ARCH="amd64"
    DOCKER_REPO="${UBUNTU_ARCHIVE_URL}"
    EXTRA_ARCH="arm64"
    EXTRA_REPO="${UBUNTU_PORTS_URL}"
    dpkg --add-architecture arm64
fi

sed -i -e 's/^deb-src /# deb-src /g' "${source_file}"

VERSION_CODENAME=${VERSION_CODENAME:-trusty}

echo "APT::Default-Release \""${VERSION_CODENAME}"\";" > /etc/apt/apt.conf.d/default-distro

sub_source_file=/etc/apt/sources.list.d/vnftest.list
touch "${sub_source_file}"

# first add xenial repo needed for installing qemu_static_user/xenial in the container
# then add complementary architecture repositories in case the cloud image is of different arch
if [[ "${VERSION_CODENAME}" != "xenial" ]]; then
    REPO_UPDATE="deb [arch="${DOCKER_ARCH}"] "${DOCKER_REPO}" xenial-updates universe"
fi

echo -e ""${REPO_UPDATE}"
deb [arch="${EXTRA_ARCH}"] "${EXTRA_REPO}" "${VERSION_CODENAME}" main universe multiverse restricted
deb [arch="${EXTRA_ARCH}"] "${EXTRA_REPO}" "${VERSION_CODENAME}"-updates main universe multiverse restricted
deb [arch="${EXTRA_ARCH}"] "${EXTRA_REPO}" "${VERSION_CODENAME}"-security main universe multiverse restricted
deb [arch="${EXTRA_ARCH}"] "${EXTRA_REPO}" "${VERSION_CODENAME}"-proposed main universe multiverse restricted" > "${sub_source_file}"

echo "vm.mmap_min_addr = 0" > /etc/sysctl.d/mmap_min_addr.conf

# install tools
apt-get update && apt-get install -y \
    qemu-user-static/xenial \
    bonnie++ \
    wget \
    expect \
    curl \
    git \
    sshpass \
    qemu-utils \
    kpartx \
    libffi-dev \
    libssl-dev \
    libzmq-dev \
    python \
    python-dev \
    libxml2-dev \
    libxslt1-dev \
    supervisor \
    python-pip \
    vim \
    libxft-dev \
    libxss-dev \
    sudo \
    iputils-ping

if [[ "${DOCKER_ARCH}" != "aarch64" ]]; then
    apt-get install -y libc6:arm64
fi

apt-get -y autoremove && apt-get clean

git config --global http.sslVerify false

mkdir -p /etc/vnftest
cp "${PWD}/etc/vnftest/vnftest.yaml" /etc/vnftest
# install vnftest + dependencies
easy_install -U pip
pip install -r requirements.txt
pip install .
