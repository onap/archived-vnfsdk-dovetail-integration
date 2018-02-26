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
# yardstick/docker/exec_tests.sh
set -e

: ${VNFTEST_REPO:='https://gerrit.onap.org/gerrit/vnftest'}
: ${VNFTEST_REPO_DIR:='/home/onap/repos/vnftest'}
: ${VNFTEST_BRANCH:='master'} # branch, tag, sha1 or refspec

# git update using reference as a branch.
# git_update_branch ref
function git_update_branch {
    local git_branch=$1

    git checkout -f origin/${git_branch}
    # a local branch might not exist
    git branch -D ${git_branch} || true
    git checkout -b ${git_branch}
}

# git update using reference as a branch.
# git_update_remote_branch ref
function git_update_remote_branch {
    local git_branch=$1

    git checkout -b ${git_branch} -t origin/${git_branch}
}

# git update using reference as a tag. Be careful editing source at that repo
# as working copy will be in a detached mode
# git_update_tag ref
function git_update_tag {
    local git_tag=$1

    git tag -d ${git_tag}
    # fetching given tag only
    git fetch origin tag ${git_tag}
    git checkout -f ${git_tag}
}


# OpenStack Functions

git_checkout()
{
    local git_ref=$1
    if [[ -n "$(git show-ref refs/tags/${git_ref})" ]]; then
        git_update_tag "${git_ref}"
    elif [[ -n "$(git show-ref refs/heads/${git_ref})" ]]; then
        git_update_branch "${git_ref}"
    elif [[ -n "$(git show-ref refs/remotes/origin/${git_ref})" ]]; then
        git_update_remote_branch "${git_ref}"
    # check to see if it is a remote ref
    elif git fetch --tags origin "${git_ref}"; then
        # refspec / changeset
        git checkout FETCH_HEAD
    else
        # if we are a random commit id we have to unshallow
        # to get all the commits
        git fetch --unshallow origin
        git checkout -f "${git_ref}"
    fi
}

# releng is not needed, we bind-mount the credentials

echo
echo "INFO: Updating vnftest -> ${VNFTEST_BRANCH}"
if [ ! -d ${VNFTEST_REPO_DIR} ]; then
    git clone ${VNFTEST_REPO} ${VNFTEST_REPO_DIR}
fi
cd ${VNFTEST_REPO_DIR}
git_checkout ${VNFTEST_BRANCH}

if [[ "${DEPLOY_STEP:0:2}" == "os" ]];then
    # setup the environment
    source ${VNFTEST_REPO_DIR}/tests/ci/prepare_env.sh
fi

# execute tests
${VNFTEST_REPO_DIR}/tests/ci/vnftest-verify $@
