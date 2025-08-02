import random
from attrs import define


activity_viz = "😀😃😄😁🙂😉😍🤩🥸😎🤓"
activity_perms = list()

# itertools.permutations "more correct" but more boring
for _ in range(32):
    this = [
        random.choice(activity_viz)
        for _ in range(10)
    ]
    activity_perms.append("".join(this))



@define
class Status:
    peers: list = []


@define
class Peer:
    url: str = None#"ws://relay.magic-wormhole.io:4000/v1"
    code: str = None
    connected: int = 0  # timestamp of connection
    total_bytes: int = 0;  # bytes in + out
    activity: list = None
    _act_perm: list = None

    def __attrs_post_init__(self):
        global activity_perms
        if not self.activity:
            self.activity = []
        self._act_perm = random.choice(activity_perms)


@define
class Activity:
    id_: str
    started: float
    bytes_in: int = 0
    bytes_out: int = 0
    ended: float = None
