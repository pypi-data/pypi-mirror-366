from __future__ import annotations

import os

import requests


def http_download_file(url: str, dst_path: str, chunk: int = 1 << 16) -> None:
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with requests.get(url, timeout=None, stream=True) as r:
        r.raise_for_status()
        with open(dst_path, "wb") as f:
            for block in r.iter_content(chunk):
                f.write(block)
