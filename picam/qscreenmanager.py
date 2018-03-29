from collections import deque

from kivy.uix.screenmanager import ScreenManager, Screen


class QScreenManager(ScreenManager):
    """
    a subclass of ScreenManager that keeps a simple back stack.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stack = deque()

    def on_current(self, instance, value):
        """
        when a new screen is set, put it on the queue
        :param instance:
        :param value:
        :return:
        """
        super().on_current(instance, value)

        # only keep one
        if value in self.stack:
            self.stack.remove(value)

        # None clears history
        if value is None:
            self.stack.clear()
        else:
            self.stack.append(value)

    def pop(self):
        """
        pop the current screen off and load the previous one
        :return:
        """
        old = self.stack.pop()
        if self.stack:
            self.current = self.stack.pop()
        else:
            self.current = None
        return old

    def toggle(self, value):
        if self.current == value:
            return self.pop()
        else:
            self.current = value


def _test():
    q = QScreenManager()
    q.add_widget(Screen(name='a'))
    q.add_widget(Screen(name='b'))

    q.current = 'a'

    q.current = 'b'

    q.pop()

    print('now', q.current)
    print(q.stack)

    q.pop()

    print('now', q.current)
    print(q.stack)


if __name__ == '__main__':
    _test()
