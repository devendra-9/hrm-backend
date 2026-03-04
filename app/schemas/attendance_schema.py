from pydantic import BaseModel
from bson import ObjectId
from typing import Literal

class EmployeeAttendance(BaseModel):
    employee_id: str
    date: str
    status: Literal["present", "absent", "unmarked"]

    model_config = {
        "arbitrary_types_allowed": True
    }