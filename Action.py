from abc import abstractmethod
from enum import Enum, unique
from threading import Thread, Event


@unique
class Type(Enum):
    none = 0
    updatable = 1
    runnable = 2


class StoppableThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self._stop = Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class Action:
    def __init__(self, action, action_stop, name: str):
        self._name = name
        self._action_stop = action_stop
        self._action = action

    def name(self):
        return self._name

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def stopped(self):
        pass


class RunAction(Action):
    def __init__(self, action, action_stop, name: str):
        super().__init__(action, action_stop, name)

        def target():
            self._action()
            self.__action.stop()

        self.__action = StoppableThread(target=target)
        self.__action.start()

    def stop(self):
        self._action_stop()
        self.__action.stop()

    def stopped(self):
        return self.__action.stopped()


class UpdAction(Action):
    def __init__(self, action, action_stop, name: str):
        super().__init__(action, action_stop, name)
        self.__stopped = False

    def update(self, snd_nick: str, public: bool, text: str):
        if not self.__stopped: self._action(snd_nick, public, text)

    def stop(self):
        if not self.stopped(): self._action_stop()
        self.__stopped = True

    def stopped(self):
        return self.__stopped


class NoneAction(Action):
    def __init__(self):
        super().__init__(None, None, "none")

    def stop(self):
        pass

    def stopped(self):
        return True
