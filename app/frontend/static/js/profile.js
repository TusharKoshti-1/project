document.addEventListener("DOMContentLoaded", () => {
    // API Configuration
    const API_URL = "http://127.0.0.1:8000/admin/profile/";
    const token = sessionStorage.getItem("user");
    const userId = sessionStorage.getItem("userId");

    // Elements
    const adminPhoto = document.getElementById("adminPhoto"); // Added for profile photo
    const adminName = document.getElementById("adminName");
    const adminEmail = document.getElementById("adminEmail");
    const adminPhone = document.getElementById("adminPhone");

    // Edit form elements
    const editName = document.getElementById("editName");
    const editEmail = document.getElementById("editEmail");
    const editPhone = document.getElementById("editPhone");
    const editPhotoFile = document.getElementById("editPhotoFile"); // File input for photo
    const editForm = document.getElementById("editForm");

    // Check if all elements exist
    if (!adminPhoto || !adminName || !adminEmail || !adminPhone || !editName || !editEmail || !editPhone || !editPhotoFile || !editForm) {
        console.error("One or more DOM elements not found. Check your HTML.");
        return;
    }

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
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": "true",
                },
            });

            if (response.ok) {
                const data = await response.json();
                const user = data.user;

                // Update profile display including photo
                adminName.textContent = user.name || "Unknown User";
                adminEmail.textContent = user.email;
                adminPhone.textContent = user.phone || "Not provided";

                // Handle profile photo (now base64)
                if (user.profile_picture) {
                    adminPhoto.src = user.profile_picture; // This will be "data:image/jpeg;base64,..."
                } else {
                    // Fallback to default image
                    adminPhoto.src = "https://randomuser.me/api/portraits/men/75.jpg";
                }

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
    window.toggleEdit = function () {
        editForm.style.display = editForm.style.display === "none" ? "block" : "none";
    };

    // Save profile changes with FormData for file upload
    window.saveProfile = async function () {
        if (!token) {
            alert("Please login first");
            return;
        }

        const formData = new FormData();
        formData.append("full_name", editName.value.trim());
        formData.append("email", editEmail.value.trim());
        formData.append("phone", editPhone.value.trim());

        // Check if a file is selected
        if (editPhotoFile.files && editPhotoFile.files[0]) {
            formData.append("profile_picture", editPhotoFile.files[0]);
            console.log("File appended to FormData:", editPhotoFile.files[0].name); // Debug log
        } else {
            console.warn("No file selected for upload.");
        }

        // Log FormData contents (for debugging)
        for (let pair of formData.entries()) {
            console.log(`${pair[0]}:`, pair[1]);
        }

        try {
            const response = await fetch(`${API_URL}${userId}`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "ngrok-skip-browser-warning": "true",
                },
                body: formData,
            });

            if (response.ok) {
                alert("Profile updated successfully");
                fetchUserProfile(); // Refresh the display
                toggleEdit(); // Hide the form
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Failed to update profile");
                console.error("Server response:", errorData);
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            alert("Error connecting to the server");
        }
    };

    // Initial fetch when page loads
    fetchUserProfile();
});