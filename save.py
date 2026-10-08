"""Each step stores its numbers in runs/stepN.json, so a later reader (or the film) does not retype them."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def save(step, **numbers):
    os.makedirs(os.path.join(HERE, 'runs'), exist_ok=True)
    with open(os.path.join(HERE, 'runs', 'step%d.json' % step), 'w') as f:
        json.dump(numbers, f)
