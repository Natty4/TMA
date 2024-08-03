console.log('JavaScript is loaded and running!');


document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript is running!'); // Check if JS runs

    // Fetch services
    fetch('/get_services/')
        .then(response => response.json())
        .then(data => {
            console.log('Services:', data); // Check fetched data
            const serviceSelect = document.getElementById('service');
            data.services.forEach(service => {
                const option = document.createElement('option');
                option.value = service.id;
                option.text = `${service.name} - $${service.price}`;
                serviceSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching services:', error);
        });

    // Fetch doctors
    fetch('/get_doctors/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Doctors:', data); // Check fetched data
            const doctorList = document.getElementById('doctorList');
            data.doctors.forEach(doctor => {
                const doctorDiv = document.createElement('div');
                doctorDiv.className = 'doctor-item';
                doctorDiv.innerHTML = `
                    <h3>${doctor.full_name}</h3>
                    <p><strong>Specialty:</strong> ${doctor.specialty}</p>
                    <p><strong>Availability:</strong> ${doctor.availability}</p>
                    <p><strong>Rating:</strong> ${doctor.rating} / 5</p>
                    <button type="button" onclick="selectDoctor(${doctor.id})">Select Doctor</button>
                `;
                doctorList.appendChild(doctorDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching doctors:', error);
        });
});

// Function to handle doctor selection
window.selectDoctor = function(doctorId) {
    document.getElementById('selected_doctor').value = doctorId;
    alert('Doctor selected with ID: ' + doctorId);
};










// document.addEventListener('DOMContentLoaded', function () {
//     const form = document.getElementById('appointmentForm');

//     form.addEventListener('submit', function (event) {
//         event.preventDefault();
//         const formData = new FormData(form);
//         fetch('/book_appointment/', {
//             method: 'POST',
//             body: formData,
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken')
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 alert('Appointment booked successfully!');
//                 form.reset();
//             } else {
//                 alert('Error booking appointment.');
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
//     });

//     function getCookie(name) {
//         let cookieValue = null;
//         if (document.cookie && document.cookie !== '') {
//             const cookies = document.cookie.split(';');
//             for (let i = 0; i < cookies.length; i++) {
//                 const cookie = cookies[i].trim();
//                 if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                     break;
//                 }
//             }
//         }
//         return cookieValue;
//     }

//     fetch('/get_services/')
//         .then(response => response.json())
//         .then(data => {
//             const serviceSelect = document.getElementById('service');
//             data.services.forEach(service => {
//                 const option = document.createElement('option');
//                 option.value = service.id;
//                 option.text = `${service.name} - $${service.price}`;
//                 serviceSelect.appendChild(option);
//             });
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });

//     fetch('/get_doctors/')
//         .then(response => response.json())
//         .then(data => {
//             const doctorSelect = document.getElementById('doctor');
//             data.doctors.forEach(doctor => {
//                 const option = document.createElement('option');
//                 option.value = doctor.id;
//                 option.text = doctor.full_name;
//                 doctorSelect.appendChild(option);
//             });
            
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
// });










// document.addEventListener('DOMContentLoaded', function () {
//     const form = document.getElementById('appointmentForm');

//     form.addEventListener('submit', function (event) {
//         event.preventDefault();
//         const formData = new FormData(form);
//         fetch('/book_appointment/', {
//             method: 'POST',
//             body: formData,
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken')
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             alert('Appointment booked successfully!');
//             form.reset();
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
//     });

//     function getCookie(name) {
//         let cookieValue = null;
//         if (document.cookie && document.cookie !== '') {
//             const cookies = document.cookie.split(';');
//             for (let i = 0; i < cookies.length; i++) {
//                 const cookie = cookies[i].trim();
//                 if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                     break;
//                 }
//             }
//         }
//         return cookieValue;
//     }

//     fetch('/get_services/')
//         .then(response => response.json())
//         .then(data => {
//             const serviceSelect = document.getElementById('service');
//             data.services.forEach(service => {
//                 const option = document.createElement('option');
//                 option.value = service.id;
//                 option.text = service.name;
//                 serviceSelect.appendChild(option);
//             });
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
// });