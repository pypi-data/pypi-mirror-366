import os
import sys
import tty
import pty
import fcntl
import array
import termios
import click
import signal
import shutil
import wormhole
from wormhole.cli import public_relay
from fowl.api import create_coop
from fowl._proto import create_fowl
from fowl.observer import When
from fowl.tcp import allocate_tcp_port
from twisted.internet.defer import ensureDeferred, Deferred
from twisted.internet.task import react, deferLater
from twisted.internet.protocol import Protocol
from twisted.internet.stdio import StandardIO
from twisted.internet.error import ProcessDone


@click.command()
@click.option(
    "--mailbox",
    default="ws://relay.magic-wormhole.io:4000/v1",
    help="The Mailbox URL to use",
    required=False,
)
@click.option(
    "--read-only",
    "-R",
    help="Peers cannot provide input to the terminal",
    flag_value="read_only",
    default=False,
)
@click.argument("code", default=None, required=False)
def shwim(code, mailbox, read_only):
    """
    SHell WIth Me allows you to share you shell with another computer.

    This uses the great tty-share under the hood, except that it never
    uses tty-share's public server -- all communications are
    end-to-end encrypted over Magic Wormhole.
    """
    if code is None:
        react(
            lambda r: ensureDeferred(_host(r, mailbox, read_only))
        )
    else:
        react(
            lambda r: ensureDeferred(_guest(r, mailbox, code))
        )


async def _guest(reactor, mailbox, code):
    """
    Share another person's terminal via tty-share
    """
    wh = wormhole.create("meejah.ca/shwim", mailbox, reactor, dilation=True)
    coop = create_coop(reactor, wh)

    wh.set_code(code)
    c = await wh.get_code()

    print("Connecting to peer")
    dilated = await coop.dilate(transit_relay_location=public_relay.TRANSIT_RELAY)
    print("...connected, launching tty-share")

    x = coop.roost("tty-share")
    channel = await coop.when_roosted("tty-share")
    port = channel.connect_port

    await launch_tty_share(reactor, f"http://localhost:{port}/s/local/")
    await Deferred()


class TtyShare(Protocol):
    """
    Speak stdin/stdout to a tty-share

    This also handles synchronizing terminal sizes between our
    controlling terminal and the tty-share subprocess via SIGWINCH
    """

    def __init__(self, reactor):
        self._reactor = reactor
        self._done = When()

    def when_done(self):
        return self._done.when_triggered()

    def connectionMade(self):
        self.transport.write(b"\n")
        # we need to make some terminal Raw somewhere, how about here?
        self._origstate = termios.tcgetattr(0)
        tty.setraw(0)
        self._sync_terminal_size()

    def _sync_terminal_size(self):
        # we should also sync terminal size on SIGWINCH I believe?
        size = termios.tcgetwinsize(0)
        termios.tcsetwinsize(self.transport.fileno(), size)

    def childDataReceived(self, fd, data):
        #print(fd, data)
        self.std.write(data)
        return
        if fd == 1:
            os.write(1, data)
        elif fd == 2:
            os.write(2, data)
        else:
            print("weird", fd)

    def processEnded(self, why):
        termios.tcsetattr(0, termios.TCSADRAIN, self._origstate)
        if isinstance(why.value, ProcessDone):
            why = None
        self._done.trigger(self._reactor, why)


class WriteTo(Protocol):
    """
    Write any incoming data to the attached tty-share
    """

    def __init__(self, ttyshare):
        self._ttyshare = ttyshare

    def connectionMade(self):
        pass

    def dataReceived(self, data):
        self._ttyshare.transport.write(data)

    def processEnded(self, why):
        pass


async def launch_tty_share(reactor, *args):
    """
    run a tty-share subprocess
    """
    proto = TtyShare(reactor)
    # print(f"RUN: {args}")
    proc = reactor.spawnProcess(
        proto,
        shutil.which("tty-share"),
        args=('tty-share',) + args,
        env=os.environ,
        usePTY=True,
    )

    # respond to re-sizes more-or-less properly?
    # XXX use _sync_terminal_size
    def forward_winch(sig, frame):
        proto._sync_terminal_size()
        # print("forward winch")
        # b = array.array('h', [0, 0, 0, 0])
        # fcntl.ioctl(pty.STDOUT_FILENO, termios.TIOCGWINSZ, b, True)
        # fcntl.ioctl(proc.fd, termios.TIOCSWINSZ, b)
        # ##proc.signalProcess(signal.SIGWINCH)
    signal.signal(signal.SIGWINCH, forward_winch)

    std = StandardIO(WriteTo(proto))
    proto.std = std
    await proto.when_done()


async def _host(reactor, mailbox, read_only):
    """
    Run the host side interaction, launching a tty-share
    subprocess and basically turning over 'this' terminal to it.
    """
    print(f"Preparing to share this terminal with a peer")
    if not read_only:
        print(f"Remember: they can type any command!")
        print(f"(So share this code with a person you trust with your keyboard)")
    print()
    wh = wormhole.create("meejah.ca/shwim", mailbox, reactor, dilation=True)
    coop = create_coop(reactor, wh)
    wh.allocate_code()
    code = await wh.get_code()
    print(f"magic code: {code}")

    dilated = await coop.dilate()
    print("host: dilated")

    # XXX need to forward on the "resize" signal to our child, so that
    # if we're too big etc those messages get through

    # we're running the server -- we want a random port, but also we
    # _NEED_ to have the same port in use on the far side, for boring
    # HTTP reasons (the "same origin" check includes the port, so
    # "localhost:1234" is not the same origin as "localhost:<other port>")
    random_port = 8001###allocate_tcp_port()
    # race between here, and when we acutally listen...
    print("host: fledging")
    channel = await coop.fledge("tty-share", random_port, random_port)
    print(f"running tty-share on: {channel.listen_port}")

    if 0:
        await Deferred()
    else:
        ro_args = ["-readonly"] if read_only else []
        await launch_tty_share(reactor, "--listen", f"localhost:{channel.listen_port}", *ro_args)
