from dataclasses import dataclass
from typing import Optional

from pytest_plugins.models.status import ExecutionStatus


@dataclass
class ExecutionData:
    execution_status: ExecutionStatus
    revision: Optional[str]
    pull_request_number: Optional[str]
    merge_request_number: Optional[str]
    execution_start_time: Optional[str] = None
    execution_end_time: Optional[str] = None
    execution_duration_sec: Optional[str] = None
    test_list: Optional[list] = None
