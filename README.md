# Admission Prediction API

Run the following commands in order from the directory containing
`admission_prediction_service.tar` and `tests/`.
Docker must be installed and running. Python 3.12 or newer must be available.

## 1. Load the Docker image

```bash
docker load -i admission_prediction_service.tar
```

## 2. Start the service

The tests connect to port 3001 on your machine. The container listens on port 3000.

```bash
docker run -d --name admission-prediction -p 127.0.0.1:3001:3000 admission_prediction_service:latest
```

## 3. Create a test environment and install dependencies

These commands are intended for Linux, WSL, or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 4. Run the tests

Keep the Docker container running while executing the tests.

```bash
pytest -v tests/
```

## 5. Stop and remove the container

After testing:

```bash
docker stop admission-prediction
docker rm admission-prediction
```

## Submission contents

The final submission archive contains:

- `admission_prediction_service.tar`
- `requirements.txt`
- `README.md`
- `tests/`