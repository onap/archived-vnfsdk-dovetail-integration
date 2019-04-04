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
# yardstick/common/utils.py

import collections
from contextlib import closing
import datetime
import errno
from string import Formatter

import ipaddress
import logging
import os
import random
import socket
import subprocess

import pkg_resources
import six
from flask import jsonify
from six.moves import configparser
from oslo_serialization import jsonutils
import xml.etree.ElementTree

from vnftest.common.exceptions import ResourceNotFound

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class_implementations = {}


# Decorator for cli-args
def cliargs(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def findsubclasses(cls):
    if cls.__name__ not in class_implementations:
        # Load entrypoint classes just once.
        if len(class_implementations) == 0:
            for entrypoint in pkg_resources.iter_entry_points(group='vnftest.extension'):
                loaded_type = entrypoint.load()
                logger.info("Loaded: " + str(loaded_type))

        subclasses = []
        class_implementations[cls.__name__] = subclasses

        def getallnativesubclasses(clazz):
            for subclass in clazz.__subclasses__():
                subclasses.append(subclass)
                getallnativesubclasses(subclass)

        getallnativesubclasses(cls)
    return class_implementations[cls.__name__]


def makedirs(d):
    try:
        os.makedirs(d)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def remove_file(path):
    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def execute_command(cmd):
    exec_msg = "Executing command: '%s'" % cmd
    logger.debug(exec_msg)

    output = subprocess.check_output(cmd.split()).split(os.linesep)

    return output


def source_env(env_file):
    p = subprocess.Popen(". %s; env" % env_file, stdout=subprocess.PIPE,
                         shell=True)
    output = p.communicate()[0]
    env = dict(line.split('=', 1) for line in output.splitlines() if '=' in line)
    os.environ.update(env)
    return env


def read_json_from_file(path):
    with open(path, 'r') as f:
        j = f.read()
    # don't use jsonutils.load() it conflicts with already decoded input
    return jsonutils.loads(j)


def write_json_to_file(path, data, mode='w'):
    with open(path, mode) as f:
        jsonutils.dump(data, f)


def write_file(path, data, mode='w'):
    with open(path, mode) as f:
        f.write(data)


def parse_ini_file(path):
    parser = configparser.ConfigParser()

    try:
        files = parser.read(path)
    except configparser.MissingSectionHeaderError:
        logger.exception('invalid file type')
        raise
    else:
        if not files:
            raise RuntimeError('file not exist')

    try:
        default = {k: v for k, v in parser.items('DEFAULT')}
    except configparser.NoSectionError:
        default = {}

    config = dict(DEFAULT=default,
                  **{s: {k: v for k, v in parser.items(
                      s)} for s in parser.sections()})

    return config


def get_port_mac(sshclient, port):
    cmd = "ifconfig |grep HWaddr |grep %s |awk '{print $5}' " % port
    status, stdout, stderr = sshclient.execute(cmd)

    if status:
        raise RuntimeError(stderr)
    return stdout.rstrip()


def get_port_ip(sshclient, port):
    cmd = "ifconfig %s |grep 'inet addr' |awk '{print $2}' " \
          "|cut -d ':' -f2 " % port
    status, stdout, stderr = sshclient.execute(cmd)

    if status:
        raise RuntimeError(stderr)
    return stdout.rstrip()


def flatten_dict_key(data):
    next_data = {}

    # use list, because iterable is too generic
    if not any(isinstance(v, (collections.Mapping, list))
               for v in data.values()):
        return data

    for k, v in data.items():
        if isinstance(v, collections.Mapping):
            for n_k, n_v in v.items():
                next_data["%s.%s" % (k, n_k)] = n_v
        # use list because iterable is too generic
        elif isinstance(v, collections.Iterable) and not isinstance(v, six.string_types):
            for index, item in enumerate(v):
                next_data["%s%d" % (k, index)] = item
        else:
            next_data[k] = v

    return flatten_dict_key(next_data)


def translate_to_str(obj):
    if isinstance(obj, collections.Mapping):
        return {str(k): translate_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [translate_to_str(ele) for ele in obj]
    elif isinstance(obj, six.text_type):
        return str(obj)
    return obj


def result_handler(status, data):
    result = {
        'status': status,
        'result': data
    }
    return jsonify(result)


def set_dict_value(dic, keys, value):
    return_dic = dic

    for key in keys.split('.'):
        return_dic.setdefault(key, {})
        if key == keys.split('.')[-1]:
            return_dic[key] = value
        else:
            return_dic = return_dic[key]
    return dic


def get_free_port(ip):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        port = random.randint(5000, 10000)
        while s.connect_ex((ip, port)) == 0:
            port = random.randint(5000, 10000)
        return port


def mac_address_to_hex_list(mac):
    octets = ["0x{:02x}".format(int(elem, 16)) for elem in mac.split(':')]
    assert len(octets) == 6 and all(len(octet) == 4 for octet in octets)
    return octets


def safe_ip_address(ip_addr):
    """ get ip address version v6 or v4 """
    try:
        return ipaddress.ip_address(six.text_type(ip_addr))
    except ValueError:
        logging.error("%s is not valid", ip_addr)
        return None


def get_ip_version(ip_addr):
    """ get ip address version v6 or v4 """
    try:
        address = ipaddress.ip_address(six.text_type(ip_addr))
    except ValueError:
        logging.error("%s is not valid", ip_addr)
        return None
    else:
        return address.version


def ip_to_hex(ip_addr, separator=''):
    try:
        address = ipaddress.ip_address(six.text_type(ip_addr))
    except ValueError:
        logging.error("%s is not valid", ip_addr)
        return ip_addr

    if address.version != 4:
        return ip_addr

    if not separator:
        return '{:08x}'.format(int(address))

    return separator.join('{:02x}'.format(octet) for octet in address.packed)


def try_int(s, *args):
    """Convert to integer if possible."""
    try:
        return int(s)
    except (TypeError, ValueError):
        return args[0] if args else s


class SocketTopology(dict):

    @classmethod
    def parse_cpuinfo(cls, cpuinfo):
        socket_map = {}

        lines = cpuinfo.splitlines()

        core_details = []
        core_lines = {}
        for line in lines:
            if line.strip():
                name, value = line.split(":", 1)
                core_lines[name.strip()] = try_int(value.strip())
            else:
                core_details.append(core_lines)
                core_lines = {}

        for core in core_details:
            socket_map.setdefault(core["physical id"], {}).setdefault(
                core["core id"], {})[core["processor"]] = (
                core["processor"], core["core id"], core["physical id"])

        return cls(socket_map)

    def sockets(self):
        return sorted(self.keys())

    def cores(self):
        return sorted(core for cores in self.values() for core in cores)

    def processors(self):
        return sorted(
            proc for cores in self.values() for procs in cores.values() for
            proc in procs)


def config_to_dict(config):
    return {section: dict(config.items(section)) for section in
            config.sections()}


def validate_non_string_sequence(value, default=None, raise_exc=None):
    # NOTE(ralonsoh): refactor this function to check if raise_exc is an
    # Exception. Remove duplicate code, this function is duplicated in this
    # repository.
    if isinstance(value, collections.Sequence) and not isinstance(value, six.string_types):
        return value
    if raise_exc:
        raise raise_exc  # pylint: disable=raising-bad-type
    return default


def join_non_strings(separator, *non_strings):
    try:
        non_strings = validate_non_string_sequence(non_strings[0], raise_exc=RuntimeError)
    except (IndexError, RuntimeError):
        pass
    return str(separator).join(str(non_string) for non_string in non_strings)


def safe_decode_utf8(s):
    """Safe decode a str from UTF"""
    if six.PY3 and isinstance(s, bytes):
        return s.decode('utf-8', 'surrogateescape')
    return s


class ErrorClass(object):

    def __init__(self, *args, **kwargs):
        if 'test' not in kwargs:
            raise RuntimeError

    def __getattr__(self, item):
        raise AttributeError


class Timer(object):
    def __init__(self):
        super(Timer, self).__init__()
        self.start = self.delta = None

    def __enter__(self):
        self.start = datetime.datetime.now()
        return self

    def __exit__(self, *_):
        self.delta = datetime.datetime.now() - self.start

    def __getattr__(self, item):
        return getattr(self.delta, item)


def find_relative_file(path, task_path):
    """
    Find file in one of places: in abs of path or relative to a directory path,
    in this order.

    :param path:
    :param task_path:
    :return str: full path to file
    """
    # fixme: create schema to validate all fields have been provided
    for lookup in [os.path.abspath(path), os.path.join(task_path, path)]:
        try:
            with open(lookup):
                return lookup
        except IOError:
            pass
    raise IOError(errno.ENOENT, 'Unable to find {} file'.format(path))


def open_relative_file(path, task_path):
    try:
        return open(path)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return open(os.path.join(task_path, path))
        raise


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def deep_dotdict(obj):
    if isinstance(obj, dict):
        dot_dict = {}
        for k, v in obj.items():
            if isinstance(k, basestring) and not k.startswith('_'):
                v = deep_dotdict(v)
                dot_dict[k] = v
        return dotdict(dot_dict)
    if isinstance(obj, list):
        new_list = []
        for element in obj:
            element = deep_dotdict(element)
            new_list.append(element)
        return new_list
    return obj


def normalize_data_struct(obj, cache={}):
    if obj is None:
        return None
    if id(obj) in cache.keys():
        return cache[id(obj)]
    if isinstance(obj, list):
        normalized_list = []
        for element in obj:
            element = normalize_data_struct(element, cache)
            normalized_list.append(element)
        return normalized_list
    if isinstance(obj, dict):
        normalized_dict = {}
        for k, v in obj.items():
            if isinstance(k, basestring) and not k.startswith('_'):
                v = normalize_data_struct(v, cache)
                normalized_dict[k] = v
        return normalized_dict
    # return obj if it is string, integer, bool ect.
    if not hasattr(obj, '__dict__'):
        return obj
    obj_as_dict = {}
    cache[id(obj)] = obj_as_dict
    normalized = normalize_data_struct(obj.__dict__, cache)
    obj_as_dict.update(normalized)
    return obj_as_dict


def xml_to_dict(xml_str):
    return element_tree_to_dict(xml.etree.ElementTree.fromstring(xml_str))


def element_tree_to_dict(element_tree):
    def internal_iter(tree, accum):
        if tree is None:
            return accum
        attribute_target = None
        if tree.getchildren():
            accum[tree.tag] = {}
            attribute_target = accum[tree.tag]
            for each in tree.getchildren():
                result = internal_iter(each, {})
                if each.tag in accum[tree.tag]:
                    if not isinstance(accum[tree.tag][each.tag], list):
                        accum[tree.tag][each.tag] = [
                            accum[tree.tag][each.tag]
                        ]
                    accum[tree.tag][each.tag].append(result[each.tag])
                else:
                    accum[tree.tag].update(result)
        else:
            attribute_target = accum
            accum[tree.tag] = tree.text
        # Add attributes
        attributes = tree.attrib or {}
        for att_name, att_value in attributes.iteritems():
            attribute_target[att_name] = att_value

        return accum

    return internal_iter(element_tree, {})


def resource_as_string(path):
    resource = load_resource(path)
    return resource.read()


def load_resource(path, mode="r"):
    try:
        return open(path, mode)
    except Exception:
        split_path = os.path.split(path)
        package = split_path[0].replace("/", ".")
        if not pkg_resources.resource_exists(package, split_path[1]):
            raise ResourceNotFound(resource=path)
        return pkg_resources.resource_stream(package, split_path[1])


def resource_abs_path(path, mode="r"):
    try:
        open(path, mode)
        return path
    except Exception:
        split_path = os.path.split(path)
        package = split_path[0].replace("/", ".")
        if not pkg_resources.resource_exists(package, split_path[1]):
            raise ResourceNotFound(resource=path)
        return pkg_resources.resource_filename(package, split_path[1])


def format(in_obj, params):
    if isinstance(in_obj, list):
        ret_list = []
        for item in in_obj:
            item = format(item, params)
            ret_list.append(item)
        return ret_list
    if isinstance(in_obj, dict):
        ret_dict = {}
        for k, v in in_obj.items():
            v = format(v, params)
            ret_dict[k] = v
        return ret_dict
    if not isinstance(in_obj, basestring):
        return in_obj

    ret_str = ""
    ret_obj = None
    for literal_text, field_name, format_spec, conversion in \
            Formatter().parse(in_obj):
        if field_name is None:
            ret_str = ret_str + literal_text
        else:
            tmp_dict = ret_obj or params
            try:
                value = tmp_dict[field_name]
            except KeyError:
                tmp_dict = deep_dotdict(tmp_dict)
                field_name = '{' + field_name + '}'
                value = field_name.format(**tmp_dict)
            if isinstance(value, basestring):
                ret_str = ret_str + value
            else:
                ret_obj = value
    return ret_obj or ret_str
