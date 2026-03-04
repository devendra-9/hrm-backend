from fastapi import APIRouter
from app.schemas.employee_schema import Employee
from app.config.database import db
from app.services.employee_service import create_employee_service, get_all_employees, delete_employee_service, update_employee_service, get_employee_by_id_service

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/create")
async def create_employee(employee: Employee):
    return await create_employee_service(employee)

@router.get("/allUser")
async def get_employees():
     return await get_all_employees()

@router.delete("/delete/{id}")
async def delete_employee(id: str):
    return await delete_employee_service(id)

@router.put("/{id}")
async def update_employee(id: str, employee: Employee):
    return await update_employee_service(id, employee)

@router.get("/{id}")
async def get_employee_by_id(id: str):
    return await get_employee_by_id_service(id)