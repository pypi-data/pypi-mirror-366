# snsr

A playful Python-based "screensaver" that randomly moves your mouse and simulates key presses to keep your screen active.

## Features

- Moves the mouse to random screen positions.
- Simulates random key presses.
- Keeps your system from going idle.
- Lightweight and easy to use.

## Usage

### Using `uv`

If you're using `uv`, you can run the `snsr` command directly without needing to activate a virtual environment first. Just use `uvx`:

```bash
uvx snsr
```

### Using pip

You can install `snsr` using `pip`:

```bash
pip install snsr
snsr
```

It will:

* Move your mouse to random points on the screen
* Press a random key (`a`, `s`, `d`, `f`, `j`, `k`, `l`)
* Repeat this process every few seconds

### To Stop

Press `Ctrl+C` in the terminal to exit.

## Notes

* Ensure your OS allows simulated input events from Python scripts.
* Useful for keeping your machine awake during long tasks (e.g., rendering, builds, meetings).

## Disclaimer

This project is intended for educational or personal use only. Use responsibly and respect your organization's policies regarding input automation.

---

MIT License © 2025
