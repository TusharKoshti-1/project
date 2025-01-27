document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    // const expiration =urlParams.get('exp');

    if (expiration) {
      const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
      // console.log(currentTime + 'this is current time');
      // console.log(expiration + 'this is expiration time');
      if (currentTime > expiration) {
        document.body.innerHTML = `
          <div style="text-align: center; padding: 20px;">
            <h1>Link Expired</h1>
            <p>This reset password link has expired. Please request a new one.</p>
          </div>
        `;
        return; // Stop further execution
      }
    }

    // Proceed to handle the form submission
    const form = document.getElementById("reset-password-form");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const token = urlParams.get("token");
      const password = document.getElementById("new-password").value;

      if (!token || !password) {
        alert("Invalid request. Missing token or password.");
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