
  // Handle Google login click event
  document.getElementById('googleLoginButton').addEventListener('click', function() {
    console.log('Google Login button clicked!');  // Add debug log here
    // Redirect to the /login route to trigger Google OAuth
    window.location.href = '/login';  // This triggers the OAuth flow from FastAPI
  });
  
  // Function to handle login via Google
  async function handleGoogleLogin() {
    console.log('Handle Google Login function called');
    const googleLoginUrl = "http://localhost:8000/login"; // Replace with your actual login URL
    window.location.href = googleLoginUrl; // Redirect the user to Google OAuth login
  }
  
  // Event listener for form submission (Login via email/password)
  // document.getElementById("loginForm").addEventListener("submit", validateLogin);
  
  // Check if the user is already logged in (via sessionStorage or localStorage)
  // function checkLoginStatus() {
  //   const token = sessionStorage.getItem("token") || localStorage.getItem("token");
  
  //   if (token) {
  //     // If a token exists, redirect to the dashboard
  //     window.location.href = "/dashboard";
  //   } else {
  //     // If no token is found, keep the user on the login page
  //     console.log("No token found. Please log in.");
  //   }
  // }
  
  // // Call this function to check login status when the page loads
  // window.onload = checkLoginStatus;