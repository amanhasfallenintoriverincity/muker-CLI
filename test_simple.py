"""Simplest possible Textual app."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static


class SimpleApp(App):
    def compose(self) -> ComposeResult:
        print("[DEBUG] SimpleApp.compose() called!")
        yield Header()
        yield Static("Hello from SimpleApp!")
        yield Footer()

    async def on_mount(self):
        print("[DEBUG] SimpleApp.on_mount() called!")


if __name__ == "__main__":
    print("[DEBUG] Creating SimpleApp...")
    app = SimpleApp()
    print("[DEBUG] Running SimpleApp...")
    app.run()
    print("[DEBUG] SimpleApp finished")
