from __future__ import annotations
import os
from typing import Literal
import numpy as np
import h5py
from silx.gui import qt


def get_omega_array(
    file_path: str,
    omega_motor: str,
    scan_id: str,
) -> np.ndarray:
    with h5py.File(file_path, "r") as hin:
        omega_angles = hin[f"{scan_id}/measurement/{omega_motor}"]
        omega_array = omega_angles[()]
        return omega_array


def get_unique_instrument_keys(master_file: str, groups: list[str]) -> list[str]:
    unique_keys = set()
    with h5py.File(master_file) as hin:
        for group in groups:
            instrument_path = f"{group}/instrument"
            if instrument_path in hin:
                group_keys = hin[instrument_path].keys()
                unique_keys.update(group_keys)

    return sorted(unique_keys)


def find_possible_scan_numbers(master_file: str) -> list[int]:
    parent_dir = os.path.dirname(master_file)
    candidates = []
    for d in os.listdir(parent_dir):
        if d.lower().startswith("scan") and os.path.isdir(os.path.join(parent_dir, d)):
            digits = "".join(filter(str.isdigit, d))
            if digits:
                candidates.append(int(digits))
    return candidates


def ask_confirmation_to_repeat_segmentation() -> Literal["continue", "show", "cancel"]:
    """Asks the user what to do when segmentation parameters have not changed
    Returns:
    str: One of "continue", "show", or "cancel"
    """
    msg_box = qt.QMessageBox()
    msg_box.setIcon(qt.QMessageBox.Warning)
    msg_box.setWindowTitle("Segmentation Already Run")
    msg_box.setText("You've already run a full segmentation with these parameters.")
    msg_box.setInformativeText("What would you like to do?")

    repeat_btn = msg_box.addButton("Repeat anyway", qt.QMessageBox.AcceptRole)
    show_btn = msg_box.addButton("Show previous results", qt.QMessageBox.ActionRole)
    cancel_btn = msg_box.addButton("Cancel", qt.QMessageBox.RejectRole)
    msg_box.exec()

    clicked = msg_box.clickedButton()
    if clicked == repeat_btn:
        return "continue"
    elif clicked == show_btn:
        return "show"
    elif clicked == cancel_btn:
        return "cancel"
