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
# yardstick/docker/Makefile

SHELL = /bin/bash

IMAGE = onap/vnftest

DOCKER_TAG = brahmaputra.0

.PHONY: all
all: .docker

.docker:
	/usr/bin/docker build --rm=true --no-cache=true -t $(IMAGE):$(DOCKER_TAG) vnftest-ci
	/usr/bin/docker tag -f $(IMAGE):$(DOCKER_TAG) $(IMAGE):latest
	touch .docker


.PHONY:	clean
clean:
	@docker ps | grep $(IMAGE) | awk '{print $$1}' | xargs -r docker stop
	@docker ps -a | grep $(IMAGE) | awk '{print $$1}' | xargs -r docker rm
	@echo "Docker images to remove:"
	@docker images | head -1 && docker images | grep $(IMAGE) || true
	@image_tags=($$(docker images | grep $(IMAGE) | awk '{print $$2}')) ; \
	for tag in "$${image_tags[@]}"; do \
	   echo "Removing docker image $(IMAGE):$$tag..." ; \
	   docker rmi $(IMAGE):$$tag ; \
	done
	rm -f .docker
