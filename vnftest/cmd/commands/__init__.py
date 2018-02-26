from __future__ import absolute_import
from vnftest.onap.core import Param


def change_osloobj_to_paras(args):
    param = Param({})
    for k in vars(param):
        if hasattr(args, k):
            setattr(param, k, getattr(args, k))
    return param


class Commands(object):

    def _change_to_dict(self, args):
        p = Param({})
        return {k: getattr(args, k) for k in vars(p) if hasattr(args, k)}
