# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Salon smart mirror application: detects faces via camera, identifies returning customers, and generates AI hairstyle previews using Stable Diffusion inpainting. Customers can browse hairstyles, preview them on their live image, and book appointments. Built with Python/PyQt5/SQLite for desktop development, targeting Jetson Orin Nano for production deployment.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt          # Desktop (macOS/Linux)
pip install -r requirements-jetson.txt   # Jetson Orin Nano

# Copy and configure environment
cp .env.example .env

# Run
python main.py
```

Database tables are auto-created and hairstyle catalog is auto-seeded on first run.

## Architecture

### Layer Structure

- **`main.py`** — Entry point. `SmartMirrorController` wires everything together: config → DB → services → inference backend → UI screens → worker threads → event loop.
- **`config.py`** — Platform detection (`detect_platform()` checks `/etc/nv_tegra_release` for Jetson) and environment-driven configuration with platform-specific defaults (resolution, face detection model, inference device).
- **`core/`** — Business logic, no UI dependencies.
  - `hardware/` — Abstract `CameraBackend` and `InferenceBackend` with factory functions (`create_camera()`, `create_inference_backend()`) that select implementations based on detected platform.
  - `face/` — Face detection and recognition using dlib/face_recognition.
  - `hair/` — Hair segmentation and Stable Diffusion inpainting pipeline.
  - `services/` — CRUD service layer for domain entities (customers, appointments, stylists).
- **`ui/`** — PyQt5 interface.
  - `screens/` — Eight screens managed by QStackedWidget: Mirror → Recognition → Profile → Menu → Browser → Preview → Appointment → History.
  - `threads/` — Three worker threads: `CameraThread` (~30 FPS capture), `FaceDetectionThread` (~5 FPS detection), `HairGenerationThread` (on-demand SD inference). All communicate with UI via Qt signals.
  - `widgets/` — Reusable UI components.
- **`db/`** — SQLAlchemy ORM models (`models.py`), database init/session management (`engine.py`), hairstyle catalog seeding (`seed.py`).
- **`assets/`** — QSS stylesheets.

### Key Patterns

- **Factory pattern** for platform-specific camera and inference backends (CPU/MPS/CUDA).
- **Qt signal/slot** for thread-safe communication between worker threads and UI — no blocking calls on the main thread.
- **Lazy model loading** — AI models (SD inpainting, face detection) loaded on first use in worker threads, not at startup.
- **Face encoding persistence** — Customer face encodings stored in DB (via msgpack) for fast recognition without re-enrollment.

### Database Models

`Customer` (with face encodings/photos), `Stylist`, `HairstyleCategory`, `Hairstyle` (with SD prompts), `CustomerFavorite`, `Appointment`. All defined in `db/models.py` using SQLAlchemy declarative base.

## Platform Variants

| Setting | Desktop macOS | Desktop Linux | Jetson Orin Nano |
|---|---|---|---|
| Camera | OpenCV | OpenCV | Jetson CSI |
| Inference | MPS/CPU | CPU | CUDA |
| Resolution | 640×480 | 640×480 | 1280×720 |
| Face model | HOG | HOG | CNN |

## Testing

No test suite exists yet. The `tests/` directory contains only `__init__.py`.
