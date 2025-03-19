document.addEventListener("DOMContentLoaded", () => {
  const contentArea = document.getElementById("content-area");
  const sectionTitle = document.getElementById("section-title");
  const sidebarLinks = document.querySelectorAll(".sidebar ul li a");

  // Hide/show sections based on the selected link
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();

      const section = link.getAttribute("data-section");
      sectionTitle.textContent = section;

      // Clear previous content
      contentArea.innerHTML = "";

      // Update content based on the section
      if (section === "Employees") {
        // Fixed typo: "Employess" -> "Employees"
        const employeeSection = document.getElementById("employee-section");
        employeeSection.style.display = "block";
        contentArea.appendChild(employeeSection.cloneNode(true));
      } else {
        contentArea.innerHTML = `<p>Content for the ${section} section will appear here.</p>`;
      }
    });
  });

  // Logout button functionality
  const logoutBtn = document.getElementById("logout-btn");
  logoutBtn.addEventListener("click", async () => {
    // Get employee_id from cookie
    const employeeId = getCookie("employee_id");

    if (!employeeId) {
      alert("No active session found. Redirecting to login...");
      window.location.href = "/login";
      return;
    }

    try {
      const response = await fetch("/auth/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ employee_id: parseInt(employeeId) }), // Send as integer
        credentials: "include", // Include cookies in request
      });

      if (response.ok) {
        const data = await response.json();
        alert(data.msg); // e.g., "Logout successful, monitoring stopped"
        // Clear cookies client-side
        document.cookie =
          "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; secure; samesite=lax";
        document.cookie =
          "employee_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; secure; samesite=lax";
        // Redirect to login page
        window.location.href = "/login";
      } else {
        const errorData = await response.json();
        alert(`Logout failed: ${errorData.detail}`);
      }
    } catch (error) {
      console.error("Logout error:", error);
      alert("An error occurred during logout. Please try again.");
    }
  });

  // Helper function to get cookie value by name
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }
});
