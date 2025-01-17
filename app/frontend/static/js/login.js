// login.js

// Function to handle login
async function validateLogin(event) {
  event.preventDefault(); // Prevent default form submission

  // Collect email and password from the form
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  // API endpoint
  const API_URL = "https://exact-notable-tadpole.ngrok-free.app/users/login";

  try {
      // Make the POST request to the API
      const response = await fetch(API_URL, {
          method: "POST",
          headers: {
              "ngrok-skip-browser-warning":"true",
              "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password}),
      });

      // Process the response
      if (response.ok) {
          const data = await response.json(); // Assuming API returns JSON
          alert("Login successful!");
          console.log("Token:", data.token); // Log token for development
          // Save token securely, e.g., in sessionStorage
          sessionStorage.setItem("token", data.token);
          // Redirect to dashboard
          window.location.href = "/dashboard";
      } else {
          const errorData = await response.json(); // Extract error details
          alert(errorData.message || "Invalid email or password");
      }
  } catch (error) {
      // Handle network or other errors
      alert("Error connecting to the API: " + error.message);
      console.error(error);
  }
}
