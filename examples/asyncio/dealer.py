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

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5556


class Dealer:
    def __init__(self, *, host=DEFAULT_HOST, port=DEFAULT_PORT):
        # get ZeroMQ version
        print("Current libzmq version is %s" % zmq.zmq_version())
        print("Current  pyzmq version is %s" % zmq.__version__)

        self.host = host
        self.port = port
        # sub and dealer
        self.ctx = Context.instance()

        # activate subscriber
        asyncio.get_event_loop().run_until_complete(
            asyncio.wait({self.dealer()})  # less restrictions than REQ
        )

    # Deal a message to topic 'lang' that language should be changed
    async def dealer(self):
        # setup dealer
        deal = self.ctx.socket(zmq.DEALER)
        deal.setsockopt(zmq.IDENTITY, b"lang_dealer")
        url = f"tcp://{self.host}:{self.port}"
        print("\n")
        print(79 * "*")
        print(f"*           connecting DEALER to {url}                         *")
        print(79 * "*", end="\n\n")
        deal.connect(url)
        print("Command DEALER initialized")

        # give time to router to initialize; wait time >.2 sec
        await asyncio.sleep(0.3)
        msg = f"Change that language!"

        # without try statement, no error output
        try:
            # keep sending messages
            while True:
                print(f"{time.ctime()} -- Command DEALER:\n\t\tmessage: {msg}")

                # slow down message publication
                await asyncio.sleep(2.0)

                # publish message to topic 'world'
                # multipart: topic, message; async always needs `send_multipart()`?
                await deal.send_multipart([msg.encode()])

        except Exception:
            print("Error with pub world")
            # print(e)
            logging.error(traceback.format_exc())
            print()

        finally:
            # TODO disconnect dealer/router
            pass


if __name__ == "__main__":
    import argparse

    # arg parsing
    parser = argparse.ArgumentParser(description="DEALER")
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host of dealer. Defaults to '{DEFAULT_HOST}'.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port of dealer. Defaults to '{DEFAULT_PORT}'.",
    )
    args = parser.parse_args()
    Dealer(host=args.host, port=args.port)
