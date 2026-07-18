import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from capture     import wait_for_still_frame
from reconstruct import contour_to_stl
from viewer      import display_model_spinning  # <-- Imported viewer

OUTPUT_DIR = os.getcwd()


def main():
    print("=" * 60)
    print("  EDP  -  Draw-to-3D  (Tripo AI powered)")
    print("=" * 60)
    print(f"  Output : {OUTPUT_DIR}")
    print("  Quit   : Q in the camera window")
    print("-" * 60)
    print()
    print("  Tips for best results:")
    print("  • Draw on BRIGHT WHITE paper under good lighting")
    print("  • Use a thick BLACK marker for outlines")
    print("  • Fill the guide box with your drawing")
    print("  • Move your hand fully out of frame before capture")
    print()

    # ── Step 1: capture ───────────────────────────────────────────
    print("[1/2] Waiting for drawing ...")
    try:
        frame = wait_for_still_frame(label="DRAWING")
    except KeyboardInterrupt:
        print("\nAborted.")
        return

    # ── Step 2: reconstruct ───────────────────────────────────────
    stamp    = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUTPUT_DIR, f"model_{stamp}.glb")

    print("\n[2/2] Sending to Tripo AI for 3D reconstruction ...")
    try:
        saved = contour_to_stl(frame, out_path)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        traceback.print_exc()
        return

    print()
    print("=" * 60)
    print(f"  Done!  Model saved to:")
    print(f"  {saved}")
    print("=" * 60)
    print()

    # ── Step 3: auto-view ─────────────────────────────────────────
    try:
        display_model_spinning(saved)
    except Exception as e:
        print(f"\n[ERROR] Viewer failed to launch: {e}")


if __name__ == "__main__":
    main()