import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def save(name, obj):
    with open(os.path.join(DATA, name), "w") as f:
        json.dump(obj, f, indent=2)


def load_profile():
    return load("profile.json")


def load_assumptions():
    return load("assumptions.json")


def load_state():
    try:
        return load("state.json")
    except FileNotFoundError:
        from .model import default_state
        state = default_state(load_profile())
        save("state.json", state)
        return state


def save_state(state):
    save("state.json", state)
