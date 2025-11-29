"""Main entry point for Muker CLI music player."""

import sys
from muker.app import MukerApp


def main():
    """Run the Muker music player application."""
    app = MukerApp()
    app.run()


if __name__ == "__main__":
    main()
