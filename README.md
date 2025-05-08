# SceneFun3D Viewer with GUI

This project provides a lightweight and interactive GUI to explore the **SceneFun3D** dataset with fine-grained annotations and 3D pointcloud visualization. Built using Python and [viser](https://pypi.org/project/viser/), this tool enables users to inspect how functional elements in indoor scenes—such as knobs, handles, and buttons—are annotated and visualized using frame-by-frame RGB-D video data converted into a dataset of images (both regular and depth).

SceneFun3D is a novel dataset designed to push the boundaries of functionality-driven 3D scene understanding by introducing:
- Over **14.8k annotated** functional interaction points across **710** high-resolution indoor scenes.
- **Affordance segmentation**, **task-driven grounding**, and **3D motion estimation**.
- **Natural language task descriptions** aligned with actionable elements in the scene.

> 📁 We are currently using the example dataset provided by the official SceneFun3D paper, where each image frame is paired with depth data from a video capture.

---

## 🔍 Features

- 🧠 Fine-grained 3D functionality and affordance visualization
- 📸 Point cloud rendering of image and depth data
- 📌 Annotation overlays and affordance masks
- 🌐 Task-based interactions through motion and language cues (Working on it!)
- ⚙️ Easily extendable with additional SceneFun3D scenes (Need to provide the dataset that contains both the images and thier depth captures)

---

## 📸 GUI Screenshots

Visualizations rendered using the provided RGB-D frames from SceneFun3D:

![RGB & Laser Scan View](assets/rgb_laserscan.png)

![Annotation Overlay](assets/anotations.png)

---

This project uses [`uv`](https://github.com/astral-sh/uv), a fast Python package manager and environment tool, to manage dependencies and virtual environments. The app can also be run inside a Docker container.
### 🚀 Getting Started

### 1. Install `uv`

To install `uv`, you need Rust and Python 3.8+. You can install `uv` via the following command:

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

Or if you're using Homebrew (macOS/Linux):

```bash
brew install astral-sh/uv/uv
```

Verify installation:

```bash
uv --version
```

### 2. Create a Virtual Environment

Use `uv` to create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # Linux/macOS

# OR for Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Lock and Sync Dependencies

Install dependencies using `uv`:

```bash
# If you already have a pyproject.toml and want to lock dependencies
uv lock

# Sync dependencies to the virtual environment
uv sync
```

If you want to add new dependencies:

```bash
uv pip install <package-name>
uv pip freeze > requirements.txt  # Optional: keep requirements.txt in sync
uv lock  # Update the lockfile
```

---

## 🐳 Running with Docker

### 1. Build Docker Image

Build the Docker image:

```bash
docker build -t your-app-name .
```

### 2. Run Docker Container

Run the server inside the container:

```bash
docker run -p 8080:8080 -v ./data:/usr/src/scenefun3d/data your-app-name
```

This maps port `8080` from the container to your local machine. You can now access the server at `http://localhost:8080`.

---

## 📂 Project Structure (example)

```bash
.
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── app.py
├── data_downloader
│   └── download_utils
│   └── data_asset_donwload.py
└── README.md
```

---

## ✅ Notes

- Always use `uv lock` after changing dependencies to keep `uv.lock` in sync.
- `uv sync` ensures the virtual environment matches the lockfile exactly.
- Consider using `.env` files or Docker secrets for managing sensitive config.
- if you are using Mac with ARM chips like M1, M2, .. then use the below docker options to build and run since we are having open3d installation we cant run docker over arm, so we need to take advantage of buildx
```bash
docker buildx create --use

docker buildx build --platform linux/amd64 -t your-app-name . --load

docker run -p 8080:8080 -v ./data:/usr/src/scenefun3d/data your-app-name
```
---




