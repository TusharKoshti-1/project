document.addEventListener('DOMContentLoaded', () => {
    const employeeForm = document.getElementById('employee-form');
  
    employeeForm.addEventListener('submit', async (e) => {
      e.preventDefault();  // Prevent the page from refreshing on form submission
  
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const role_id = 0; 
  
      const formData = {
        email: email,
        password: password,
        role_id : role_id
      };
  
      try {
        // Send a POST request to the API
        const response = await fetch('https://4bfb-103-176-11-62.ngrok-free.app/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'ngrok-skip-browser-warning': 'true',
            },
            body: JSON.stringify(formData),
        });
    
        if (!response.ok) {
            throw new Error(`Failed to add employee. Status: ${response.status}`);
        }
    
        const responseData = await response.json();
        alert(`Employee added successfully! ${responseData.message}`);
        employeeForm.reset();
    } catch (error) {
        console.error('Error:', error);
        if (error.response) {
            const errorData = await error.response.json(); // Handle error response body, if any.
            console.error('Error response body:', errorData);
        } else {
            alert('An error occurred while adding the employee.');
        }
    }
    });
  });