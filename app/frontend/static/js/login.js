async function validateLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

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
      const data = await response.json();
      alert("Login successful!");
      console.log("Token:", data.token);
      sessionStorage.setItem("user", data.access_token);
      window.location.href = "/dashboard";
    } else {
      const errorData = await response.json();
      alert(errorData.message || "Invalid email or password");
    }
  } catch (error) {
    alert("Error connecting to the API: " + error.message);
    console.error(error);
  }
}
