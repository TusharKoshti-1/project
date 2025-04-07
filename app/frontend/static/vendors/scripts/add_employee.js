console.log("add_employee.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM fully loaded");
  const employeeForm = document.getElementById("employeeForm");
  if (!employeeForm) {
    console.error("employeeForm not found");
    return;
  }

  employeeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("Form submission intercepted");

    const formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("mobile", document.getElementById("phone").value);
    formData.append("age", document.getElementById("age").value);
    formData.append("gender", document.getElementById("gender").value);
    formData.append(
      "department_name",
      document.getElementById("department_name").value,
    );
    formData.append("email", document.getElementById("email").value);
    formData.append("password", document.getElementById("password").value);
    formData.append("role_id", 1);
    const faceFile = document.getElementById("face_file").files[0];
    if (faceFile) {
      formData.append("face_file", faceFile);
      console.log("Face file added:", faceFile.name);
    } else {
      console.warn("No face_file selected");
    }

    try {
      console.log("Sending request to /employees/register");
      const response = await fetch(
        "http://127.0.0.1:8000/employees/register", // Changed to local URL
        {
          method: "POST",
          headers: {
            Accept: "application/json",
          },
          body: formData,
        },
      );
      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error response:", errorData);
        throw new Error(
          `Failed to add employee. Status: ${response.status}, Message: ${errorData.detail || "Unknown error"}`,
        );
      }

      const responseData = await response.json();
      console.log("Success response:", responseData);
      alert(
        `Employee added successfully! ${responseData.message || "Employee registered"}`,
      );
      employeeForm.reset();
      document.getElementById("imagePreviewContainer").innerHTML = "";
    } catch (error) {
      console.error("Fetch error:", error);
      alert(`An error occurred while adding the employee: ${error.message}`);
    }
  });
});
