#
#   Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2013 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Cocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys

from cocaine.services import Service
from log_message import PROTOCOL_LIST
from log_message import Message

__all__ = ["Logger"]

VERBOSITY_LEVELS = {
    0 : "ignore",
    1 : "error",
    2 : "warn",
    3 : "info",
    4 : "debug"
}

class _STDERR_Logger(object):

    def debug(self, data):
        print >> sys.stderr, data

    def info(self, data):
        print >> sys.stderr, data

    def warn(self, data):
        print >> sys.stderr, data

    def error(self, data):
        print >> sys.stderr, data

    def ignore(self, data):
        print >> sys.stderr, data

def _construct_logger_methods(cls, verbosity_level):
    def closure(_lvl):
        if _lvl <= verbosity_level:
            def func(data):
                cls._counter += 1
                cls._logger.w_stream.write(Message("Message", cls._counter, _lvl,  cls.target, str(data)).pack())
            return func
        else:
            def func(data):
                pass
            return func

    setattr(cls, "_counter", 0)
    for level, name in VERBOSITY_LEVELS.iteritems():
        setattr(cls, name, closure(level))


class Logger(object):

    def __new__(cls):
        if not hasattr(cls, "_instanse"):
            instanse = object.__new__(cls)
            try:
                _logger = Service("logging")
                for verbosity in _logger.perform_sync("verbosity"): #only one chunk and read choke also.
                    pass
                setattr(instanse, "_logger", _logger)
                try:
                    setattr(instanse, "target", "app/%s" % sys.argv[sys.argv.index("--app") + 1])
                except ValueError: 
                    setattr(instanse, "target", "app/%s" % "standalone" )
                _construct_logger_methods(instanse, verbosity)
            except Exception as err:
                instanse = _STDERR_Logger()
                instanse.warn("Logger init error: %s. Use stderr logger" % err)
            cls._instanse = instanse
        return cls._instanse
