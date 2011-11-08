#
#    Copyright (c) 2010-2011 Brian E. Granger & Min Ragan-Kelley
#
#    This file is part of pyzmq.
#
#    pyzmq is free software; you can redistribute it and/or modify it under
#    the terms of the Lesser GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    pyzmq is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    Lesser GNU General Public License for more details.
#
#    You should have received a copy of the Lesser GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import sys
import time
from threading import Thread

from unittest import TestCase

import zmq
from zmq.utils import jsonapi

try:
    from unittest import SkipTest
except ImportError:
    try:
        from nose import SkipTest
    except ImportError:
        class SkipTest(Exception):
            pass

#-----------------------------------------------------------------------------
# Utilities
#-----------------------------------------------------------------------------
if zmq.zmq_version_info() >= (3,0,0):
    # keep NOBLOCK for tests
    zmq.NOBLOCK = zmq.DONTWAIT

class BaseZMQTestCase(TestCase):

    def setUp(self):
        self.context = zmq.Context.instance()
        self.sockets = []
    
    def tearDown(self):
        contexts = set([self.context])
        while self.sockets:
            sock = self.sockets.pop()
            contexts.add(sock.context) # in case additional contexts are created
            sock.close()
        for ctx in contexts:
            t = Thread(target=ctx.term)
            t.start()
            t.join(timeout=2)
            if sys.version[:3] == '2.5':
                t.is_alive = t.isAlive
            if t.is_alive():
                raise RuntimeError("context could not terminate, open sockets likely remain in test")

    def create_bound_pair(self, type1=zmq.PAIR, type2=zmq.PAIR, interface='tcp://127.0.0.1'):
        """Create a bound socket pair using a random port."""
        s1 = zmq.Socket(self.context, type1)
        s1.setsockopt(zmq.LINGER, 0)
        port = s1.bind_to_random_port(interface)
        s2 = zmq.Socket(self.context, type2)
        s2.setsockopt(zmq.LINGER, 0)
        s2.connect('%s:%s' % (interface, port))
        self.sockets.extend([s1,s2])
        return s1, s2

    def ping_pong(self, s1, s2, msg):
        s1.send(msg)
        msg2 = s2.recv()
        s2.send(msg2)
        msg3 = s1.recv()
        return msg3

    def ping_pong_json(self, s1, s2, o):
        if jsonapi.jsonmod is None:
            raise SkipTest("No json library")
        s1.send_json(o)
        o2 = s2.recv_json()
        s2.send_json(o2)
        o3 = s1.recv_json()
        return o3

    def ping_pong_pyobj(self, s1, s2, o):
        s1.send_pyobj(o)
        o2 = s2.recv_pyobj()
        s2.send_pyobj(o2)
        o3 = s1.recv_pyobj()
        return o3

    def assertRaisesErrno(self, errno, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except zmq.ZMQError:
            e = sys.exc_info()[1]
            self.assertEqual(e.errno, errno, "wrong error raised, expected '%s' \
got '%s'" % (zmq.ZMQError(errno), zmq.ZMQError(e.errno)))
        else:
            self.fail("Function did not raise any error")
    
    def _select_recv(self, multipart, socket, **kwargs):
        """call recv[_multipart] in a way that raises if there is nothing to receive"""
        if zmq.zmq_version_info() >= (3,1,0):
            # zmq 3.1 has a bug, where poll can return false positives,
            # so we wait a little bit just in case
            # See LIBZMQ-280 on JIRA
            time.sleep(0.1)
        
        r,w,x = zmq.select([socket], [], [], timeout=5)
        assert len(r) > 0, "Should have received a message"
        kwargs['flags'] = zmq.DONTWAIT | kwargs.get('flags', 0)
        
        recv = socket.recv_multipart if multipart else socket.recv
        return recv(**kwargs)
        
    def recv(self, socket, **kwargs):
        """call recv in a way that raises if there is nothing to receive"""
        return self._select_recv(False, socket, **kwargs)

    def recv_multipart(self, socket, **kwargs):
        """call recv_multipart in a way that raises if there is nothing to receive"""
        return self._select_recv(True, socket, **kwargs)
    

class PollZMQTestCase(BaseZMQTestCase):
    pass

