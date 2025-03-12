
document.getElementById('employeeForm').addEventListener('submit', function(e) {
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

// The following functions would typically go in Employee.html
function displayEmployees() {
    const employeeGrid = document.getElementById('employeeGrid');
    const employees = JSON.parse(localStorage.getItem('employees')) || [];

    if (!employeeGrid) return; // Only run if on dashboard page

    if (employees.length === 0) {
        employeeGrid.innerHTML = '<p style="text-align: center; color: var(--secondary-color);">No employees found. Add some employees!</p>';
        return;
    }

    employeeGrid.innerHTML = '';
    employees.forEach((employee, index) => {
        const card = document.createElement('div');
        card.className = 'employee-card';
        card.innerHTML = `
            <img src="${employee.image}" alt="${employee.name}" class="employee-image">
            <div class="employee-info">
                <h3>${employee.name}</h3>
                <p><strong>Job:</strong> ${employee.job}</p>
                <p><strong>Department:</strong> ${employee.department}</p>
                <p><strong>ID:</strong> ${employee.id}</p>
                <p><strong>Email:</strong> ${employee.email}</p>
                <p><strong>Phone:</strong> ${employee.phone}</p>
                <p><strong>Added:</strong> ${new Date(employee.createdAt).toLocaleDateString()}</p>
            </div>
            <div class="employee-actions">
                <button class="action-btn edit-btn" data-index="${index}">Edit</button>
                <button class="action-btn delete-btn" data-index="${index}">Delete</button>
            </div>
        `;
        employeeGrid.appendChild(card);
    });

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => editEmployee(e.target.dataset.index));
    });
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => deleteEmployee(e.target.dataset.index));
    });
}

function editEmployee(index) {
    const employees = JSON.parse(localStorage.getItem('employees')) || [];
    const employee = employees[index];
    
    const newName = prompt('Enter new name:', employee.name);
    const newJob = prompt('Enter new job:', employee.job);
    if (newName && newJob) {
        employees[index].name = newName.trim();
        employees[index].job = newJob.trim();
        localStorage.setItem('employees', JSON.stringify(employees));
        displayEmployees();
    }
}

function deleteEmployee(index) {
    if (confirm('Are you sure you want to delete this employee?')) {
        const employees = JSON.parse(localStorage.getItem('employees')) || [];
        employees.splice(index, 1);
        localStorage.setItem('employees', JSON.stringify(employees));
        displayEmployees();
    }
}

window.onload = displayEmployees;
window.addEventListener('storage', displayEmployees);
