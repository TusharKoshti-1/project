from sqlalchemy.orm import Session
from app.api.vo.login_vo import User
from app.api.vo.employee_vo import Employee

class EmployeeDAO:
    @staticmethod
    def create_employee(db: Session, employee_data: dict) -> Employee:
        new_employee = Employee(
            name=employee_data['name'],
            age=employee_data['age'],
            gender=employee_data['gender'],
            department_name=employee_data['department_name'],
            face_file=employee_data['face_file'],
            login_id=employee_data['login_id']
        )
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        return new_employee