import cv2
import numpy as np
import time

# ── settings ──────────────────────────────────────────────────────────────────
STILL_SECONDS   = 3
MOTION_THRESH   = 25
MOTION_MIN_AREA = 500
CAMERA_INDEX    = 1
FRAME_WIDTH     = 1280
FRAME_HEIGHT    = 720
# ─────────────────────────────────────────────────────────────────────────────


def open_camera():
    for backend in [cv2.CAP_DSHOW, cv2.CAP_ANY]:   # CAP_DSHOW = best on Windows
        cap = cv2.VideoCapture(CAMERA_INDEX, backend)
        if cap.isOpened():
            break
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {CAMERA_INDEX}.")
    return cap


def _has_motion(prev_gray, curr_gray):
    diff  = cv2.absdiff(prev_gray, curr_gray)
    _, th = cv2.threshold(diff, MOTION_THRESH, 255, cv2.THRESH_BINARY)
    th    = cv2.dilate(th, None, iterations=2)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return any(cv2.contourArea(c) > MOTION_MIN_AREA for c in cnts)


def _overlay(frame, label, still_since, active):
    disp = frame.copy()
    h, w = disp.shape[:2]
    cv2.rectangle(disp, (0, 0), (w, 65), (0, 0, 0), -1)

    if active and still_since is not None:
        elapsed = time.time() - still_since
        remain  = max(0.0, STILL_SECONDS - elapsed)
        bar_w   = int(w * elapsed / STILL_SECONDS)
        cv2.rectangle(disp, (0, 55), (bar_w, 65), (0, 220, 80), -1)
        txt   = f"[{label}]  Hold still … {remain:.1f}s"
        color = (0, 220, 80)
    else:
        txt   = f"[{label}]  Show drawing, move hand away"
        color = (200, 200, 200)

    cv2.putText(disp, txt, (15, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)
    cv2.putText(disp, "Q = quit", (w - 160, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1, cv2.LINE_AA)

    # guide box: centre 60% of frame
    bx, by = int(w * 0.20), int(h * 0.10)
    bw, bh = int(w * 0.60), int(h * 0.80)
    cv2.rectangle(disp, (bx, by), (bx+bw, by+bh), (80, 80, 200), 1)
    cv2.putText(disp, "keep drawing inside this box", (bx+4, by+20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 80, 200), 1, cv2.LINE_AA)
    return disp


def wait_for_still_frame(label="VIEW"):
    cap = open_camera()
    print(f"  [camera] Ready – waiting for still {label} frame …")

    ret, prev = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Cannot read from camera.")

    prev_g      = cv2.GaussianBlur(cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    still_since = None
    captured    = None

    cv2.namedWindow(f"EDP – {label}", cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            curr_g = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            motion = _has_motion(prev_g, curr_g)
            prev_g = curr_g

            if motion:
                still_since = None
            else:
                if still_since is None:
                    still_since = time.time()
                if time.time() - still_since >= STILL_SECONDS:
                    captured = frame.copy()
                    print(f"  [camera] {label} captured!")
                    break

            cv2.imshow(f"EDP – {label}", _overlay(frame, label, still_since, still_since is not None))
            # key = cv2.waitKey(1) & 0xFF
            # if key in (ord('q'), 27):
            #     cap.release()
            #     cv2.destroyAllWindows()
            #     raise KeyboardInterrupt("User quit.")
            key = cv2.waitKey(1) & 0xFF

            # Press 's' to capture manually
            if key == ord('s'):
                captured = frame.copy()
                print(f"  [camera] {label} manually captured!")
                break

            # Quit
            if key in (ord('q'), 27):
                cap.release()
                cv2.destroyAllWindows()
                raise KeyboardInterrupt("User quit.")

    finally:
        cap.release()
        cv2.destroyAllWindows()

    return captured