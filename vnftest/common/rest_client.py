#!/usr/bin/env python
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

import json

import logging
import os
import urllib2
import requests
import sys
import traceback
from vnftest.common import utils

logger = logging.getLogger(__name__)
os.putenv('PYTHONHTTPSVERIFY', "0")


def post(url, headers, data, logger):
    return call(url, 'POST', headers, data, logger)


def call(url, method, headers, data, logger):
    data_json = json.dumps(data)
    f = None
    try:
        req = urllib2.Request(url, data=data_json, headers=headers)
        req.get_method = lambda: method
        f = urllib2.urlopen(req)
        return_code = f.code
        response_body = f.read()
        headers = f.headers.dict

        content_type = headers['content-type'] if 'content-type' in headers else 'application/json'
        f.close()
        if len(str(response_body)) == 0:
            response_body = "{}"
        if 'application/xml' in content_type:
            response_body = utils.xml_to_dict(response_body)
        else:
            response_body = json.loads(response_body)
        result = {'return_code': return_code, 'body': response_body, 'headers': headers}
        return result
    except urllib2.HTTPError as e:
        error_message = e.read()
        logger.exception(error_message)
        raise RuntimeError(error_message)
    except Exception as e:
        message = "Cannot read content from {}, exception: {}".format(url, e)
        logger.exception(message)
        raise RuntimeError(message)
    finally:
        if f is not None:
            f.close()


def upload_file(url, headers, file, logger):
    logger.debug("Upload file. URL: {}".format(url))
    response = None
    try:
        response = requests.post(url, headers=headers, files=file, verify=False)
        return {'return_code': response.status_code, 'body': response.json(), 'headers': response.headers}
    except Exception as e:
        message = "Error while uploading file to {}, exception: {}".format(url, e)
        logger.exception(message)
        raise RuntimeError(message)
    finally:
        if response is not None:
            response.close()
