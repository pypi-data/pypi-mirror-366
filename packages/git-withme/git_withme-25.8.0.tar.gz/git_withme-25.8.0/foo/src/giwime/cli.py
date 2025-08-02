import os
import sys
import json
import signal
import shutil
import functools
from collections import defaultdict
from pathlib import Path
import tty
import termios
import humanize

import click

from twisted.internet.task import react, deferLater
from twisted.internet.defer import ensureDeferred, Deferred, race
from twisted.internet.utils import getProcessOutputAndValue
from twisted.internet.protocol import Factory, Protocol, BaseProtocol
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet.stdio import StandardIO

from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from twisted.internet.protocol import ProcessProtocol, Protocol, Factory
from attr import frozen

from wormhole.cli.public_relay import MAILBOX_RELAY
from wormhole import create as wormhole_create
import fowl.api
from fowl._proto import fowld_command_to_json, parse_fowld_output  # FIXME private? or API?
from fowl.messages import Welcome, AllocateCode, CodeAllocated, PeerConnected, GrantPermission, RemoteListener, RemoteListeningSucceeded, IncomingDone, IncomingConnection, RemoteListeningFailed, Listening, SetCode

from .status import Status, Peer, Activity
from fowl.cli import WELL_KNOWN_MAILBOXES, _Config as FowlConfig


well_known_names = ", ".join(f'"{name}"' for name in WELL_KNOWN_MAILBOXES.keys())


@frozen
class _Config:
    """
    Represents a set of validated configuration
    """
    mailbox_url: str
    repository: Path


def react_coro(coro_fn, *args, **kwargs):
    """
    Properly run the given coroutine using Twisted's react()
    """
    return react(
        lambda reactor: ensureDeferred(
            coro_fn(reactor, *args, **kwargs)
        )
    )


@click.group(invoke_without_command=True)
@click.option(
    "--mailbox", "-m",
    help=f"The Magic Wormhole Mailbox to use (or the name of one: {well_known_names}). Default is {MAILBOX_RELAY}",
    default=MAILBOX_RELAY,
)
@click.option(
    "--repo",
    required=False,
    default=".",
    # note: https://github.com/pallets/click/issues/1428
    # exists=False does _not_ mean "it must not exist"
    type=click.Path(path_type=Path),
    metavar="DIR",
    help='The directory which will contain the clone (use "--update" on an existing repository)',
)
@click.pass_context
def withme(ctx, mailbox, repo):
    """
    Invite collaborators to a Git repository

    With no subcommand, begin hosting a repository. A bare repository
    is created in $TMPDIR so that collaborators can use this like
    GitLab or GitHub.
    """
    ctx.obj = _Config(
        mailbox_url=WELL_KNOWN_MAILBOXES.get(mailbox, mailbox),
        repository=repo,
    )

    p = Path(repo).absolute()
    gitp = p / ".git"
    if not gitp.exists():
        print(f"Not a git repository; can't find {gitp.absolute()}")

    # when invoked as "git-withme accept" the subcommand will be
    # non-None, otherwise we want to run the actual command -- without
    # the early return it's impossible to use "git-withme accept"
    if ctx.invoked_subcommand is not None:
        return

    react_coro(_host_main, p, ctx.obj.mailbox_url)


@withme.command()
@click.option(
    "--update/--no-update",
    required=False,
    default=False,
    help="If the --repo path already exists, update it in-place",
)
@click.argument(
    "code",
)
@click.pass_context
def accept(ctx, code, update):
    """
    Accept a git-withme invite to collaborate on a repository.

    This will add a 'gitwithme' remote to the given repository, and
    remove it at the end of the collaboration session (when this
    command ends).

    While 'git-withme accept' is running, you can use the repository
    like you would a hosted bare Git repository (e.g. like GitLab or
    GitHub): 'git push gitwithme' to share changes and 'git pull
    gitwithme' to receive changes.

    The difference is that the peer running 'git-withme host' has the
    remote repository, and all messaging is end-to-end encrypted to
    your peer. The host may invite multiple clients.
    """
    print("ASDF")
    cfg = ctx.obj
    if cfg.repository.exists():
        if not update:
            print(f'"{cfg.repository}" exists; aborting. Use --update if you wanted to re-use a repository')
            print("(We have not consumed the magic code, you may re-try)")
            return 1

    react_coro(_accept_main, code, cfg.repository, ctx.obj.mailbox_url)



class FowlProtocol(ProcessProtocol):
    """
    This speaks to an underlying ``fowl`` sub-process.
    """

    def __init__(self, on_message, done):
        self._on_message = on_message
        self._data = b""
        self._done = done

    def childDataReceived(self, childFD, data):
        if childFD != 1:
            print(data.decode("utf8"), end="")
            return

        self._data += data
        while b'\n' in self._data:
            line, self._data = self._data.split(b"\n", 1)
            try:
                msg = parse_fowld_output(line)
            except Exception as e:
                print(f"Not JSON: {line}: {e}")
            else:
                d = ensureDeferred(self._on_message(msg))
                d.addErrback(lambda f: print(f"BAD: {f}"))

    def processEnded(self, reason):
        self._done.callback(None)

    def send_message(self, msg):
        self.transport.write(
            json.dumps(
                fowld_command_to_json(msg)
            ).encode("utf8") + b"\n"
        )


class GitProtocol(ProcessProtocol):
    """
    Speak to git-daemon
    """

    def __init__(self):
        # all messages we've received that _haven't_ yet been asked
        # for via next_message()
        self._messages = []
        # maps str -> list[Deferred]: kind-string to awaiters
        self._message_awaits = defaultdict(list)
        self.exited = Deferred()
        self._data = b""

    def processEnded(self, reason):
        self.exited.callback(None)

    def childDataReceived(self, childFD, data):
        print(data.decode("utf8"), end="", flush=True)
        return
        if childFD != 1:
            print(data.decode("utf8"), end="")
            return

        self._data += data
        while b'\n' in self._data:
            line, self._data = self._data.split(b"\n", 1)
            print(f"Git: {line}")


class Commands(BaseProtocol):

    def __init__(self, on_command):
        self._command = on_command

    def dataReceived(self, data):
        data = data.decode("utf8")
        for char in data:
            self._command(char)

    def connectionLost(self, reason):
        pass



async def _host_main(reactor, repo_p, mailbox_url):
    """
    - (optional?) make a bare repo, etc? ... auto-remote?
    - create: temporary bare git repo
    - connect: "this" git repo to ^
    - push: everything? current branh? to ^
    - spawn: git daemon (on "temporary bare git repo")
    - spawn: fowld (for each client)
    """

    #XXX we want to refactor this so that the "main" / run parts call
    #the "real" API stuff -- and that should "take" an existing
    #wormhole -- so that we can "plug in" a "Git Withme" thing

    env = os.environ.copy()
    git_bin = shutil.which("git")
    ## using "-u" instead env['PYTHONUNBUFFERED'] = '1'

    # 1. add a remote for "gitwithme"

    # 1. a) first, check if we already have that remote
    out, err, code = await getProcessOutputAndValue(
        git_bin,
        [
            f"--git-dir={(repo_p / '.git').absolute()}",
            "remote",
        ],
        env=env,
    )
    remotes = out.decode("utf8").strip().split("\n")
    if code != 0:
        print(f"Error:\n{out}\n{err}")
        return
    if "gitwithme" in remotes:
        print(f'Aready have a "gitwithme" remote; not overwriting it')
        return

    # 1. b) actually create a bare repo in /tmp or whatever
    from tempfile import TemporaryDirectory
    bare_git = TemporaryDirectory()
    reactor.addSystemEventTrigger("after", "shutdown", bare_git.cleanup)

    bare_git_p = Path(bare_git.name) / "gitwithme_remote"  # repo_p.name
    bare_git_p.mkdir()

    out, err, code = await getProcessOutputAndValue(
        git_bin,
        [
            "init",
            "--bare",
            bare_git_p,
        ],
        env=env,
    )
    if code != 0:
        print(f"Error:\n{out}\n{err}")
        return

    # 1. c) add the "gitwithme" remote, pointing at the new bare repo in /tmp
    out, err, code = await getProcessOutputAndValue(
        git_bin,
        [
            f"--git-dir={(repo_p / '.git').absolute()}",
            "remote",
            "add",
            "-f",
            "gitwithme",
            bare_git_p,
        ],
        env=env,
    )
    if code != 0:
        print(f"Error:\n{out}\n{err}")
        return

    async def cleanup_remote():
        """
        When the host daemon shuts down, we remove the 'gitwithme'
        remote (because it's in temp so will be deleted anyway, even
        if our cleanup code never ran)
        """
        out, err, code = await getProcessOutputAndValue(
            git_bin,
            [
                f"--git-dir={(repo_p / '.git').absolute()}",
                "remote",
                "remove",
                "gitwithme",
            ],
            env=env,
        )
        if code != 0:
            print(f"Error cleaning up 'gitwithme' remote:\n{out}\n{err}")
            return
    reactor.addSystemEventTrigger(
        "before", "shutdown",
        lambda: ensureDeferred(cleanup_remote())
    )

    # 2. We have our local, bare git repo -- new poplate it
    out, err, code = await getProcessOutputAndValue(
        git_bin,
        [
            f"--git-dir={(repo_p / '.git').absolute()}",
            "push",
            "--all",
            "gitwithme",
        ],
        env=env,
    )
    if code != 0:
        print(f"Error:\n{out}\n{err}")
        return

    #XXX decide on port a better way? (e.g. "allocate random unused one")

    # 3. Run "git daemon" in the bare git repo so we can export over
    # the network (but only on magic-wormhole)
    gitproto = GitProtocol()
    basep = repo_p.parent
    gitprocess = reactor.spawnProcess(
        gitproto,
        git_bin,
        [
            "git", "daemon",
            "--reuseaddr",
            "--listen=localhost",
            "--export-all",
            f"--base-path={bare_git_p.parent}",
            "--log-destination=stderr",
            "--enable=receive-pack",
            "--enable=upload-pack",
            bare_git_p,
        ],
        env=env,
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown",
        lambda: gitprocess.signalProcess(signal.SIGTERM),
    )
    print(f"Hosting {repo_p} (via bare repo {bare_git_p})")

    # 4. Invite peers

    status = Status()

    def create_peer():
        peer = Peer()
        status.peers.append(peer)

        @functools.singledispatch
        async def on_message(msg):
            print(f"MSG: {msg}")

        @on_message.register(Welcome)
        async def _(msg):
            print("welcome", msg.url)
            peer.url = msg.url
            # do something -- allocate unused port
            fowlproto.send_message(GrantPermission([], [9418]))
            fowlproto.send_message(RemoteListener("tcp:9419:interface=localhost", "tcp:localhost:9418"))
            fowlproto.send_message(AllocateCode())

        @on_message.register(CodeAllocated)
        async def _(msg):
            peer.code = msg.code

        @on_message.register(PeerConnected)
        async def _(msg):
            peer.connected = reactor.seconds()
            print("connected.")

        @on_message.register(RemoteListeningSucceeded)
        async def _(msg):
            peer.listening = True

        @on_message.register(RemoteListeningFailed)
        async def _(msg):
            print(f"Bad: {msg.message}")

        @on_message.register(IncomingConnection)
        async def _(msg):
            peer.activity.append(
                Activity(msg.id, reactor.seconds())
            )

        peer_done = Deferred()
        @peer_done.addCallback
        def _(_):
            status.peers.remove(peer)

        def on_status(st):
            print("status:", st)

        wh = wormhole_create(
            "meejah.ca/git-withme",
            mailbox_url,
            reactor,
            # XXX do we want "fowl" stuff in here? how would it get here if we did?
            versions={
                "git-withme": {
                    "features": ["giwime-core"],
                }
            },
            dilation=True,
            on_status_update=on_status,
        )
        nest = fowl.api.create(reactor)
        config = FowlConfig(
            relay_url=mailbox_url,
            use_tor=False,
            code=None,
            code_length=2,
            commands=[],
            listen_policy=None,
            connect_policy=None,
            output_debug_messages=None,
        )

        def on_msg_eat_async(msg):
            d = ensureDeferred(on_message(msg))
            d.addErrback(lambda f: print(f"BAD: {f}"))

        subprotocols = nest.build_subprotocols(on_msg_eat_async)
        dilated = wh.dilate(subprotocols)
        print("DING", dilated)
        nest.dilated(dilated)

        # XXX okay so we could maybe refactor so that all the
        # "out_message" stuff is written via a "sequential"-looking
        # thing where it does like "welcom = await wh.get_welcome()"
        # etc etc
        async def run_peer():
            welcome = await wh.get_welcome()
            print("WELCOME", welcome)
            wh.allocate_code()
            code = await wh.get_code()
            print("CODE", code)
            channel = await nest.fledge(
                unique_name="gitwithme-fixme",
                endpoint=TCP4ClientEndpoint(reactor, "localhost", 9418),
            )
            print("channel", channel)
        reactor.callLater(0, lambda: ensureDeferred(run_peer()))

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    # see also https://github.com/Textualize/rich/issues/1103
    tty.setcbreak(fd)

    done = Deferred()
    def on_command(char):
        print("oncommand", char)
        if char.lower() == 'q':
            done.callback(None)
        if char.lower() == 'n':
            create_peer()

    def render():
        top = Table(show_header=False, show_lines=False, show_edge=False)
        if True:
            message = Text("Hosting:")
            message.append_text(Text(f" {repo_p}", style="bold red"))
            message.append("\nGit WithMe is now running. To push code to all peers, use:")
            message.append("\n    git push gitwithme", style="bold")
            message.append("\n...and to receive code from a peer who has pushed, use:")
            message.append("\n    git pull gitwithme main", style="bold")
            message.append("\nThe temporary bare repository we created will be deleted when")
            message.append("\nthis process is terminated.")
            message.append("\n")
            message.append("\nN -- create new peer", style="bold")
            message.append("\nQ -- quit, terminate all peers")

        top.add_row(Panel.fit(message))

        peers = Table(show_header=False, show_lines=True, title="Peers")

        for p in status.peers:
            if p.connected:
                interval = reactor.seconds() - p.connected
                interval = humanize.naturaldelta(interval)
                r = Text("Connected")
                r.stylize("rgb(50,200,50)")
                r.append(f" (for {interval}). ")
                if p.activity:
                    act = p.activity[-1]
                    interval = reactor.seconds() - act.started
                    interval = humanize.naturaldelta(interval)
                    interval = f"(last {interval} ago)"
                    lots = "🥳..." if len(p.activity) > 10 else ""
                    recent = p._act_perm[:min(10, len(p.activity))]
                    r.append_text(Text(f"{lots}{recent} {interval}"))
                else:
                    r.append_text(Text(f"(no activity)"))
            elif p.code is None:
                if p.url is None:
                    r = Text("Connecting...")
                else:
                    r = Text(p.url, style="rgb(0,200,0)")
            else:
                r = Text("Invite code:")
                r.stylize("rgb(0,0,0) on rgb(200,255,0)")
                c = Text(f" {p.code}")
                r.append(c)
            peers.add_row(r)

        top.add_row(peers)

        return top


    try:
        cmds = Commands(on_command)
        stdio = StandardIO(cmds)

        if 1:
        #with Live(get_renderable=render):
            while not done.called:
                await deferLater(reactor, 0.25, lambda: None)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


async def _accept_main(reactor, magic_code: str, repo_p: Path, mailbox_url: str):
    """
    The 'invitee' side of the git-withme flow
    """
    env = os.environ.copy()
    git_bin = shutil.which("git")

    @functools.singledispatch
    async def on_message(msg):
        pass

    @on_message.register(Welcome)
    async def _(msg):
        print("welcome", msg.url)
        fowlproto.send_message(GrantPermission([9419], []))
        fowlproto.send_message(SetCode(magic_code))

    @on_message.register(PeerConnected)
    async def _(msg):
        print("Peer has connected.")

    @on_message.register(Listening)
    async def _(msg):
        print("Listening", msg)

        # now we are listening, we can clone the remote repo
        repo_name = "gitwithme_remote"
        out, err, code = await getProcessOutputAndValue(
            git_bin,
            [
                 "clone",
                f"git://localhost:4321/{repo_name}",
                repo_p,
            ],
            env=env,
        )
        n = "git" if code == 0 else "ERR"
        for line in out.decode("utf8").split("\n"):
            print(f"  {n}: {line}")
        for line in err.decode("utf8").split("\n"):
            print(f"  {n}: {line}")
        if code != 0:
            print("Cloning failed")
            return

        print(f"You can now use normal git commands in {repo_p}")
        print('"git pull": update from the host')
        print('"git push": push changes to the host')


    def on_status(st):
        print("status:", st)

    wh = wormhole_create(
        "meejah.ca/git-withme",
        mailbox_url,
        reactor,
        # XXX do we want "fowl" stuff in here? how would it get here if we did?
        versions={
            "git-withme": {
                "features": ["giwime-core"],
            }
        },
        dilation=True,
        on_status_update=on_status,
    )
    # XXX wrong api here, we NEED both sides to create a FowlNest() so
    # the ONLY interaction with Fowl must be via this thing ... so we
    # need to give it the wormhole, so that it may dilate 'for us'?
    # ....well, what about "fowl(git) + fowl(sync)"?
    nest = fowl.api.create(reactor)
    config = FowlConfig(
        relay_url=mailbox_url,
        use_tor=False,
        code=None,
        code_length=2,
        commands=[],
        listen_policy=None,
        connect_policy=None,
        output_debug_messages=None,
    )

    def on_msg_eat_async(msg):
        d = ensureDeferred(on_message(msg))
        d.addErrback(lambda f: print(f"BAD: {f}"))

    subprotocols = nest.build_subprotocols(on_msg_eat_async)
    dilated = wh.dilate(subprotocols)
    print("DING", dilated)
    nest.dilated(dilated)

    # XXX okay so we could maybe refactor so that all the
    # "out_message" stuff is written via a "sequential"-looking
    # thing where it does like "welcom = await wh.get_welcome()"
    # etc etc
    async def run_peer():
        welcome = await wh.get_welcome()
        print("WELCOME", welcome)
        wh.set_code(magic_code)
        await wh.get_code()
        channel = await nest.permit_fledgling(
            unique_name="gitwithme-fixme",
##            endpoint=TCP4ServerEndpoint(reactor, 9419, interface="localhost"),
        )
        print("channel", channel)
    reactor.callLater(0, lambda: ensureDeferred(run_peer()))

    await Deferred()
