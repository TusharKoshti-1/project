// Ensure DOM is fully loaded before running code
document.addEventListener("DOMContentLoaded", () => {
  // Show modal popup
  function showModal(message, isSuccess) {
      return new Promise((resolve) => {
          const modal = document.getElementById("popup-modal");
          const modalContent = document.getElementById("modal-content");
          const modalMessage = document.getElementById("modal-message");
          const modalOk = document.getElementById("modal-ok");

          // Check if elements exist
          if (!modal || !modalContent || !modalMessage || !modalOk) {
              console.error("Modal elements not found in DOM");
              resolve(); // Resolve promise to avoid hanging, but log error
              return;
          }

          modalMessage.textContent = message;
          modalContent.className = "modal-content " + (isSuccess ? "success" : "error");
          modal.style.display = "flex";

          modalOk.onclick = () => {
              modal.style.display = "none";
              resolve();
          };
      });
  }

  // Show error messages
  function showError(message) {
      return showModal(message, false);
  }

  // Show success messages
  function showSuccess(message) {
      return showModal(message, true);
  }

  // Validate forgot password form
  async function validateForgotPassword(event) {
      event.preventDefault();

      const emailInput = document.getElementById("email");
      const email = emailInput.value.trim();
      const submitButton = event.target.querySelector("button[type='submit']");

      submitButton.disabled = true; // Disable button to prevent multiple submissions

      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          await showError("Please enter a valid email address.");
          submitButton.disabled = false;
          return;
      }

      const API_URL = "http://127.0.0.1:8000/auth/forgot-password"; // Updated to match your endpoint

      try {
          const response = await fetch(API_URL, {
              method: "POST",
              headers: {
                  "ngrok-skip-browser-warning": "true", // If using ngrok
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ email }),
          });

          const result = await response.json();

          if (response.ok) {
              // Store email in sessionStorage before redirecting
              sessionStorage.setItem("resetEmail", email);
              await showSuccess(result.message || "Password reset email sent successfully.");
              window.location.href = "/otp_verify"; // Redirect after OK
              document.getElementById("forgot-password-form").reset();
          } else {
              throw new Error(result.detail || "An error occurred while processing your request.");
          }
      } catch (error) {
          await showError(error.message);
          console.error("Error:", error);
      } finally {
          submitButton.disabled = false; // Re-enable the button
      }
  }

  // Attach event listener to form
  const form = document.getElementById("forgot-password-form");
  if (form) {
      form.addEventListener("submit", validateForgotPassword);
  } else {
      console.error("Form with ID 'forgot-password-form' not found");
  }
});