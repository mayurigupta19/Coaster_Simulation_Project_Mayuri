# COASTER 3D — Roller Coaster Simulation

An interactive 3D Computer Graphics project made with Python, GLFW and PyOpenGL. It renders a closed, undulating roller-coaster track, steel rails, cross ties, support pillars, a moving multi-car train, wheels, trees and a ground platform.

## Features
- Continuous 3D train movement along a closed track with changing elevation.
- Each car follows the track tangent, so the train turns and pitches with the track.
- Orbit camera: drag with the left mouse button; scroll to zoom.
- On-ride camera: press `C` to switch to a moving first-person ride view.
- Pause/resume with `Space`; adjust speed with `+` and `-`.
- Toggle support pillars with `S`; reset orbit camera with `R`; hide/show compact HUD title with `H`.
- Arrow keys also adjust the orbit camera; `Esc` exits.

## Requirements
- macOS with a desktop session and OpenGL support (tested design target: MacBook with Apple Silicon using macOS system OpenGL compatibility).
- Python 3.10 or newer.

## Run on macOS
Open Terminal in this folder and run:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 main.py
```

If `python3` points to Python 3.14 and a dependency fails to install, use a Python 3.12 installation and repeat the commands with `python3.12`.

## Controls
| Input | Action |
|---|---|
| Left mouse drag | Orbit camera |
| Mouse wheel | Zoom in/out |
| `C` | Switch orbit / on-ride camera |
| `Space` | Pause / resume train |
| `+` / `-` | Increase / decrease train speed |
| Arrow keys | Adjust orbit camera |
| `S` | Toggle support pillars |
| `R` | Reset orbit camera |
| `H` | Toggle HUD title details |
| `Esc` | Exit |

## Project structure
- `main.py` — complete 3D scene, geometry, animation, camera and input handling.
- `requirements.txt` — Python dependencies.
- `PROJECT_REPORT.md` — project overview and graphics concepts.
- `VIVA_QUESTIONS.md` — viva preparation questions and answers.

## Notes
This is an educational visualization, not a physically validated amusement-ride engineering simulator. Track geometry and train speed are stylized for clear 3D animation. OpenGL is deprecated by Apple but remains available through macOS compatibility contexts; future macOS versions may change this support.
