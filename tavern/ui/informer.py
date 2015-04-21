from tavern.view.show_console import display_text


class Informer(object):
    def __init__(self, console):
        self.console = console
        self.text = ''

    def receive(self, event):
        self.text = event.get('data')
        print(self.text)

    def display(self):
        display_text(self.console.console, self.text, 0, 1)

    def __repr__(self):
        return "Feedback"
