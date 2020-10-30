#!/usr/bin/env python3

"""

use with ~/.gitconfig

    [credential]
            helper = cache
            helper = cache --timeout 7200

    [user]
            email = your-email
            name = your-git hub account

make first a push and enter your credits before running this

start as backgroud job call with e.g.

./auto_push.py [sleep_sec] &

"""

import sys
import os
import time


# print(sys.argv)

sleep_delay_min = 30 if len(sys.argv) == 1 else int(sys.argv[1])

sleep_delay_sec = sleep_delay_min * 60

print("auto push interval", sleep_delay_min, "min")


def exec(cmd):
    print("exe", cmd)
    with os.popen(cmd) as p:
        resp = p.read()
        print(resp)


while True:

    print("sleeping")

    time.sleep(sleep_delay_sec)

    for cmd in [
        "git push",
        "git push --tags",
    ]:
        exec(cmd)
