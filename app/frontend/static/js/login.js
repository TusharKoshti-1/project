// Function to handle login via email/password
async function validateLogin(event) {
    event.preventDefault(); // Prevent default form submission
  
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
  
    // API endpoint
    const API_URL = "https://exact-notable-tadpole.ngrok-free.app/users/login";
  
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "ngrok-skip-browser-warning": "true",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
  
      if (response.ok) {
        const data = await response.json();  // Assuming JSON response with access_token
        alert("Login successful!");
        console.log("Token:", data.token);  // Log token for development
        sessionStorage.setItem("token", data.access_token);  // Store token in session
        window.location.href = "/dashboard";  // Redirect to dashboard
      } else {
        const errorData = await response.json();
        alert(errorData.message || "Invalid email or password");
      }
    } catch (error) {
      alert("Error connecting to the API: " + error.message);
      console.error(error);
    }
  }
  