function toggleEdit() {
  const form = document.getElementById('editForm');
  form.style.display = form.style.display === 'block' ? 'none' : 'block';
}

function saveProfile() {
  const name = document.getElementById('editName').value.trim();
  const email = document.getElementById('editEmail').value.trim();
  const phone = document.getElementById('editPhone').value.trim();
  const photoFile = document.getElementById('editPhotoFile').files[0];

  if (name) document.getElementById('adminName').innerText = name;
  if (email) document.getElementById('adminEmail').innerText = email;
  if (phone) document.getElementById('adminPhone').innerText = phone;

  if (photoFile) {
    const reader = new FileReader();
    reader.onload = function (e) {
      document.getElementById('adminPhoto').src = e.target.result;
    };
    reader.readAsDataURL(photoFile);
  }

  toggleEdit();
}