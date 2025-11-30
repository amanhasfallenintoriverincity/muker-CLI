"""Test if Textual works."""

from textual.app import App
from textual.widgets import Static


class TestApp(App):
    def compose(self):
        print("[DEBUG] TestApp compose() called!")
        yield Static("Hello World!")


if __name__ == "__main__":
    print("[DEBUG] Starting test app...")
    app = TestApp()
    print("[DEBUG] Running test app...")
    app.run()
    print("[DEBUG] Test app finished")
