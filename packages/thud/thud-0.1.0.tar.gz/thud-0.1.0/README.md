# Thud

Reactively change volume based on typing speed to induce flow state

Usage:

```bash
python thud.py [--max MAX_VOLUME] [--min MIN_VOLUME] [--decay DECAY_RATE] [--magnitude CHANGE_MAGNITUDE] [--log True|False]
```

**Arguments:**

- `--max`: Maximum volume level (default: 30)
- `--min`: Minimum volume level (default: 10)
- `--decay`: Continuous decay rate when lps is 0 (default: 0.5)
- `--magnitude`: Change magnitude per key press (default: 0.1)
- `--log`: Enable logging of volume changes (default: False)
