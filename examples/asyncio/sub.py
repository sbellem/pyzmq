"""Example using zmq with asyncio with pub/sub and dealer/router for
asynchronous messages

Publisher sends either 'Hello World' or 'Hello Sekai' based on class
language setting, which is received by the Subscriber

When the Router receives a message from the Dealer, it changes the
language setting
"""

# Copyright (c) Stef van der Struijk.
# This example is in the public domain (CC-0)

import asyncio
import logging
import time
import traceback

import zmq.asyncio
from zmq.asyncio import Context


# receives "Hello World" from topic 'world'
# changes "World" to "Sekai" and returns message 'sekai'
class HelloWorldPrinter:
    # process received message
    def msg_sub(self, msg):
        print(f"{time.ctime()} -- message received world: {msg}")


# manages message flow of subscribers
class Sub:
    def __init__(self, *, host="127.0.0.1", port=5555):
        # get ZeroMQ version
        print("Current libzmq version is %s" % zmq.zmq_version())
        print("Current  pyzmq version is %s" % zmq.__version__)

        self.host = host
        self.port = port
        self.url = f"tcp://{self.host}:{self.port}"
        # sub and dealer
        self.ctx = Context.instance()

        # activate subscriber
        asyncio.get_event_loop().run_until_complete(
            asyncio.wait({self.sub()})  # less restrictions than REQ
        )

    # processes message topic 'world'; "Hello World" or "Hello Sekai"
    async def sub(self):
        print("Setting up world SUB")
        obj = HelloWorldPrinter()
        # setup subscriber
        sub = self.ctx.socket(zmq.SUB)
        print(f"Connecting SUBSCRIBER to {self.url}")
        sub.bind(self.url)
        sub.setsockopt(zmq.SUBSCRIBE, b"world")
        print("World SUB initialized")

        # without try statement, no error output
        try:
            # keep listening to all published message on topic 'world'
            while True:
                topic, msg = await sub.recv_multipart()
                print(f"{time.ctime()} -- world SUB; topic: {topic}\tmessage: {msg}")
                # process message
                obj.msg_sub(msg.decode())

                # await asyncio.sleep(.2)

                # publish message to topic 'sekai'
                # async always needs `send_multipart()`
                # await pub.send_multipart([b'sekai', msg_publish.encode('ascii')])

        except Exception:
            print("Error with sub world")
            # print(e)
            logging.error(traceback.format_exc())
            print()

        finally:
            # TODO disconnect pub/sub
            pass


if __name__ == "__main__":
    import argparse

    # arg parsing
    default_host = "127.0.0.1"
    parser = argparse.ArgumentParser(description="SUB")
    parser.add_argument(
        "--host",
        default=default_host,
        help=f"Host of publisher to subscribe to. Defaults to '{default_host}'.",
    )
    default_port = 5555
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Port of publisher to subscribe to. Defaults to '{default_port}'.",
    )
    args = parser.parse_args()
    Sub(host=args.host, port=args.port)
