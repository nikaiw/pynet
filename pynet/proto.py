#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
from collections import defaultdict

from pynet.tools.utils import Register,DirectAccessDict

class ProtoRegister(Register):
    _cmd_  = "Proto"
    _desc_ = "List of registered Proto"
    registry = defaultdict(dict)

class Proto(object):
    _desc_ = "Default proto"
    registerer = ProtoRegister

    @classmethod
    def register(cls,f):
        PluginRegister.register(f)
        return cls.registerer.register(f)

    @classmethod
    def from_cli(cls,cli):
        obj = cls(**cli)
        obj.cli = cli
        return obj

    @classmethod
    def set_cli_arguments(cls,parser):
        pass

    @classmethod
    def get_cmdline_name(cls):
        if hasattr(cls,"_cmd_") and \
           (not hasattr(cls.__bases__[0],"_cmd_") or cls.__bases__[0]._cmd_ != cls._cmd_):
            key = "_cmd_"
        else:
            key = "__name__"
        return getattr(cls,key)

    def add_layer(self,data):
        return data

    def del_layer(self,data):
        return data

    def __init__(self,*args,**kargs):
        self.args = DirectAccessDict(kargs)


class NoProto(object):
    _desc_ = "No specific protocol"


class LengthProto(object):
    _desc_ = "Len proto"

    def __init__(self,fmt=">H",*args,**kargs):
        super().__init__(*args,**kargs)
        self.buf = b""
        self.fmt = fmt
        self.fmt_sz = struct.calcsize(self.fmt)

    def add_layer(self,data):
        return struct.pack(self.fmt,len(data)) + data

    def del_layer(self,data):
        data = self.buf + data
        self.buf = b""
        try:
            sz = struct.unpack(self.fmt,data[:self.fmt_sz])[0]
        except:
            self.buf = data
            return None

        payload  = data[self.fmt_sz:]

        if len(payload) < sz: # Missing payload
            self.buf = data
            return None
        elif len(payload) == sz:
            return payload
        else: # To much data
            res = []
            while len(payload) > 0:
                res.append(payload[:sz])
                data = payload[sz:]
                try:
                    sz = struct.unpack(self.fmt,data[:self.fmt_sz])[0]
                except:
                    self.buf = data
                    return res

                payload  = data[self.fmt_sz:]
                if len(payload) < sz:
                    self.buf = data
                    return res
