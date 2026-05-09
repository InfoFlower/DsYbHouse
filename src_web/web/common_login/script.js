

function check_login() {
    const passphrase = localStorage.getItem('passphrase');
    if (passphrase) {
        fetch('/api/check_passphrase/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ passphrase })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                return true;
            }
            else {
                localStorage.removeItem('passphrase');
                display_login();
                return false;
            }
        });
    }
}

function Send_login(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
  .then(data => {
    debug_section = document.getElementById('debug-section');
    if (debug_section) {
        debug_section.textContent = JSON.stringify(data, null, 2);
    }
      if (data.status === 'success') {
            if (data.passphrase) { 
                localStorage.setItem('passphrase', data.passphrase);
                display_rating();
            }
            else {
                alert('Login successful, but no passphrase received.');
            }
        }
        else {
            alert('Login failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during login.');
    });
}