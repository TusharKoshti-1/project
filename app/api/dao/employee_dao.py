from sqlalchemy.orm import Session
from app.api.vo.login_vo import User
from app.api.vo.employee_vo import Employee
from datetime import datetime


class EmployeeDAO:
    @staticmethod
    def create_employee(db: Session, employee_data: dict) -> Employee:
        new_employee = Employee(
            name=employee_data["name"],
            phone=employee_data["phone"],
            age=employee_data["age"],
            gender=employee_data["gender"],
            department_name=employee_data["department_name"],
            face_file=employee_data["face_file"],
            login_id=employee_data["login_id"],
        )
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        return new_employee

    @staticmethod
    def get_all_employees(db: Session):
        """Fetch all employees from the database."""
        return db.query(Employee).filter(Employee.is_deleted == False).all()

    @staticmethod
    def get_employee_by_name(db: Session, name: str) -> Employee:
        """Fetch a single employee by name."""
        return (
            db.query(Employee)
            .filter(Employee.name == name, Employee.is_deleted == False)
            .first()
        )

    @staticmethod
    def update_last_recognition(db: Session, employee_id: int):
        """Update the last recognized timestamp of an employee."""
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            employee.last_recognized_on = datetime.utcnow()
            db.commit()
            db.refresh(employee)
        return employee

