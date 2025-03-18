from app.config import SessionLocal
from app.api.vo.role_vo import Role

db = SessionLocal()

# Ensure the table is empty before inserting
db.query(Role).delete()
db.commit()

# Insert roles with fixed IDs
admin_role = Role(id=0, role_type="Admin")
employee_role = Role(id=1, role_type="Employee")

db.add(admin_role)
db.add(employee_role)
db.commit()
db.close()

print("Roles inserted successfully!")
