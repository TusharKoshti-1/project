async function validateLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const API_URL = "http://127.0.0.1:8000/auth/login";

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
      const data = await response.json();
      console.log("Data:", data);
      console.log("Token:", data.access_token); // Fixed from data.token to data.access_token
      sessionStorage.setItem("user", data.access_token);
      console.log("Role ID:", data.role_id);

      // Redirect based on role_id
      if (data.role_id === 0) {
        window.location.href = "/dashboard";
      } else if (data.role_id === 1) {
        window.location.href = "/employee/dashboard";
      } else {
        alert("Unknown user role");
        // Handle unexpected role ID here if needed
      }
    } else {
      const errorData = await response.json();
      alert(errorData.message || "Invalid email or password");
    }
  } catch (error) {
    alert("Error connecting to the API: " + error.message);
    console.error(error);
  }
}