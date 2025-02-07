from datetime import datetime
from typing import TypedDict


class TimeEntry(TypedDict):
    iteration: int
    timestamp: datetime

    function_file: str
    function_name: str

    old_cc: int
    new_cc: int
    old_prj_avg_cc: float
    new_prj_avg_cc: float
    old_fn_count: int
    new_fn_count: int
    old_avg_nloc: float
    new_avg_nloc: float
    sent_tokens: int
    received_tokens: int
