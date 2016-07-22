from Action import NoneAction

def users(names: set, masters: set) -> map:
    _users = {name: User(name) for name in names}
    for master in masters:
        if master not in _users: _users[master] = User(master)
        _users[master].master = True
    return _users


class User:
    def __init__(self, name: str):
        self.name = name
        self.master = False
        self.hello = False
        self.memory = None
        self.action = NoneAction()
