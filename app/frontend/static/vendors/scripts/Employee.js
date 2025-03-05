// Array of eight employee objects
const employees = [
    {
        name: "Jane Smith",
        jobTitle: "Project Manager",
        department: "Operations",
        id: "67890",
        email: "janesmith@example.com",
        phone: "+9876543210",
        image: "vendors/images/photo1.jpg"
    },
    {
        name: "John Doe",
        jobTitle: "Software Engineer",
        department: "IT",
        id: "12345",
        email: "johndoe@example.com",
        phone: "+1234567890",
        image: "vendors/images/photo2.jpg"
    },
    {
        name: "Alice Johnson",
        jobTitle: "UX Designer",
        department: "Design",
        id: "24680",
        email: "alicej@example.com",
        phone: "+1122334455",
        image: "vendors/images/photo3.jpg"
    },
    {
        name: "Bob Wilson",
        jobTitle: "Data Analyst",
        department: "Analytics",
        id: "13579",
        email: "bobw@example.com",
        phone: "+9988776655",
        image: "vendors/images/photo4.jpg"
    },
    {
        name: "Jane Smith",
        jobTitle: "Project Manager",
        department: "Operations",
        id: "67890",
        email: "janesmith@example.com",
        phone: "+9876543210",
        image: "vendors/images/photo1.jpg"
    },
    {
        name: "John Doe",
        jobTitle: "Software Engineer",
        department: "IT",
        id: "12345",
        email: "johndoe@example.com",
        phone: "+1234567890",
        image: "vendors/images/photo2.jpg"
    },
    {
        name: "Alice Johnson",
        jobTitle: "UX Designer",
        department: "Design",
        id: "24680",
        email: "alicej@example.com",
        phone: "+1122334455",
        image: "vendors/images/photo3.jpg"
    },
    {
        name: "Bob Wilson",
        jobTitle: "Data Analyst",
        department: "Analytics",
        id: "13579",
        email: "bobw@example.com",
        phone: "+9988776655",
        image: "vendors/images/photo4.jpg"
    }
];

// Get container element
const container = document.getElementById("employeeContainer");

// Function to create a profile card
function createProfileCard(employee) {
    // Create card div
    const card = document.createElement("div");
    card.className = "profile-card";

    // Create and append elements
    card.innerHTML = `
        <img class="profile-img" alt="Employee Photo">
        <h2>${employee.name}</h2>
        <p class="profile-info">${employee.jobTitle}</p>
        <p class="profile-info">${employee.department}</p>
        <p class="profile-info"><strong>ID:</strong> <span>${employee.id}</span></p>
        <p class="profile-info"><strong>Email:</strong> <span>${employee.email}</span></p>
        <p class="profile-info"><strong>Phone:</strong> <span>${employee.phone}</span></p>
    `;

    // Handle image
    const profileImage = card.querySelector(".profile-img");
    if (employee.image) {
        profileImage.src = employee.image;
        profileImage.onerror = () => {
            profileImage.src = "https://via.placeholder.com/80?text=Employee+Photo";
        };
    } else {
        profileImage.src = "https://via.placeholder.com/80?text=Employee+Photo";
    }

    return card;
}

// Generate all profile cards
employees.forEach(employee => {
    const profileCard = createProfileCard(employee);
    container.appendChild(profileCard);
});