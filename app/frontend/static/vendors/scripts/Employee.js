console.log("Employee.js loaded");

// Function to create a profile card
function createProfileCard(employee) {
  const card = document.createElement("div");
  card.className = "profile-card";

  card.innerHTML = `
        <img class="profile-img" alt="Employee Photo">
        <h2>${employee.name}</h2>
        <p class="profile-info">${employee.jobTitle}</p>
        <p class="profile-info">${employee.department}</p>
        <p class="profile-info"><strong>ID:</strong> <span>${employee.id}</span></p>
        <p class="profile-info"><strong>Email:</strong> <span>${employee.email}</span></p>
        <p class="profile-info"><strong>Phone:</strong> <span>${employee.phone}</span></p>
    `;

  const profileImage = card.querySelector(".profile-img");
  profileImage.src = employee.image;
  profileImage.onerror = () => {
    profileImage.src = "https://via.placeholder.com/80?text=Employee+Photo";
  };

  return card;
}

// Fetch employees from the backend and display them
document.addEventListener("DOMContentLoaded", async () => {
  console.log("DOM fully loaded");
  const container = document.getElementById("employeeContainer");
  if (!container) {
    console.error("employeeContainer not found");
    return;
  }

  try {
    console.log("Fetching employees from /employees");
    const response = await fetch("http://127.0.0.1:8000/employees/", {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch employees: ${response.status}`);
    }

    const employees = await response.json();
    console.log("Fetched employees:", employees);

    if (employees.length === 0) {
      container.innerHTML = "<p>No employees found in the database.</p>";
      return;
    }

    employees.forEach((employee) => {
      const profileCard = createProfileCard(employee);
      container.appendChild(profileCard);
    });
  } catch (error) {
    console.error("Error fetching employees:", error);
    container.innerHTML =
      "<p>Error loading employees. Please try again later.</p>";
  }
});

