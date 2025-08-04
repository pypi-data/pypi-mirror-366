from __future__ import annotations

import traceback


def format_exception(error: Exception) -> str:
    return "\n".join(traceback.format_exception(error))
