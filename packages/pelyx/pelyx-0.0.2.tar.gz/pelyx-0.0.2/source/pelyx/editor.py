import textual
from textual.app import App, ComposeResult
from textual.widgets import Header, TextArea, Footer

class Editor(textual.app.App):
    TITLE = 'Pelyx'
    SUB_TITLE = 'a terminal text editor'

    def __init__(self, path: str):
        super().__init__()
        with open(path) as file:
            self.text = file.read()

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextArea.code_editor(self.text)
        yield Footer()
