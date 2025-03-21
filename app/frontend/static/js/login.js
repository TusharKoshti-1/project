document.addEventListener("DOMContentLoaded", () => {
  // Toggle password visibility
  const togglePassword = document.querySelector(".toggle-password");
  if (togglePassword) {
      togglePassword.addEventListener("click", () => {
          const passwordInput = document.getElementById("password");
          const icon = togglePassword.querySelector("i");

          if (passwordInput.type === "password") {
              passwordInput.type = "text";
              icon.classList.remove("fa-eye");
              icon.classList.add("fa-eye-slash");
          } else {
              passwordInput.type = "password";
              icon.classList.remove("fa-eye-slash");
              icon.classList.add("fa-eye");
          }
      });
  } else {
      console.error("Toggle password element not found");
  }

  // Validate login form
  async function validateLogin(event) {
      event.preventDefault();

      const emailInput = document.getElementById("email");
      const passwordInput = document.getElementById("password");
      const roleInput = document.querySelector('input[name="options"]:checked');
      const submitButton = event.target.querySelector("button[type='submit']");

      submitButton.disabled = true; // Disable button to prevent multiple submissions

      const email = emailInput.value.trim();
      const password = passwordInput.value.trim();
      const role = roleInput ? roleInput.value : null;

      // Basic validation
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          alert("Please enter a valid email address.");
          submitButton.disabled = false;
          return;
      }

      if (!role) {
          alert("Please select a role (Manager or Employee).");
          submitButton.disabled = false;
          return;
      }

      const API_URL = "http://127.0.0.1:8000/auth/login";

      try {
          const response = await fetch(API_URL, {
              method: "POST",
              headers: {
                  "ngrok-skip-browser-warning": "true",
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ email, password, role_id: parseInt(role) }), // Include role_id
          });

          if (response.ok) {
              const data = await response.json();
              console.log("Data:", data);
              console.log("Token:", data.access_token);
              sessionStorage.setItem("user", data.access_token);
              console.log("Role ID:", data.role_id);

              // Redirect based on role_id
              if (data.role_id === 0) {
                  window.location.href = "/dashboard";
              } else if (data.role_id === 1) {
                  window.location.href = "/employee/dashboard";
              } else {
                  alert("Unknown user role");
              }
          } else {
              const errorData = await response.json();
              alert(errorData.message || "Invalid email or password");
          }
      } catch (error) {
          alert("Error connecting to the API: " + error.message);
          console.error("Error:", error);
      } finally {
          submitButton.disabled = false; // Re-enable the button
      }
  }

  // Attach event listener to form
  const form = document.getElementById("login-form");
  if (form) {
      form.addEventListener("submit", validateLogin);
  } else {
      console.error("Form with ID 'login-form' not found");
  }
});