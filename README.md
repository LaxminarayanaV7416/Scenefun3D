## SceneFun3D with GUI


This documentation provides a comprehensive guide to help you efficiently view the SceneFun3D dataset with anotations. It includes detailed descriptions of the data assets, step-by-step instructions for downloading the data, utilizing the project’s tools and libraries, and guidelines for running the evaluation benchmarks.
below are few screenshots of the GUI where you can clearly see how the anotations and pointcloud ares shown from a video to 3D model using Fine-Grained Functionality and Affordance Understanding in 3D Scenes.


![App Screenshot](assets/rgb_laserscan.png)


![App Screenshot2](assets/anotations.png)


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




