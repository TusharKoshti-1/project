document.addEventListener("DOMContentLoaded", () => {
    // Get all OTP inputs
    const otpInputs = document.querySelectorAll(".otp-input");

    // Add event listeners to each input
    otpInputs.forEach((input, index) => {
        input.addEventListener("input", (e) => {
            // Only allow numbers
            if (e.target.value && !/^[0-9]$/.test(e.target.value)) {
                e.target.value = "";
                return;
            }

            // Move to next input if a digit is entered
            if (e.target.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });

        input.addEventListener("keydown", (e) => {
            // Move to previous input on backspace if current input is empty
            if (e.key === "Backspace" && !e.target.value && index > 0) {
                otpInputs[index - 1].focus();
            }
        });

        // Handle paste event
        input.addEventListener("paste", (e) => {
            e.preventDefault();
            const pastedData = e.clipboardData.getData("text").replace(/\D/g, ""); // Remove non-digits
            if (pastedData.length > 0) {
                for (let i = 0; i < otpInputs.length && i < pastedData.length; i++) {
                    otpInputs[i].value = pastedData[i];
                    if (i < otpInputs.length - 1) {
                        otpInputs[i + 1].focus();
                    }
                }
            }
        });
    });

    // Verify OTP function
    async function verifyOtp(email, otp) {
        const API_URL = "http://127.0.0.1:8000/auth/verify-otp";
        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "ngrok-skip-browser-warning": "true", // If using ngrok
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, otp }),
            });

            const result = await response.json();

            if (response.ok) {
                sessionStorage.setItem("verifiedOtp", otp);
                window.location.href = "/reset-password";
            } else {
                throw new Error(result.detail || "Invalid OTP");
            }
        } catch (error) {
            alert("An error occurred: " + error.message);
        }
    }

    // Form submission handler
    const form = document.getElementById("otp-form");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Collect OTP
        const otp = Array.from(otpInputs)
            .map(input => input.value)
            .join("");

        if (otp.length !== 6 || !/^\d{6}$/.test(otp)) {
            alert("Please enter a valid 6-digit OTP.");
            return;
        }

        // Retrieve email from sessionStorage
        const email = sessionStorage.getItem("resetEmail");
        if (!email) {
            alert("No email found. Please start the reset process again.");
            window.location.href = "/forgot-password";
            return;
        }

        await verifyOtp(email, otp);
    });
});