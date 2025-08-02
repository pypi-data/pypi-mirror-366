# Git With Me

I have a Git repository and I want to collaborate with others.
We do not have a public server, and do not wish to use existing hosting services.

``git withme`` provides a way for a single host to invite numerous peers with short, one-time secure codes.
The peers connect directly via [Dilated Magic Wormhole channels](https://meejah.ca/blog/fow-wormhole-forward), allowing collaborators to ``git clone git://localhost/<repo-name>``.

![The FOWL Logo, a chicken head, mashed together with 4 Git logos connected by Ethernet cables, suggesting a host and 3 peers](git-withme.svg)


## Motivational Example

I have created a Git repository:

    $ mkdir ~/src/gwm
    $ cd ~/src/gmw
    $ echo "Git With Me" > README
    $ git add README
    $ git commit -m "begin"

Now chatting with a friend, I invite them to collaborate.
In its own shell, I run the hosting service; this will connect to the public Magic Wormhole mailbox server.

    $ cd ~/src/gwm
    $ git withme host
    Connected to ws://mailbox.magic-wormhole.io:4001/v1
    Hosting /home/meejah/src/gwm on git://localhost:9418/gwm
    Ready for peers.
    Press "return" to create invite:
    Invite code: 4-quux-foo
    Waiting for peer...

I now send the code ``4-quux-foo`` to my friend.
On their computer, they run the "accept" command (with the secret code) to begin collaborating.

    $ git withme accept 4-quux-foo ~/src/gwm
    Connected to ws://mailbox.magic-wormhole.io:4001/v1
    Listening on port 9418
    Repository available at:
       git clone git://localhost/gwm
    $ cd ~/src
    $ git clone git://localhost/gwm

Meanwhile, I should see something like this on my side:

    ...
    Press "return" to create invite:
    Invite code: 4-quux-foo
    Waiting for peer...connected.
    Remote listening on port 9418
    Peer 1 has cloned the repository.

As long as both of these shells -- the one on my computer, and the one on my friend's -- remain running they forward end-to-end encrypted traffic between our two computers.
This means that my friend can pull (and push) code; we can use Git somewhat normally.

Note that this is a little different than GitHub and similar services.
My friend is _directly_ pushing to my repository; there is no "bare" repository (e.g. on the host side).
Git doesn't like when you're both on the same branch in this situation.

To alleviate this, you may create your own ``git init --bare /tmp/foo`` repository, and run ``git withme host /tmp/foo`` to host it out of that instead.
You'd then also ``git remote add -f collab file:///tmp/foo`` (or similar) in your original local copy so you have a remote to push to / pull from.
This workflow is more like that of hosted services.

    XXX: do we want to have an option to just do this for you? maybe that's the default?


# One-Time Codes

Malicious actors (even the Mailbox server, if malicious or compromised) get a single guess at breaking the code; if they are wrong, the mailbox is destroyed and the legitimate recipient will notice (they get a "crowded" error).
This gives us an identity-free, long-lived connection -- so long as we keep our shells running, we can put our laptops to sleep or otherwise move networks (note that if **both** sides are disconnected for more than 10 minutes, the connection will be terminated).


# How to Install

``git withme`` is a Git extension written in Python.
To "install" it, the ``git-withme`` script needs to be somewhere on your ``PATH`` (for ``git withme`` to work).

I recommend using a "virtualenv" or "venv" to install into, or you can try ``pip install --user git-withme`` if that works for your platform.
For a "venv":

    $ python -m venv ~/gwm-venv
    $ ~/gwm-venv/bin/pip install git+https://git.sr.ht/~meejah/git-withme
    $ export ~/gwm-venv/bin:$PATH
    $ git withme --help


# TODO

- A ``--read-only`` or similar option to disable push access by peers
- better UX (e.g. let "host" invite more than one at once, show more details, etc)
- ``git withme accept`` side; doesn't do a lot currently (can basically just be ``fowl``) but symmetry and future expansion are nice
- tie in Dilation feedback / updates UX through from fowl, for experimenting
