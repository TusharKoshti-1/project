document.addEventListener('DOMContentLoaded', () => {
    const contentArea = document.getElementById('content-area');
    const sectionTitle = document.getElementById('section-title');
    const sidebarLinks = document.querySelectorAll('.sidebar ul li a');

    // Hide/show sections based on the selected link
    sidebarLinks.forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();

            const section = link.getAttribute('data-section');
            sectionTitle.textContent = section;

            // Clear previous content
            contentArea.innerHTML = '';

            // Update content based on the section
            if (section === 'Employess') {
                // Show the Employee section
                const employeeSection = document.getElementById('employee-section');
                employeeSection.style.display = 'block';
                contentArea.appendChild(employeeSection.cloneNode(true));
            } else {
                contentArea.innerHTML = `<p>Content for the ${section} section will appear here.</p>`;
            }
        });
    });

    // Logout button functionality
    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', () => {
        alert('Logging out...');
        // Redirect to login page or perform logout logic
        window.location.href = '/logout';
    });
});