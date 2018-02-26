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
# vnftest comment: this is a modified copy of
# yardstick/tests/main.py
""" vnftest - command line tool for managing benchmarks

    Example invocation:
    $ vnftest task start samples/ping.yaml

    Servers are the same as VMs (Nova calls them servers in the API)

    Many tests use a client/server architecture. A test client is configured
    to use a specific test server e.g. using an IP address. This is true for
    example iperf. In some cases the test server is included in the kernel
    (ping, pktgen) and no additional software is needed on the server. In other
    cases (iperf) a server process needs to be installed and started.

    One server is required to host the test client program (such as ping or
    iperf). In the task file this server is called host.

    A server can be the _target_ of a test client (think ping destination
    argument). A target server is optional but needed in most test steps.
    In the task file this server is called target. This is probably the same
    as DUT in existing terminology.

    Existing terminology:
    https://www.ietf.org/rfc/rfc1242.txt (throughput/latency)
    https://www.ietf.org/rfc/rfc2285.txt (DUT/SUT)

    New terminology:
    NFV TST

"""
from __future__ import absolute_import
import sys

from vnftest.cmd.cli import VnftestCLI


def main():
    """vnftest main"""
    VnftestCLI().main(sys.argv[1:])

if __name__ == '__main__':
    main()
