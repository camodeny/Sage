const urlParams = new URLSearchParams(window.location.hash.substring(1));
let access_token = urlParams.get('access_token');

if (access_token) {
    document.cookie = `jwt=${access_token}; path=/; secure; samesite=strict`;
} else {
   access_token = document.cookie
     .split('; ')
     .find(row => row.startsWith('jwt='))
     ?.split('=')[1];
}

fetch('/auth/verity_login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ token: access_token, html_page: html_page, scripts: scripts })
})
.then(response => response.json())
.then(data => {
    if (data.status == "error") {
        window.location.href = '/login';
    }
    if (data.message == 'email_not_verified') {
        window.location.href = '/confirm_email';
    }

    document.getElementById('root').innerHTML = data.html;

    for (const script_url of data.scripts) {
        const script = document.createElement('script');
        script.src = script_url;
        document.head.appendChild(script);
    }
})
.catch(error => console.error('Error:', error));