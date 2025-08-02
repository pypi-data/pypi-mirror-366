# Git With Me

I have a Git repository and I want to collaborate with others.
We do not have a public server, and do not wish to use existing hosting services.

``git withme`` provides a way for a single host to invite numerous peers with short, one-time secure codes.
The peers connect directly via [Dilated Magic Wormhole channels](https://meejah.ca/blog/fow-wormhole-forward), allowing collaborators to ``git clone git://localhost/<repo-name>``.

![The FOWL Logo, a chicken head, mashed together with 4 Git logos connected by Ethernet cables, suggesting a host and 3 peers](git-withme.svg)

- Git: https://git.sr.ht/~meejah/git-withme
- Releases: https://pypi.org/project/git-withme/


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
    $ git withme
    Hosting /home/meejah/src/gwm (via bare repo /tmp/tmpx_y7q2iq/gitwithme_remote)
     ╭───────────────────────────────────────────────────────────────╮
     │ Hosting: /home/mike/src/git-withme                            │
     │ Git WithMe is now running. To push code to all peers, use:    │
     │     git push gitwithme                                        │
     │ ...and to receive code from a peer who has pushed, use:       │
     │     git pull gitwithme main                                   │
     │ The temporary bare repository we created will be deleted when │
     │ this process is terminated.                                   │
     │                                                               │
     │ N -- create new peer                                          │
     │ Q -- quit, terminate all peers                                │
     ╰───────────────────────────────────────────────────────────────╯
                          Peers
     ┌────────────────────────────────────────────┐
     │ Invite code: 4-quux-foo                    │
     │ run "git-withme accept 4-quux-foo" to join │
     └────────────────────────────────────────────┘

I now send the code ``4-quux-foo`` to my friend.
On their computer, they run the "accept" command (with the secret code) to begin collaborating.

    $ git withme --repo ~/src/gwm accept 4-quux-foo
    welcome ws://relay.magic-wormhole.io:4000/v1
    Peer has connected.
      git:
      git: Cloning into '~/src/gwm'...
      git:
    You can now use normal git commands in ~/src/gwm
    "git pull": update from the host
    "git push": push changes to the host

Meanwhile, I should see something like this on my side:

    ┌──────────────────────────────────────────────────────┐
    │ Connected (for 58 seconds). 🙂 (last 58 seconds ago) │
    └──────────────────────────────────────────────────────┘

As long as both of these shells -- the one on my computer, and the one on my friend's -- remain running they forward end-to-end encrypted traffic between our two computers.
This means that my friend can pull (and push) code; we can use Git somewhat normally.

When the host terminates, the bare repository in $TMPDIR is removed.


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
