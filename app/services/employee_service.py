from app.config.database import db
from fastapi import HTTPException
from bson import ObjectId

async def create_employee_service(employee):
    try:
        result = await db.employees.insert_one(employee.dict())
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_all_employees():
    try:
        employees = []
        async for emp in db.employees.find():
            emp["_id"] = str(emp["_id"])
            employees.append(emp)
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def delete_employee_service(id: str):
    try:
        result = await db.employees.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {"message": "Employee deleted successfully"}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
async def get_employee_by_id_service(id: str):
    try:
        employee = await db.employees.find_one({"_id": ObjectId(id)})

        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        employee["_id"] = str(employee["_id"])
        return employee

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
async def update_employee_service(id: str, employee):
    try:
        result = await db.employees.update_one(
            {"_id": ObjectId(id)},
            {"$set": employee.dict()}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {"message": "Employee updated successfully"}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")