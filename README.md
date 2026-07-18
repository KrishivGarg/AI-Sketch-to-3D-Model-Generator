# AI Sketch to 3D Model Generator

Convert a hand-drawn sketch into an interactive 3D model using computer vision and AI. The application captures a stable webcam image, removes its background, reconstructs it into a 3D model using the Tripo3D API, and automatically displays the generated model in a rotating 3D viewer.

## Features

*  Automatic webcam capture with motion detection
*  Manual capture option
*  AI-powered background removal using `rembg`
*  Image-to-3D reconstruction via Tripo3D API
*  Automatic GLB model download
*  Interactive 3D preview using Open3D
*  End-to-end automated workflow

## How It Works

1. Show your sketch to the webcam.
2. The application waits until the image is still.
3. Background is removed automatically.
4. The processed image is uploaded to the Tripo3D API.
5. AI reconstructs the image into a 3D model.
6. The generated GLB model is downloaded.
7. The model opens in an interactive 3D viewer.

## Project Structure

```text
capture.py        Webcam capture with motion detection
reconstruct.py    Background removal & Tripo3D reconstruction
viewer.py         Open3D model viewer
check.py          Reconstruction utility/testing
```

## Technologies Used

* Python
* OpenCV
* Open3D
* Pillow
* rembg
* NumPy
* Requests
* Tripo3D API

## Installation

```bash
git clone https://github.com/yourusername/AI-Sketch-to-3D.git
cd AI-Sketch-to-3D
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Future Improvements

* Local AI-based 3D reconstruction
* Support for multiple input images
* Mesh editing and smoothing
* STL/OBJ/FBX export
* Gradio or Streamlit web interface
* Texture generation and editing

## License

This project is intended for educational and research purposes.
