document.addEventListener("DOMContentLoaded", () => {
    // API Configuration
    const API_URL = "http://127.0.0.1:8000/admin/profile/";
    const token = sessionStorage.getItem("user");
    const userId = sessionStorage.getItem("userId");

    // Elements
    // const adminPhoto = document.getElementById("adminPhoto");
    const adminName = document.getElementById("adminName");
    // const adminRole = document.getElementById("adminRole");
    const adminEmail = document.getElementById("adminEmail");
    const adminPhone = document.getElementById("adminPhone");

    // Edit form elements
    const editName = document.getElementById("editName");
    const editEmail = document.getElementById("editEmail");
    const editPhone = document.getElementById("editPhone");
    const editForm = document.getElementById("editForm");

    async function fetchUserProfile() {
        if (!token || !userId) {
            alert("Please login first");
            window.location.href = "/login";
            return;
        }

        try {
            const response = await fetch(`${API_URL}${userId}`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": "true"
                }
            });

            if (response.ok) {
                const data = await response.json();
                const user = data.user;

                // Update profile display
                adminName.textContent = user.name || "Unknown User";
                adminEmail.textContent = user.email;
                adminPhone.textContent = user.phone || "Not provided";
                // adminRole.textContent = user.role_id === 1 ? "Administrator" : "Employee";
                
                // Populate edit form
                editName.value = user.name || "";
                editEmail.value = user.email;
                editPhone.value = user.phone || "";
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Failed to fetch profile");
                if (response.status === 401) {
                    sessionStorage.clear();
                    window.location.href = "/login";
                }
            }
        } catch (error) {
            console.error("Error fetching profile:", error);
            alert("Error connecting to the server");
        }
    }

    // Toggle edit form visibility
    window.toggleEdit = function() {
        editForm.style.display = editForm.style.display === "none" ? "block" : "none";
    };

    // Save profile changes (you'll need to implement the PUT endpoint)
    window.saveProfile = async function() {
        if (!token) {
            alert("Please login first");
            return;
        }

        const updatedProfile = {
            name: editName.value.trim(),
            email: editEmail.value.trim(),
            phone: editPhone.value.trim()
        };

        try {
            const response = await fetch(`${API_URL}${userId}`, {
                method: "PUT", // Assuming you'll add a PUT endpoint
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": "true"
                },
                body: JSON.stringify(updatedProfile)
            });

            if (response.ok) {
                alert("Profile updated successfully");
                fetchUserProfile(); // Refresh the display
                toggleEdit(); // Hide the form
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Failed to update profile");
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            alert("Error connecting to the server");
        }
    };

    // Initial fetch when page loads
    fetchUserProfile();
});