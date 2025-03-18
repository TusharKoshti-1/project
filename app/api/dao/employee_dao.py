# app/api/dao/employee_dao.py
from sqlalchemy.orm import Session
from app.api.vo.employee_vo import Employee
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmployeeDAO:
    @staticmethod
    def create_employee(db: Session, employee_data: dict):
        employee = Employee(
            name=employee_data["name"],
            phone=employee_data["phone"],
            age=employee_data["age"],
            gender=employee_data["gender"],
            department_name=employee_data["department_name"],
            face_image_path=employee_data["face_image_path"],
            login_id=employee_data["login_id"],
            is_deleted=employee_data.get("is_deleted", False),
            created_on=employee_data.get("created_on", datetime.utcnow()),
            modified_on=employee_data.get("modified_on", datetime.utcnow()),
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def get_all_employees(db: Session):
        employees = db.query(Employee).filter(Employee.is_deleted == False).all()
        logger.debug(f"Retrieved {len(employees)} employees from database")
        return employees

    @staticmethod
    def update_last_recognition(db: Session, employee_id: int):
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            logger.warning(f"Employee with id {employee_id} not found")
            return None
        employee.last_recognized_on = datetime.utcnow()
        employee.modified_on = datetime.utcnow()
        db.commit()
        db.refresh(employee)
        logger.info(f"Updated last_recognized_on for employee_id: {employee_id}")
        return employee
