document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const form = document.getElementById("reset-password-form");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const token = urlParams.get("token");
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    // Validate passwords match
    if (password !== confirmPassword) {
      document.getElementById("message-box").innerHTML =
        `<p style="color: red;">Passwords do not match.</p>`;
      return;
    }

    // Ensure token is present
    if (!token) {
      document.getElementById("message-box").innerHTML =
        `<p style="color: red;">Invalid request. Missing token.</p>`;
      return;
    }

    try {
      const response = await fetch("https://exact-notable-tadpole.ngrok-free.app/users/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({ token, password }),
      });

      const result = await response.json();

      if (response.ok) {
        document.getElementById("message-box").innerHTML =
          `<p style="color: green;">${result.message || "Password reset successful."}</p>`;
        form.reset(); // Clear the form
      } else {
        throw new Error(result.detail || "An error occurred while resetting the password.");
      }
    } catch (error) {
      document.getElementById("message-box").innerHTML =
        `<p style="color: red;">${error.message}</p>`;
    }
  });
});
