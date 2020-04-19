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


# set message based on language
class HelloWorld:
    def __init__(self):
        self.lang = "eng"
        self.msg = "Hello World"

    def change_language(self):
        if self.lang == "eng":
            self.lang = "jap"
            self.msg = "Hello Sekai"

        else:
            self.lang = "eng"
            self.msg = "Hello World"

    def msg_pub(self):
        return self.msg


# manages message flow between publishers and subscribers
class PubRouter:
    def __init__(
        self,
        *,
        sub_host=DEFAULT_HOST,
        sub_port=5555,
        router_host=DEFAULT_HOST,
        router_port=5556,
    ):
        # get ZeroMQ version
        print("Current libzmq version is %s" % zmq.zmq_version())
        print("Current  pyzmq version is %s" % zmq.__version__)

        self.sub_host = sub_host
        self.sub_port = sub_port
        self.router_host = router_host
        self.router_port = router_port

        self.ctx = Context.instance()

        # init hello world publisher obj
        self.hello_world = HelloWorld()

        # activate publishers / subscribers
        asyncio.get_event_loop().run_until_complete(
            asyncio.wait([self.pub(), self.router()])  # less restrictions than REP
        )

    # generates message "Hello World" and publish to topic 'world'
    async def pub(self):
        url = f"tcp://{self.sub_host}:{self.sub_port}"
        pub = self.ctx.socket(zmq.PUB)
        print(f"Connecting PUBLISHER to {url}")
        pub.connect(url)

        # give time to subscribers to initialize; wait time >.2 sec
        await asyncio.sleep(0.3)
        # send setup connection message
        # await pub.send_multipart([b'world', "init".encode('utf-8')])
        # await pub.send_json([b'world', "init".encode('utf-8')])

        # without try statement, no error output
        try:
            # keep sending messages
            while True:
                # ask for message
                msg = self.hello_world.msg_pub()
                print(f"{time.ctime()} -- PUB: {msg}")

                # slow down message publication
                await asyncio.sleep(0.5)

                # publish message to topic 'world'
                # multipart: topic, message; async always needs `send_multipart()`?
                await pub.send_multipart([b"world", msg.encode()])

        except Exception:
            print("Error with pub world")
            # print(e)
            logging.error(traceback.format_exc())
            print()

        finally:
            # TODO disconnect pub/sub
            pass

    # changes Hello xxx message when a command is received from topic 'lang';
    # keeps listening for commands
    async def router(self):
        # setup router
        router = self.ctx.socket(zmq.ROUTER)
        url = f"tcp://{self.router_host}:{self.router_port}"
        print("\n")
        print(79 * "*")
        print(f"*           connecting ROUTER to {url}                         *")
        print(79 * "*", end="\n\n")
        router.bind(url)
        # router.setsockopt(zmq.SUBSCRIBE, b'')
        print("Command ROUTER initialized")

        # without try statement, no error output
        try:
            # keep listening to all published message on topic 'world'
            while True:
                id_dealer, msg = await router.recv_multipart()
                print(
                    f"{time.ctime()} -- Command ROUTER:\n"
                    f"\t\tsender ID: {id_dealer}\n"
                    f"\t\tmessage: {msg}"
                )

                self.hello_world.change_language()
                print(
                    "\t\tChanged language! New language is: {self.hello_world.lang}\n"
                )

        except Exception:
            print("Error with sub world")
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
        "--sub-host",
        default=DEFAULT_HOST,
        help=(
            f"Host of subscriber to connect to send messages to. "
            f"Defaults to '{DEFAULT_HOST}'."
        ),
    )
    default_sub_port = 5555
    parser.add_argument(
        "--sub-port",
        type=int,
        default=default_sub_port,
        help=(
            f"Port of subscriber to connect to send messages to. "
            f"Defaults to '{default_sub_port}'."
        ),
    )
    parser.add_argument(
        "--router-host",
        default=DEFAULT_HOST,
        help=(
            f"Host of router to bind to listen to messages. "
            f"Defaults to '{DEFAULT_HOST}'."
        ),
    )
    default_router_port = 5556
    parser.add_argument(
        "--router-port",
        type=int,
        default=default_router_port,
        help=(
            f"Port of router to bind to listent to messages. "
            f"Defaults to '{default_router_port}'."
        ),
    )
    args = parser.parse_args()
    PubRouter(
        sub_host=args.sub_host,
        sub_port=args.sub_port,
        router_host=args.router_host,
        router_port=args.router_port,
    )
