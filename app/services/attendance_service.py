from bson import ObjectId
from bson.errors import InvalidId
from datetime import date as dt_date
from fastapi import HTTPException, status
from app.config.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def mark_attendance(data):
    """
    Mark or update employee attendance
    """
    try:
        # Validate employee_id
        try:
            employee_obj_id = ObjectId(data.employee_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid employee ID format: {data.employee_id}"
            )

        # Check if employee exists
        employee_exists = await db.employees.find_one({"_id": employee_obj_id})
        if not employee_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {data.employee_id} not found"
            )

        # Validate date format
        try:
            year, month, day = map(int, data.date.split("-"))
            dt_date(year, month, day)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format. Expected YYYY-MM-DD, got: {data.date}"
            )

        # Validate status
        if data.status not in ["present", "absent", "leave"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be 'present', 'absent', or 'leave', got: {data.status}"
            )

        # Check existing attendance
        existing = await db.attendance.find_one({
            "employee_id": employee_obj_id,
            "date": data.date
        })

        if existing:
            # Update
            await db.attendance.update_one(
                {"_id": existing["_id"]},
                {"$set": {"status": data.status}}
            )
            logger.info(f"Attendance updated for employee {data.employee_id} on {data.date}")
            return {
                "message": "Attendance updated successfully",
                "employee_id": data.employee_id,
                "date": data.date,
                "status": data.status
            }

        # Insert new
        attendance = {
            "employee_id": employee_obj_id,
            "date": data.date,
            "status": data.status
        }
        result = await db.attendance.insert_one(attendance)
        logger.info(f"Attendance marked for employee {data.employee_id} on {data.date}")
        return {
            "message": "Attendance marked successfully",
            "attendance_id": str(result.inserted_id),
            "employee_id": data.employee_id,
            "date": data.date,
            "status": data.status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in mark_attendance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


async def get_daily_summary(attendance_date: str):
    """
    Get summary of attendance for a specific date
    """
    try:
        # Validate date
        try:
            year, month, day = map(int, attendance_date.split("-"))
            dt_date(year, month, day)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format. Expected YYYY-MM-DD, got: {attendance_date}"
            )

        # Get all employees
        all_employees = await db.employees.find({}).to_list(length=None)
        total_employees = len(all_employees)
        if total_employees == 0:
            return {
                "date": attendance_date,
                "total_employees": 0,
                "present": 0,
                "absent": 0,
                "leave": 0,
                "unmarked": 0,
                "attendance_percentage": 0,
                "message": "No employees registered in the system"
            }

        # Get attendance for the date
        attendance_records = await db.attendance.find({"date": attendance_date}).to_list(length=None)

        # Map employee_id -> status
        attendance_map = {str(record["employee_id"]): record["status"] for record in attendance_records}

        present_count = 0
        absent_count = 0
        unmarked_count = 0

        for emp in all_employees:
            emp_id_str = str(emp["_id"])
            status = attendance_map.get(emp_id_str)
            if status == "present":
                present_count += 1
            elif status == "absent":
                absent_count += 1
            else:
                # No record for this employee
                unmarked_count += 1

        attendance_percentage = round((present_count / total_employees) * 100, 2) if total_employees else 0

        return {
            "date": attendance_date,
            "total_employees": total_employees,
            "present": present_count,
            "absent": absent_count,
            "unmarked": unmarked_count,
            "attendance_percentage": attendance_percentage
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_daily_summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    

async def get_attendance_by_date(attendance_date: str):
    records = await db.attendance.find(
        {"date": attendance_date}
    ).to_list(None)

    # Convert to dictionary: { employee_id: status }
    attendance_map = {}

    for record in records:
        attendance_map[str(record["employee_id"])] = record["status"]

    return attendance_map

