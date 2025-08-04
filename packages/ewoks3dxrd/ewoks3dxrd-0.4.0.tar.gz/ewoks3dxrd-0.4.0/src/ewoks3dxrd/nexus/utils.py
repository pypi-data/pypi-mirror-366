from __future__ import annotations
from pathlib import Path
from typing import Tuple
import h5py
from silx.io.utils import DataUrl
import posixpath


def group_exists(filename: str | Path, data_group_path: str) -> bool:
    if isinstance(filename, str):
        filename = Path(filename)
    if not filename.exists():
        return False

    with h5py.File(filename, "r") as file:
        if data_group_path in file:
            return True
    return False


def check_throw_write_data_group_url(
    overwrite: bool, filename: str | Path, data_group_path: str
):
    if not overwrite and group_exists(
        filename=filename, data_group_path=data_group_path
    ):
        raise ValueError(
            f"""Data group '{data_group_path}' already exists in {filename},
            Set `overwrite` to True if you wish to overwrite the existing data group.
            """
        )


def get_data_url_paths(data_url_as_str: str) -> Tuple[str, str]:
    data_url = DataUrl(data_url_as_str)
    file_path = data_url.file_path()
    data_path = data_url.data_path()
    if not Path(file_path).exists():
        raise FileNotFoundError(f"{file_path} not found")
    if data_path is None or not group_exists(file_path, data_path):
        raise KeyError(f"{data_path} not found in {file_path}")

    return file_path, data_path


def get_entry_name(process_group_path: str):
    return posixpath.dirname(process_group_path)
