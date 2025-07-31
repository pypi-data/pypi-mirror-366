import threading
import time
import argparse
from pynput import keyboard
from . import constants
from . import utils

def main():
    parser = argparse.ArgumentParser(description="Volume Control based on Key Presses")
    parser.add_argument("--max", type=int, default=constants.max_volume, help="Maximum volume level (default: 30)")
    parser.add_argument("--min", type=int, default=constants.min_volume, help="Minimum volume level (default: 10)")
    parser.add_argument("--decay", type=float, default=constants.decay, help="Continuous decay rate when lps is 0 (default: 0.5)")
    parser.add_argument("--magnitude", type=float, default=constants.change_magnitude, help="Change magnitude per key press (default: 0.1)")
    parser.add_argument("--log", type=bool, default=False, help="Enable logging of volume changes")

    args = parser.parse_args()

    global max_volume, min_volume, continuous_decay, change_magnitude, log_enabled
    max_volume = args.max
    min_volume = args.min
    continuous_decay = args.decay
    change_magnitude = args.magnitude
    log_enabled = args.log
    current_volume = utils.get_true_volume()

    print(f"Thud | Max: {max_volume} — Min: {min_volume} — Decay: {continuous_decay} — Mag: {change_magnitude} — Log: {log_enabled}")

    lps = 0
    lock = threading.Lock()

    def on_press(key):
        nonlocal lps
        with lock:
            lps += 1

    def lps_counter():
        nonlocal lps, current_volume
        while True:
            time.sleep(1)
            with lock:
                if log_enabled:
                    print(f"Letters per second: {lps}, Current volume: {current_volume}                     ", end='\r', flush=True)
                if lps == 0:
                    current_volume = utils.change_volume(current_volume, -continuous_decay, min_volume, max_volume)
                else:
                    current_volume = utils.change_volume(current_volume, lps * change_magnitude, min_volume, max_volume)
                lps = 0

    try:
        threading.Thread(target=lps_counter, daemon=True).start()
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()