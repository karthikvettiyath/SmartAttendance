const API_BASE = "http://localhost:8000/api";

// --- Tab Switching Logic ---
document.addEventListener("DOMContentLoaded", () => {
    const navLinks = document.querySelectorAll(".nav-link");
    const viewSections = document.querySelectorAll(".view-section");

    navLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            // Remove active classes
            navLinks.forEach(l => l.classList.remove("active"));
            viewSections.forEach(v => v.classList.add("hidden"));
            viewSections.forEach(v => v.classList.remove("active"));

            // Add active class to clicked tab and corresponding section
            link.classList.add("active");
            const targetId = link.getAttribute("data-target");
            document.getElementById(targetId).classList.remove("hidden");
            document.getElementById(targetId).classList.add("active");
        });
    });
});

// --- Login Logic ---
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMsg = document.getElementById('errorMsg');

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const res = await fetch(`${API_BASE}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!res.ok) throw new Error("Invalid username or password");
            const data = await res.json();
            
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', username);
            window.location.href = "dashboard.html";
        } catch (err) {
            errorMsg.innerText = err.message;
        }
    });
}

// --- Logout ---
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = "index.html";
}

// --- Upload Form (Classroom Attendance) ---
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('uploadBtn');
        const resultsArea = document.getElementById('resultsArea');
        
        btn.innerText = "Extracting Faces using DeepFace...";
        btn.disabled = true;

        const fileInput = document.getElementById('classroomImage');
        const sessionName = document.getElementById('sessionName').value;
        const targetDate = document.getElementById('targetDate').value;

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('session_name', sessionName);
        formData.append('target_date', targetDate);

        try {
            const res = await fetch(`${API_BASE}/attendance/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });

            const data = await res.json();
            resultsArea.classList.remove('hidden');
            if(res.ok) {
                resultsArea.innerHTML = `<h4>✅ Success</h4><p>${data.message}</p>
                <img src="${data.image}" style="max-width: 100%; border-radius: 8px; margin-top: 15px; border: 2px solid var(--border);" />`;
            } else {
                resultsArea.innerHTML = `<h4 style="color:red">❌ Error</h4><p>${data.detail}</p>`;
            }
        } catch (err) {
            resultsArea.classList.remove('hidden');
            resultsArea.innerHTML = `<h4 style="color:red">❌ Error</h4><p>Failed to process attendance network request.</p>`;
        } finally {
            btn.innerText = "Process Image";
            btn.disabled = false;
        }
    });
}

// --- Reports Tab Logic ---
async function loadReports() {
    const tbody = document.getElementById("reportsTableBody");
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">Fetching secure logs...</td></tr>`;
    
    try {
        const res = await fetch(`${API_BASE}/reports/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (!res.ok) throw new Error("Failed to pull reports");
        const data = await res.json();
        
        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">No attendance logged yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = "";
        data.forEach(row => {
            tbody.innerHTML += `
                <tr>
                    <td><strong>${row.student_name}</strong></td>
                    <td>${row.roll_no}</td>
                    <td>${row.date}</td>
                    <td>${row.session}</td>
                    <td><span style="color: ${row.status === 'Present' ? '#10b981' : '#ef4444'}; font-weight: 600;">${row.status}</span></td>
                    <td>
                        <button class="btn-sm btn-edit" onclick="openEditModal(${row.id}, '${row.status}')">Edit</button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">Network Error Data Request Failed</td></tr>`;
    }
}

// --- Face Enrollment Logic ---
let localStream = null;

async function startCamera() {
    const video = document.getElementById("webcamVideo");
    const btn = document.getElementById("startCamBtn");
    
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = localStream;
        video.style.display = "block";
        btn.innerText = "Camera Active";
        btn.disabled = true;
        document.getElementById("enrollBtn").disabled = false;
    } catch(err) {
        alert("Camera permissions denied or device not found! (Make sure you are on localhost or HTTPS)");
    }
}

function captureFrame() {
    const video = document.getElementById("webcamVideo");
    const canvas = document.getElementById("webcamCanvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    // Return base64 JPEG
    return canvas.toDataURL("image/jpeg", 0.9);
}

async function enrollStudent() {
    const name = document.getElementById("enrollName").value;
    const roll = document.getElementById("enrollRoll").value;
    const dept = document.getElementById("enrollDept").value;
    
    if(!name || !roll || !dept) {
        alert("Please fill in Name, Roll Number, and Department first!");
        return;
    }

    const btn = document.getElementById("enrollBtn");
    const instr = document.getElementById("captureInstructions");
    const resultsArea = document.getElementById("enrollResults");
    
    btn.disabled = true;
    resultsArea.classList.add("hidden");
    
    const angles = ["Look Straight", "Look Slightly Left", "Look Slightly Right", "Look Slightly Up", "Look Slightly Down"];
    const capturedImages = [];

    // Capture sequence loop
    for (let i = 0; i < angles.length; i++) {
        instr.innerText = angles[i] + " (Capturing in 2s...)";
        // Wait 2 seconds for user to position
        await new Promise(r => setTimeout(r, 2000));
        instr.innerText = "SNAP!";
        capturedImages.push(captureFrame());
        await new Promise(r => setTimeout(r, 500)); // slight pause
    }

    instr.innerText = "Uploading payload to AI server...";

    // Assemble form block
    const formData = new FormData();
    formData.append("name", name);
    formData.append("roll_no", roll);
    formData.append("department", dept);
    formData.append("images", JSON.stringify(capturedImages));

    try {
        const res = await fetch(`${API_BASE}/students/enroll`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        });
        
        const data = await res.json();
        
        resultsArea.classList.remove('hidden');
        if (res.ok) {
            resultsArea.innerHTML = `<h4>✅ Enrolled</h4><p>${data.message}</p>`;
            document.getElementById("enrollName").value = "";
            document.getElementById("enrollRoll").value = "";
            document.getElementById("enrollDept").value = "";
        } else {
            resultsArea.innerHTML = `<h4 style="color:red">❌ Failed</h4><p>${data.detail}</p>`;
        }
    } catch(err) {
        resultsArea.classList.remove('hidden');
        resultsArea.innerHTML = `<h4 style="color:red">❌ Network Error</h4><p>Failed to hit enrollment API.</p>`;
    } finally {
        instr.innerText = "";
        btn.disabled = false;
        
        // Stop Camera Streams
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            document.getElementById("webcamVideo").style.display = "none";
            document.getElementById("startCamBtn").innerText = "Turn On Camera";
            document.getElementById("startCamBtn").disabled = false;
            btn.disabled = true;
        }
    }
}

// --- Load Enrolled Students Logic ---
async function loadStudents() {
    const tbody = document.getElementById("studentsTableBody");
    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center;">Fetching students from neural network...</td></tr>`;
    
    try {
        const res = await fetch(`${API_BASE}/students/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (!res.ok) throw new Error("Failed to pull students");
        const data = await res.json();
        
        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" style="text-align: center;">No students enrolled yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = "";
        data.forEach(row => {
            tbody.innerHTML += `
                <tr>
                    <td><strong>${row.name}</strong></td>
                    <td>${row.roll_no}</td>
                    <td>${row.department}</td>
                    <td>
                        <button class="btn-sm btn-danger" onclick="deleteStudent(${row.id})">Delete</button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: red;">Network Error Fetching Neural Roster</td></tr>`;
    }
}

// --- Management Functions ---

async function deleteStudent(studentId) {
    if (!confirm("Are you sure you want to delete this student and all their attendance records? This cannot be undone.")) return;

    try {
        const res = await fetch(`${API_BASE}/students/${studentId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (!res.ok) throw new Error("Failed to delete student");
        alert("Student deleted successfully");
        loadStudents(); // Refresh list
    } catch (e) {
        alert("Error: " + e.message);
    }
}

function openEditModal(attendanceId, currentStatus) {
    document.getElementById("editAttendanceId").value = attendanceId;
    document.getElementById("editStatusSelect").value = currentStatus;
    document.getElementById("editModal").classList.remove("hidden");
}

function closeEditModal() {
    document.getElementById("editModal").classList.add("hidden");
}

async function submitAttendanceUpdate() {
    const id = document.getElementById("editAttendanceId").value;
    const newStatus = document.getElementById("editStatusSelect").value;

    try {
        const res = await fetch(`${API_BASE}/attendance/${id}`, {
            method: 'PATCH',
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!res.ok) throw new Error("Update failed");
        
        alert("Status updated successfully");
        closeEditModal();
        loadReports(); // Refresh table
    } catch (e) {
        alert("Error updating status: " + e.message);
    }
}
