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
# rally/rally/benchmark/steps/base.py

""" Step base class
"""

from __future__ import absolute_import
import vnftest.common.utils as utils


class Step(object):

    def setup(self):
        """ default impl for step setup """
        pass

    def run(self, args):
        """ catcher for not implemented run methods in subclasses """
        raise RuntimeError("run method not implemented")

    def teardown(self):
        """ default impl for step teardown """
        pass

    @staticmethod
    def get_types():
        """return a list of known runner type (class) names"""
        steps = []
        for step in utils.itersubclasses(Step):
            steps.append(step)
        return steps

    @staticmethod
    def get_cls(step_type):
        """return class of specified type"""
        for step in utils.itersubclasses(Step):
            if step_type == step.__step_type__:
                return step

        raise RuntimeError("No such step type %s" % step_type)

    @staticmethod
    def get(step_type):
        """Returns instance of a step runner for execution type.
        """
        for step in utils.itersubclasses(Step):
            if step_type == step.__step_type__:
                return step.__module__ + "." + step.__name__

        raise RuntimeError("No such step type %s" % step_type)

    @classmethod
    def get_step_type(cls):
        """Return a string with the step type, if defined"""
        return str(getattr(cls, '__step_type__', None))

    @classmethod
    def get_description(cls):
        """Return a single line string with the class description

        This function will retrieve the class docstring and return the first
        line, or 'None' if it's empty.
        """
        return cls.__doc__.splitlines()[0] if cls.__doc__ else str(None)

    def _push_to_outputs(self, keys, values):
        return dict(zip(keys, values))

    def _change_obj_to_dict(self, obj):
        dic = {}
        for k, v in vars(obj).items():
            try:
                vars(v)
            except TypeError:
                dic[k] = v
        return dic
