// Access the user's webcam
const video = document.getElementById('video');
const workLogList = document.getElementById('work-log-list');

// Set up webcam
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => {
    console.error('Error accessing webcam:', err);
  });

// Function to draw bounding boxes around detected faces
function drawFaceBoundingBoxes(faces) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const videoWidth = video.videoWidth;
  const videoHeight = video.videoHeight;
  
  canvas.width = videoWidth;
  canvas.height = videoHeight;
  ctx.drawImage(video, 0, 0, videoWidth, videoHeight);
  
  faces.forEach(face => {
    const [x1, y1, x2, y2] = face;
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 4;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
  });
  
  // Append the canvas over the video
  video.parentElement.appendChild(canvas);
}

// Function to call the backend API for face detection
function detectFaces() {
  fetch('http://127.0.0.1:5000/detect')
    .then(response => response.json())
    .then(data => {
      if (data.faces.length > 0) {
        drawFaceBoundingBoxes(data.faces);
        logWorkEvent('Face Detected');
      }
    })
    .catch(err => {
      console.error('Error detecting faces:', err);
    });
}

// Function to log the detection event
function logWorkEvent(message) {
  const listItem = document.createElement('li');
  listItem.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
  workLogList.appendChild(listItem);
}

// Start detecting faces in the video feed
setInterval(detectFaces, 1000);  // Check for faces every second

// Logout button functionality
document.getElementById('logout').addEventListener('click', () => {
  alert('You have logged out.');
  // Implement logout logic here
});
