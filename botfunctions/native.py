# This file is used for a number of smaller functions.

import random

def mrfreeze():
    with open('config/mrfreezequotes', 'r') as f:
        return random.choice(f.read().strip().split('\n'))
