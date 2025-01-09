// Show the modal
function showModal() {
    document.getElementById('id01').style.display = 'block';
  }
  
  // Hide the modal
  function hideModal() {
    document.getElementById('id01').style.display = 'none';
  }
  
  // Close the modal when clicking outside of it
  window.onclick = function(event) {
    const modal = document.getElementById('id01');
    if (event.target == modal) {
      hideModal();
    }
  }
   function validateLogin() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorElement = document.getElementById('error');
            errorElement.textContent = '';

            const passwordRegex = /[@&]/;

            if (!username) {
                errorElement.textContent = 'Email is required.';
                return;
            }

            if (!passwordRegex.test(password)) {
                errorElement.textContent = 'Password must contain at least one @ or & character.';
                return;
            }

            alert('Login successful!');
        }