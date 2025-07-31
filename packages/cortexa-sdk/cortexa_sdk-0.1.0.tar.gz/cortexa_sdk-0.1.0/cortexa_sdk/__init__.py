# Copyright (c) 2025 Vortek Inc. and Tuanliu (Hainan Special Economic Zone) Technology Co., Ltd.
# All rights reserved.
# 本软件版权归 Vortek Inc.（除中国大陆地区）与 湍流（海南经济特区）科技有限责任公司（中国大陆地区）所有。
# 请根据许可协议使用本软件。
import os
import json
import time
import requests
from enum import Enum
from pathlib import Path

__all__ = ["CortexaClient", "download_dataset", "ExportType"]

DEFAULT_CONFIG_PATH = Path.home() / ".cortexa" / "config.json"
DEFAULT_DATASET_DIR = Path.home() / ".cortexa" / "datasets"


class ExportType(str, Enum):
    """Export type values supported by the server."""

    JSON = "JSON"
    YOLO = "YOLO"
    COCO = "COCO"


class CortexaClient:
    """Simple client for downloading datasets.

    Configuration values are resolved in the following order:
    1. Function parameters
    2. Values from the JSON config file
    3. Environment variables

    Environment variables fall back to built-in defaults if not set.
    """

    def __init__(self, api_key=None, base_url=None, config_file=None):
        # Parameter > config > environment
        config_file = config_file or os.getenv(
            "CORTEXA_CONFIG", str(DEFAULT_CONFIG_PATH)
        )
        config_path = Path(config_file)
        config = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

        self.api_key = api_key or config.get("api_key") or os.getenv("CORTEXA_API_KEY")
        self.base_url = (
            base_url or config.get("base_url") or os.getenv("CORTEXA_BASE_URL")
        )
        if not self.base_url:
            raise ValueError(
                "base_url must be provided via parameter, config file or environment variable CORTEXA_BASE_URL"
            )
        self._config = config

    def _resolve_dir(self, kind: str, override_path: str | None) -> Path:
        env_map = {
            "dataset": "CORTEXA_DATASET_DIR",
        }
        default_map = {
            "dataset": DEFAULT_DATASET_DIR,
        }
        config_key_map = {
            "dataset": "dataset_dir",
        }
        path = (
            override_path
            or self._config.get(config_key_map[kind])
            or os.getenv(env_map[kind], str(default_map[kind]))
        )
        p = Path(path).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _api_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Perform an HTTP request against the Cortexa API."""
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        resp = requests.request(method, url, headers=self._headers(), **kwargs)
        resp.raise_for_status()
        return resp

    def _headers(self):
        headers = {}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    def download_dataset(
        self,
        dataset_id: str,
        export_type: ExportType = ExportType.JSON,
        download_dir: str | None = None,
    ) -> Path:
        """Download a dataset by creating a download task and polling for completion."""
        target_dir = self._resolve_dir("dataset", download_dir)

        # Create download task
        resp = self._api_request(
            "POST",
            "dataset/download-task-create",
            json={"dataset_id": dataset_id, "export_type": export_type.value},
        )
        if resp.json().get("code") != 202:
            raise RuntimeError(
                f"Failed to create download task: {resp.json().get('message', 'Unknown error')}"
            )
        print(f"Created download task for dataset {dataset_id}")
        task_id = resp.json()["data"]["task_id"]
        print(f"Created dataset download task {task_id} for {dataset_id}")

        zip_url = None
        last_progress = -1
        is_uploading = False
        last_status = None
        while not zip_url:
            time.sleep(2)
            poll = self._api_request(
                "GET",
                "asset/download-task",
                params={"task_id": task_id},
            )
            data = poll.json().get("data", {})
            if not data:
                raise RuntimeError(f"Download task polling failed: {poll.json()}")
            progress = data.get("progress", 0)
            status = data.get("status")
            if progress != last_progress or status != last_status:
                msg = f"dataset task {task_id} status: {status} progress: {progress}%"
                print(msg)
                last_progress = progress
                last_status = status
            if status == "FAILED":
                raise RuntimeError(data.get("error_message", "Task failed"))
            if progress == 100 and status == "PROCESSING" and not is_uploading:
                print(
                    "Download to backend server completed successfully, waiting for uploading to DB. If it takes too long, please check the (celery worker) server logs."
                )
                is_uploading = True
            zip_url = data.get("zip_url")

        print(f"Downloading dataset from {zip_url}")
        resp = requests.get(zip_url, stream=True)
        resp.raise_for_status()
        out_file = target_dir / f"{dataset_id}.zip"
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        with open(out_file, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = int(downloaded * 100 / total)
                        print(f"downloaded {pct}%", end="\r")
        print(f"Saved dataset to {out_file}")
        return out_file


def download_dataset(
    dataset_id: str,
    export_type: ExportType = ExportType.JSON,
    api_key: str | None = None,
    base_url: str | None = None,
    download_dir: str | None = None,
    config_file: str | None = None,
) -> Path:
    client = CortexaClient(api_key=api_key, base_url=base_url, config_file=config_file)
    return client.download_dataset(dataset_id, export_type, download_dir)


"""
example of download-task response:
{
    "code": 200,
    "message": "ok",
    "data": {
        "task_id": "688a18832c948e929e4ff7ce",
        "user_id": "6842952c1dd811d8c78194d6",
        "status": "PROCESSING",
        "asset_ids": [
            "687465d516475541e6f35018",
            "6887257b4c386cd71343fa26",
            "687465d116475541e6f35011",
            "687465d016475541e6f35010",
            "688725784c386cd71343fa1f",
            "688725db4c386cd71343fa2b",
            "6887257a4c386cd71343fa23",
            "687465d216475541e6f35012",
            "688725db4c386cd71343fa2d",
            "6887257f4c386cd71343fa29",
            "687465d316475541e6f35014",
            "6887257f4c386cd71343fa2a",
            "687465cf16475541e6f3500f",
            "6887257b4c386cd71343fa24",
            "688725784c386cd71343fa20",
            "6887257a4c386cd71343fa22",
            "6887257b4c386cd71343fa25",
            "688725de4c386cd71343fa34",
            "6887257c4c386cd71343fa27",
            "688726544c386cd71343fa36",
            "688725dc4c386cd71343fa2f",
            "688725dd4c386cd71343fa30",
            "688725dd4c386cd71343fa31",
            "688725e04c386cd71343fa35",
            "687465d616475541e6f35019",
            "688725de4c386cd71343fa32",
            "688725de4c386cd71343fa33",
            "688725db4c386cd71343fa2c",
            "687465d316475541e6f35016",
            "6887257d4c386cd71343fa28",
            "687465d316475541e6f35015",
            "688725784c386cd71343fa21",
            "688725dc4c386cd71343fa2e"
        ],
        "asset_hash": "4dfca091a924f416795879bfb121e682",
        "task_type": "DATASET_DOWNLOAD",
        "annotation_format": "COCO",
        "total_files": 33,
        "processed_files": 33,
        "progress": 100,
        "zip_filename": "zjx-测试数据集7",
        "zip_filesize": null,
        "zip_url": null,
        "zip_uri": null,
        "error_message": null,
        "expires_at": null,
        "created_at": 1753880707616,
        "updated_at": 1753880945748,
        "is_acknowledged": false,
        "acknowledged_at": null
    }
}
"""
