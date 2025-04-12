// Medication Reminder Notification
function checkMedicationTime() {
    const now = new Date();
    const medTimes = JSON.parse(localStorage.getItem('medicationSchedule')) || [];
    
    medTimes.forEach(med => {
        med.times.forEach(time => {
            const medDateTime = new Date(`${now.toDateString()} ${time}`);
            const diffMinutes = (now - medDateTime) / (1000 * 60);
            
            // If medication time is within last 15 minutes and not taken yet
            if (diffMinutes >= -15 && diffMinutes <= 15 && !med.taken) {
                if (Notification.permission === "granted") {
                    new Notification(`Time to take ${med.name}`, {
                        body: `Dosage: ${med.dosage}\nInstructions: ${med.instructions}`,
                        icon: '/static/images/med-icon.png'
                    });
                } else if (Notification.permission !== "denied") {
                    Notification.requestPermission().then(permission => {
                        if (permission === "granted") {
                            new Notification(`Time to take ${med.name}`, {
                                body: `Dosage: ${med.dosage}\nInstructions: ${med.instructions}`,
                                icon: '/static/images/med-icon.png'
                            });
                        }
                    });
                }
                
                // Play sound notification
                const audio = new Audio('/static/images/alert.mp3');
                audio.play();
            }
        });
    });
}

// Check every minute
setInterval(checkMedicationTime, 60000);

// Appointment Reminder
function checkAppointments() {
    const now = new Date();
    const appointments = JSON.parse(localStorage.getItem('appointments')) || [];
    
    appointments.forEach(appt => {
        const apptDate = new Date(appt.dateTime);
        const diffHours = (apptDate - now) / (1000 * 60 * 60);
        
        // If appointment is within next 24 hours and not reminded yet
        if (diffHours > 0 && diffHours <= 24 && !appt.reminded) {
            if (Notification.permission === "granted") {
                new Notification(`Upcoming Appointment`, {
                    body: `You have an appointment with ${appt.doctor} in ${Math.floor(diffHours)} hours`,
                    icon: '/static/images/appt-icon.png'
                });
                appt.reminded = true;
                localStorage.setItem('appointments', JSON.stringify(appointments));
            }
        }
    });
}

// Check every hour
setInterval(checkAppointments, 3600000);

// Wound Image Analysis
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('woundImage');
    const preview = document.getElementById('imagePreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput.click());
        
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length) {
                const file = e.target.files[0];
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    preview.src = event.target.result;
                    preview.style.display = 'block';
                    analyzeBtn.disabled = false;
                    uploadArea.style.display = 'none';
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Save medication taken
function markMedicationTaken(medId, time) {
    const meds = JSON.parse(localStorage.getItem('medicationSchedule')) || [];
    const med = meds.find(m => m.id === medId);
    
    if (med) {
        if (!med.takenTimes) med.takenTimes = [];
        med.takenTimes.push(new Date().toISOString());
        localStorage.setItem('medicationSchedule', JSON.stringify(meds));
        location.reload();
    }
}

// Chart for recovery progress
function renderProgressChart() {
    const ctx = document.getElementById('recoveryChart');
    if (ctx) {
        const progressData = JSON.parse(localStorage.getItem('recoveryProgress')) || [];
        
        const labels = progressData.map(item => new Date(item.date).toLocaleDateString());
        const painLevels = progressData.map(item => item.painLevel);
        const mobilityScores = progressData.map(item => item.mobilityScore);
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Pain Level (1-10)',
                        data: painLevels,
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1
                    },
                    {
                        label: 'Mobility Score (1-10)',
                        data: mobilityScores,
                        borderColor: 'rgb(54, 162, 235)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10
                    }
                }
            }
        });
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    renderProgressChart();
    
    // Request notification permission on first load
    if (Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission();
    }
});