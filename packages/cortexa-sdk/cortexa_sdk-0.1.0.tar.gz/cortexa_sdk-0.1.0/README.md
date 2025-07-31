<!--
Copyright (c) 2025 Vortek Inc. and Tuanliu (Hainan Special Economic Zone) Technology Co., Ltd.
All rights reserved.
本软件版权归 Vortek Inc.（除中国大陆地区）与 湍流（海南经济特区）科技有限责任公司（中国大陆地区）所有。
请根据许可协议使用本软件。
-->
# Cortexa SDK

This package provides a small client for downloading datasets from a Cortexa server.

## Installation

```bash
pip install cortexa-sdk
```

## Configuration

You can configure the SDK using:
- Function parameters
- A config file at `~/.cortexa/config.json`
- Environment variables

Example config file:
```json
{
  "api_key": "your-api-key",
  "base_url": "https://your-cortexa-server/api",
  "dataset_dir": "~/datasets"
}
```

Environment variables:
- `CORTEXA_API_KEY`
- `CORTEXA_BASE_URL`
- `CORTEXA_DATASET_DIR`

## Usage

```python
from cortexa_sdk import download_dataset, ExportType

# Parameters override config which override environment variables
path = download_dataset("DATASET_ID", export_type=ExportType.JSON)
print("dataset saved to", path)
```

The dataset download function creates a server-side task and polls its
progress, printing updates like `dataset task abc123 progress: 42%` until
the final archive is ready.

### Examples

**Using environment variables**

```bash
export CORTEXA_API_KEY="TOKEN"
export CORTEXA_BASE_URL="https://api.example.com/api/v1"
python - <<'PY'
from cortexa_sdk import download_dataset
download_dataset("dataset123")
PY
```

**Using a config file**

```python
from cortexa_sdk import download_dataset, ExportType
path = download_dataset("dataset123", export_type=ExportType.COCO)
print(path)
```

**Overriding everything with parameters**

```python
from cortexa_sdk import download_dataset, ExportType

download_dataset(
    "dataset123",
    export_type=ExportType.COCO,
    api_key="TOKEN",
    base_url="https://api.example.com/api/v1",
    download_dir="/tmp/datasets",
)
```

Environment variables:

- `CORTEXA_API_KEY` – API key used when no value is provided via parameter or config file.
- `CORTEXA_BASE_URL` – Base URL of the Cortexa server.
- `CORTEXA_DATASET_DIR` – Default dataset download directory.
- `CORTEXA_CONFIG` – Path to a JSON config file (defaults to `~/.cortexa/config.json`).

`config.json` can contain `api_key`, `base_url` and `dataset_dir`.
Example `config.json`:

```json
{
  "api_key": "YOUR_API_KEY",
  "base_url": "https://api.example.com/api/v1",
  "dataset_dir": "/data/datasets"
}
```

Configuration resolution order: parameters override values from the config file, which override environment variables.

## Releasing to PyPI

1. Ensure that `setuptools`, `build` and `twine` are installed:

```bash
pip install --upgrade setuptools build twine
```

2. Build the package:

```bash
python -m build
```

3. Upload to PyPI:

```bash
twine upload dist/*
```

4. Tag and push the release in git:
```bash
git tag v<version>
git push --tags
```

You can test uploads using [TestPyPI](https://test.pypi.org/) by passing the repository URL to `twine`.