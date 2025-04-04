document.addEventListener("DOMContentLoaded", () => {
    // API Configuration
    const API_URL = "http://127.0.0.1:8000/admin/profile/";
    const token = sessionStorage.getItem("user");
    const userId = sessionStorage.getItem("userId");

    // Elements in the user info dropdown
    const userIconImg = document.querySelector(".user-info-dropdown .user-icon img");
    const userNameSpan = document.querySelector(".user-info-dropdown .user-name");

    // Check if elements exist
    if (!userIconImg || !userNameSpan) {
        console.error("User dropdown elements not found. Check your HTML.");
        return;
    }

    async function updateUserDropdown() {
        if (!token || !userId) {
            console.warn("No token or user ID found in sessionStorage. User may need to log in.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}${userId}`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": "true",
                },
            });

            if (response.ok) {
                const data = await response.json();
                const user = data.user;

                // Update profile picture (assuming it's base64 encoded)
                if (user.profile_picture) {
                    userIconImg.src = user.profile_picture; // Set base64 image
                    userIconImg.style.width = "60px"; // Enforce size
                    userIconImg.style.height = "50px";
                    userIconImg.style.objectFit = "cover"; // Ensure proper scaling
                } else {
                    // Fallback to default image
                    userIconImg.src = "/static/vendors/images/photo1.jpg";
                    userIconImg.style.width = "60px"; // Enforce size
                    userIconImg.style.height = "50px";
                    userIconImg.style.objectFit = "cover";
                }

                // Update user name
                userNameSpan.textContent = user.name || "Unknown User";

            } else {
                const errorData = await response.json();
                console.error("Failed to fetch profile for dropdown:", errorData.detail || "Unknown error");
                // Fallback to default values
                userIconImg.src = "/static/vendors/images/photo1.jpg";
                userIconImg.style.width = "40px";
                userIconImg.style.height = "40px";
                // userIconImg.style.objectFit = "cover";
                // userNameSpan.textContent = "Guest";
            }
        } catch (error) {
            console.error("Error updating user dropdown:", error);
            // Fallback to default values in case of error
            userIconImg.src = "/static/vendors/images/photo1.jpg";
            userIconImg.style.width = "40px";
            userIconImg.style.height = "40px";
            userIconImg.style.objectFit = "cover";
            userNameSpan.textContent = "Guest";
        }
    }

    // Call the function when the page loads
    updateUserDropdown();

    // Optional: Refresh the dropdown periodically or on user interaction
    window.addEventListener("storage", () => {
        const newToken = sessionStorage.getItem("user");
        const newUserId = sessionStorage.getItem("userId");
        if (newToken && newUserId) {
            updateUserDropdown();
        }
    });
});