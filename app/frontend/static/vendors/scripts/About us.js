document.getElementById('employeeForm')?.addEventListener('submit', function(e) {
    e.preventDefault();

    const employee = {
        name: document.getElementById('name').value.trim(),
        job: document.getElementById('job').value.trim(),
        department: document.getElementById('department').value.trim(),
        id: document.getElementById('id').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        image: document.getElementById('image').value.trim() || 'https://via.placeholder.com/150',
        createdAt: new Date().toISOString()
    };

    let employees = JSON.parse(localStorage.getItem('employees')) || [];

    if (employees.some(emp => emp.id === employee.id)) {
        alert('Error: Employee ID already exists!');
        return;
    }
    if (!employee.email.includes('@') || !employee.email.includes('.')) {
        alert('Error: Please enter a valid email address!');
        return;
    }
    if (!employee.phone.match(/^\d{10}$/) && !employee.phone.match(/^\(\d{3}\)\s\d{3}-\d{4}$/)) {
        alert('Error: Please enter a valid phone number (e.g., 1234567890 or (123) 456-7890)!');
        return;
    }

    employees.push(employee);
    localStorage.setItem('employees', JSON.stringify(employees));
    this.reset();
    alert('Employee added successfully!');
    window.location.href = 'Employee.html';
});