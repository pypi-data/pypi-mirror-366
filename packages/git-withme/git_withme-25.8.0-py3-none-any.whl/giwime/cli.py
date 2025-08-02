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
from twisted.internet.defer import ensureDeferred, Deferred
from twisted.internet.utils import getProcessOutputAndValue
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet.protocol import ProcessProtocol, BaseProtocol
from twisted.internet.stdio import StandardIO

from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from attr import frozen

from wormhole.cli.public_relay import MAILBOX_RELAY
from wormhole import create as wormhole_create
from fowl.tcp import allocate_tcp_port
from fowl.api import create_coop
#import fowl.api
#from fowl._proto import fowld_command_to_json, parse_fowld_output  # FIXME private? or API?
from fowl.messages import Welcome, AllocateCode, CodeAllocated, PeerConnected, GrantPermission, RemoteListener, IncomingConnection, Listening, SetCode, BytesIn, BytesOut

from .status import Status, Peer, Activity
from fowl.cli import WELL_KNOWN_MAILBOXES, _Config as FowlConfig


well_known_names = ", ".join(f'"{name}"' for name in WELL_KNOWN_MAILBOXES.keys())


@frozen
class _Config:
    """
    Represents a set of validated configuration
    """
    mailbox_url: str
    repo: str


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
        repo=repo,
    )

    if not gitp.exists() and ctx.invoked_subcommand is None:
        p = Path(repo).absolute()
        gitp = p / ".git"
        if not gitp.exists():
            print(f"Not a git repository; can't find {gitp.absolute()}")

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
    cfg = ctx.obj
    if cfg.repository.exists():
        if not update:
            print(f'"{ctx.obj.repo}" exists; aborting. Use --update if you wanted to re-use a repository')
            print("(We have not consumed the magic code, you may re-try)")
            return 1

    react_coro(_accept_main, code, ctx.obj.repo, ctx.obj.mailbox_url)


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


async def _git(git_bin, git_p, *args):
    """
    Helper. Run git against the repository with any additional args
    passed on to Git. Return the decoded output as a str.
    """
    out, err, code = await getProcessOutputAndValue(
        git_bin,
        (f"--git-dir={git_p.absolute()}", ) + args,
        env=os.environ,
    )
    if code != 0:
        raise RuntimeError(f"Error:\n{out}\n{err}")
    output = out.decode("utf8").strip()
    return output


async def _setup_remote(reactor, git_bin, repo_p):
    """
    Prepare a given repository for use by git-withme, including
    cleanup.

    :return: the bare repository path (or exception if something went
        wrong)
    """

    # 1. add a remote for "gitwithme"
    remotes = await _git(git_bin, repo_p / ".git", "remote")
    remotes = remotes.split("\n")

    # 1. a) first, check if we already have that remote
    if "gitwithme" in remotes:
        raise RuntimeError(
            f'Aready have a "gitwithme" remote; not overwriting it'
        )

    # 1. b) actually create a bare repo in /tmp or whatever
    from tempfile import TemporaryDirectory
    bare_git = TemporaryDirectory()
    reactor.addSystemEventTrigger("after", "shutdown", bare_git.cleanup)

    bare_git_p = Path(bare_git.name) / repo_p.name
    bare_git_p.mkdir()
    await _git(git_bin, bare_git_p, "init", "--bare")

    # 1. c) add the "gitwithme" remote, pointing at the new bare repo in /tmp
    await _git(git_bin, repo_p / ".git", "remote", "add", "gitwithme", bare_git_p)

    async def cleanup_remote():
        """
        When the host daemon shuts down, we remove the 'gitwithme'
        remote (because it's in temp so will be deleted anyway, even
        if our cleanup code never ran)
        """
        await _git(git_bin, repo_p / ".git", "remote", "remove", "gitwithme")
    reactor.addSystemEventTrigger(
        "before", "shutdown",
        lambda: ensureDeferred(cleanup_remote())
    )

    # 2. We have our local, bare git repo -- new poplate it
    await _git(git_bin, repo_p / ".git", "push", "--all", "gitwithme")
    return bare_git_p


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

    git_bin = shutil.which("git")
    bare_git_p = await _setup_remote(reactor, git_bin, repo_p)

    # XXX plugins will want a way to "run a thing when the wormhole starts"?
    git_port = allocate_tcp_port()

    # 3. Run "git daemon" in the bare git repo so we can export over
    # the network (but only on magic-wormhole)
    gitproto = GitProtocol()
    gitprocess = reactor.spawnProcess(
        gitproto,
        git_bin,
        [
            "git", "daemon",
            "--reuseaddr",
            "--listen=localhost",
            f"--port={git_port}",
            "--export-all",
            f"--base-path={bare_git_p.parent}",
            "--log-destination=stderr",
            "--enable=receive-pack",
            "--enable=upload-pack",
            bare_git_p,
        ],
        env=os.environ,
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown",
        lambda: gitprocess.signalProcess(signal.SIGTERM),
    )
    print(f"Hosting {repo_p} (via bare repo {bare_git_p})")

    # 4. Invite peers

    status = Status()

    async def create_peer():
        peer = Peer()
        status.peers.append(peer)

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
                    "repositories": [repo_p.name],
                }
            },
            dilation=True,
            on_status_update=on_status,
        )
        welcome = await wh.get_welcome()
        peer.url = mailbox_url

        @functools.singledispatch
        def fowl_message(msg):
            print(msg)

        @fowl_message.register(IncomingConnection)
        def _(msg):
            peer.activity.append(Activity(msg.channel_id, reactor.seconds()))

        @fowl_message.register(BytesIn)
        def _(msg):
            peer.total_bytes += msg.bytes

        @fowl_message.register(BytesOut)
        def _(msg):
            peer.total_bytes += msg.bytes

        async def run_peer():
            wh.allocate_code()
            peer.code = await wh.get_code()
            print(f"code: {peer.code}")
            coop = create_coop(reactor, wh)
            coop._status_tracker.add_listener(fowl_message)
            dilated = await coop.dilate()
            channel = await coop.fledge(
                unique_name=repo_p.name,
                local_connect_port=git_port,
            )
            peer.connected = reactor.seconds()
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
            d = ensureDeferred(create_peer())

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
                r.append(f" ({humanize.naturalsize(p.total_bytes)} since {interval}). ")
                if p.activity:
                    act = p.activity[-1]
                    interval = reactor.seconds() - act.started
                    interval = humanize.naturaldelta(interval)
                    interval = f"(last {interval} ago)"
                    lots = "🥳..." if len(p.activity) > 10 else ""
                    recent = p._act_perm[:min(10, len(p.activity))]
                    r.append_text(Text(f"{lots}{recent} {interval}"))
                else:
                    r.append_text(Text("(no activity)"))
            elif p.code is None:
                if p.url is None:
                    r = Text("Connecting...")
                else:
                    r = Text(p.url, style="rgb(0,200,0)")
            else:
                r = Text("Invite code:")
                r.stylize("rgb(0,0,0) on rgb(200,255,0)")
                c = Text(f" {p.code}")
                c.append_text(Text(f'\nrun "git-withme accept {p.code}" to join'))
                r.append(c)
            peers.add_row(r)

        top.add_row(peers)
        return top


    try:
        cmds = Commands(on_command)
        StandardIO(cmds)

        #if 1:
        with Live(get_renderable=render):
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

    def on_status(st):
        print("status:", st)

    wh = wormhole_create(
        "meejah.ca/git-withme",
        mailbox_url,
        reactor,
        versions={
            "git-withme": {
                "features": ["giwime-core"],
            }
        },
        dilation=True,
        on_status_update=on_status,
    )

    wh.set_code(magic_code)
    welcome = await wh.get_welcome()
    await wh.get_code()

    coop = create_coop(reactor, wh)
    dilated = await coop.dilate()

    async def run_peer():
        versions = await wh.get_versions()
        repo_name = versions["git-withme"]["repositories"][0]
        channel = coop.roost(unique_name=repo_name)
        await coop.when_roosted(repo_name)

        repo_url = f"git://localhost:{channel.connect_port}/{repo_name}"
        print(f"cloning {repo_url}")

        # now we are listening, we can clone the remote repo
        out, err, code = await getProcessOutputAndValue(
            git_bin,
            [
                "clone",
                repo_url,
                repo_p,
            ],
            env=os.environ,
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

    reactor.callLater(0, lambda: ensureDeferred(run_peer()))

    await Deferred()
