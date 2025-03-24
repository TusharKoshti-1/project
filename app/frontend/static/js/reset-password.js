document.addEventListener("DOMContentLoaded", () => {
    // Show modal popup
    function showModal(message, isSuccess) {
        return new Promise((resolve) => {
            const modal = document.getElementById("popup-modal");
            const modalContent = document.getElementById("modal-content");
            const modalMessage = document.getElementById("modal-message");
            const modalOk = document.getElementById("modal-ok");

            if (!modal || !modalContent || !modalMessage || !modalOk) {
                console.error("Modal elements not found in DOM");
                resolve();
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

    // Toggle password visibility
    const togglePasswordElements = document.querySelectorAll(".toggle-password");
    togglePasswordElements.forEach(toggle => {
        toggle.addEventListener("click", () => {
            const targetId = toggle.getAttribute("data-target");
            const passwordInput = document.getElementById(targetId);
            const icon = toggle.querySelector("i");

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
    });

    // Validate and submit reset password form
    async function validateResetPassword(event) {
        event.preventDefault();

        const newPasswordInput = document.getElementById("new-password");
        const confirmPasswordInput = document.getElementById("confirm-password");
        const newPassword = newPasswordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();
        const submitButton = event.target.querySelector("button[type='submit']");

        submitButton.disabled = true; // Disable button to prevent multiple submissions

        // Password validation
        if (!newPassword || newPassword.length < 8) {
            await showError("Password must be at least 8 characters long.");
            submitButton.disabled = false;
            return;
        }

        if (newPassword !== confirmPassword) {
            await showError("Passwords do not match.");
            submitButton.disabled = false;
            return;
        }

        // Retrieve email and OTP from sessionStorage
        const email = sessionStorage.getItem("resetEmail");
        const otp = sessionStorage.getItem("verifiedOtp");

        if (!email) {
            await showError("No email found. Please start the reset process again.");
            window.location.href = "/forgot-password";
            submitButton.disabled = false;
            return;
        }

        if (!otp) {
            await showError("OTP not verified. Please verify OTP first.");
            window.location.href = "/otp_verify";
            submitButton.disabled = false;
            return;
        }

        const API_URL = "http://127.0.0.1:8000/auth/reset-password";

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "ngrok-skip-browser-warning": "true", // If using ngrok
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password: newPassword, otp }),
            });

            const result = await response.json();

            if (response.ok) {
                sessionStorage.removeItem("resetEmail"); // Clean up
                sessionStorage.removeItem("verifiedOtp"); // Clean up
                await showSuccess(result.message || "Password reset successfully.");
                window.location.href = "/login"; // Redirect to login after OK
                document.getElementById("reset-password-form").reset();
            } else {
                throw new Error(result.detail || "An error occurred while resetting your password.");
            }
        } catch (error) {
            await showError(error.message);
            console.error("Error:", error);
        } finally {
            submitButton.disabled = false; // Re-enable the button
        }
    }

    // Attach event listener to form
    const form = document.getElementById("reset-password-form");
    if (form) {
        form.addEventListener("submit", validateResetPassword);
    } else {
        console.error("Form with ID 'reset-password-form' not found");
    }
});