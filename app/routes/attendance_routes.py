from fastapi import APIRouter
from app.schemas.attendance_schema import EmployeeAttendance
from app.services.attendance_service import mark_attendance, get_daily_summary, get_attendance_by_date
from datetime import date

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/mark")
async def mark_employee_attendance(data: EmployeeAttendance):
    return await mark_attendance(data)


@router.get("/summary/{attendance_date}")
async def daily_summary(attendance_date: str):
    """
    Get attendance summary for a specific date
    Returns counts of present, absent, leave, etc.
    """
    return await get_daily_summary(attendance_date)

@router.get("/by-date/{attendance_date}")
async def attendance_by_date(attendance_date: str):
    """
    Returns employee-wise attendance for a specific date
    """
    return await get_attendance_by_date(attendance_date)