"""Main entry point for Muker CLI music player."""

import sys
import os

# CRITICAL: Set environment variables BEFORE any other imports
os.environ['TERM'] = 'xterm-256color'
os.environ['COLORTERM'] = 'truecolor'

# Enable ANSI on Windows
if sys.platform == 'win32':
    os.system('')  # Enables ANSI escape sequences on Windows 10+

# Redirect debug output to file
debug_file = open('muker_debug.log', 'w', encoding='utf-8')
original_print = print
def debug_print(*args, **kwargs):
    original_print(*args, **kwargs, file=debug_file, flush=True)
    original_print(*args, **kwargs)  # Also print to console

# Replace print globally
import builtins
builtins.print = debug_print

print("[DEBUG] Environment configured for Windows terminal support")
print("[DEBUG] Debug output will be saved to muker_debug.log")

import traceback
from muker.app import MukerApp


def main():
    """Run the Muker music player application."""
    try:
        print("[DEBUG] Starting Muker application...")
        app = MukerApp()
        print("[DEBUG] MukerApp created")
        print("[DEBUG] Calling app.run()...")

        # Check if terminal is interactive
        if not sys.stdout.isatty():
            print("[ERROR] Not running in an interactive terminal!")
            print("[ERROR] Please run this in a proper terminal (Windows Terminal, PowerShell, or cmd)")
            sys.exit(1)

        # Force interactive mode (not headless)
        print("[DEBUG] Starting in interactive mode...")
        app.run(headless=False)
        print("[DEBUG] app.run() returned normally")
    except KeyboardInterrupt:
        print("[DEBUG] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] Failed to start application: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
