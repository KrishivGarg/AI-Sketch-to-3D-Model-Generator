import os
import time
import requests
import cv2
import numpy as np
from PIL import Image
from rembg import remove
from io import BytesIO

TRIPO_API_KEY    = "tsk_FPtU1DOSOUugiNmS00oUF0XA6hJHJd1uCX_N5tmeFJ8"  
FOREGROUND_RATIO = 0.85
API_BASE         = "https://api.tripo3d.ai/v2/openapi"


def _prepare_image(frame: np.ndarray) -> Image.Image:
    """
    Remove background with AI (rembg) and place subject on
    a clean white 512x512 canvas ready for Tripo.
    """
    # BGR → RGB → PIL
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)

    # AI background removal
    removed = remove(pil)   # returns RGBA with transparent background

    size   = 512
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    thumb  = removed.copy()
    thumb.thumbnail(
        (int(size * FOREGROUND_RATIO), int(size * FOREGROUND_RATIO)),
        Image.LANCZOS
    )
    ox = (size - thumb.width)  // 2
    oy = (size - thumb.height) // 2
    canvas.paste(thumb, (ox, oy), thumb)

    canvas.save("debug_sent_to_tripo.png")
    print("  [AI] Debug image saved: debug_sent_to_tripo.png")

    return canvas


def _upload_image(pil_image: Image.Image) -> str:
    """
    Upload image to Tripo via multipart/form-data.
    Returns image_token string.
    """
    print("  [tripo] Uploading image ...")

    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    buf.seek(0)

    resp = requests.post(
        f"{API_BASE}/upload",
        headers={"Authorization": f"Bearer {TRIPO_API_KEY}"},
        files={"file": ("drawing.png", buf, "image/png")}  # multipart form
    )

    if not resp.ok:
        print(f"  [tripo] Upload error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    data  = resp.json()
    token = data["data"]["image_token"]
    print(f"  [tripo] Image token: {token}")
    return token


def _create_task(image_token: str) -> str:
    """
    Submit image-to-3D task to Tripo.
    Returns task_id string.
    """
    print("  [tripo] Submitting reconstruction task ...")

    resp = requests.post(
        f"{API_BASE}/task",
        headers={
            "Authorization": f"Bearer {TRIPO_API_KEY}",
            "Content-Type":  "application/json",
        },
        json={
            "type": "image_to_model",
            "file": {
                "type":       "png",
                "file_token": image_token,
            },
        }
    )

    if not resp.ok:
        print(f"  [tripo] Task error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    task_id = resp.json()["data"]["task_id"]
    print(f"  [tripo] Task ID: {task_id}")
    return task_id


def _poll_task(task_id: str) -> str:
    print("  [tripo] Reconstructing 3D model ", end="", flush=True)

    while True:
        resp = requests.get(
            f"{API_BASE}/task/{task_id}",
            headers={"Authorization": f"Bearer {TRIPO_API_KEY}"}
        )
        resp.raise_for_status()
        data   = resp.json()["data"]
        status = data["status"]

        if status == "success":
            print(" done!")
            print("  [tripo] Full output:", data.get("output"))  # ← show actual keys
            url = data["output"]["pbr_model"] or data["output"].get("model") or list(data["output"].values())[0]
            return url

        elif status in ("failed", "cancelled"):
            raise RuntimeError(f"Tripo task {status}")
        else:
            print(".", end="", flush=True)
            time.sleep(3)


def _download_model(url: str, output_path: str) -> str:
    """
    Download the GLB file from Tripo and save it.
    Returns the saved file path.
    """
    print("  [tripo] Downloading model ...")

    r = requests.get(url, stream=True)
    r.raise_for_status()

    glb_path = output_path.replace(".stl", ".glb")
    with open(glb_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    kb = os.path.getsize(glb_path) / 1024 
    print(f"  [tripo] Model saved: {glb_path} ({kb:.0f} KB)")
    return glb_path


def contour_to_stl(frame: np.ndarray, output_path: str) -> str:
    """
    Entry point called by main.py.
    Accepts a BGR frame (H x W x 3) from the webcam.
    Runs: background removal → upload → reconstruct → download GLB.
    """
    print("\n  [AI] Preparing image ...")
    pil_img = _prepare_image(frame)

    token   = _upload_image(pil_img)
    task_id = _create_task(token)
    url     = _poll_task(task_id)
    path    = _download_model(url, output_path)
    return path
