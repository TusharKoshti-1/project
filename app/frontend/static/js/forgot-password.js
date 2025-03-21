// Show error messages
function showError(message) {
  const messageBox = document.getElementById("message-box");
  messageBox.style.color = "red"; // Error messages in red
  messageBox.textContent = message; // Show the error message
}

// Show success messages
function showSuccess(message) {
  const messageBox = document.getElementById("message-box");
  messageBox.style.color = "green"; // Success messages in green
  messageBox.textContent = message; // Show the success message
}

// Validate forgot password form
async function validateForgotPassword(event) {
  event.preventDefault();

  const emailInput = document.getElementById("email");
  const email = emailInput.value.trim();
  const loginButton = event.target.querySelector("button[type='submit']");

  loginButton.disabled = true; // Disable button to prevent multiple submissions

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showError("Please enter a valid email address.");
    loginButton.disabled = false;
    return;
  }

  const API_URL = "http://127.0.0.1:8000/auth/forgot-password";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "ngrok-skip-browser-warning": "true",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    const result = await response.json();

    if (response.ok) {
      showSuccess(result.message || "Password reset email sent successfully.");
      window.location.href = "/reset-password"; // Redirect to the reset password page
      document.getElementById("forgot-password-form").reset();
    } else {
      throw new Error(result.detail || "An error occurred while processing your request.");
    }
  } catch (error) {
    showError(error.message);
    console.error("Error:", error);
  } finally {
    loginButton.disabled = false; // Re-enable the button
  }
}
