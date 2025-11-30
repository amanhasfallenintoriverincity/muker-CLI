"""Check terminal capabilities."""

import sys
import os

print(f"Platform: {sys.platform}")
print(f"stdout.isatty(): {sys.stdout.isatty()}")
print(f"stderr.isatty(): {sys.stderr.isatty()}")
print(f"stdin.isatty(): {sys.stdin.isatty()}")
print(f"TERM: {os.environ.get('TERM', 'NOT SET')}")
print(f"COLORTERM: {os.environ.get('COLORTERM', 'NOT SET')}")
print(f"TERM_PROGRAM: {os.environ.get('TERM_PROGRAM', 'NOT SET')}")

# Check if we can create a Textual app
try:
    from textual.app import App
    from textual.widgets import Static

    print("\n[DEBUG] Creating test Textual app...")

    class TestApp(App):
        def compose(self):
            print("  [DEBUG] compose() CALLED!")
            yield Static("Test")

    app = TestApp()
    print("[DEBUG] App created, checking driver...")
    print(f"  Driver class: {type(app.driver).__name__ if hasattr(app, 'driver') else 'No driver yet'}")

    print("\n[DEBUG] Calling run_test()...")
    # Use run_test() instead of run()
    async def test():
        async with app.run_test() as pilot:
            print("  [DEBUG] run_test() working!")
            await pilot.pause()

    import asyncio
    asyncio.run(test())
    print("[DEBUG] run_test() completed!")

except Exception as e:
    print(f"\n[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()
