const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

//async function allows /api/login to handle authentication
loginForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    const remember = document.getElementById("rememberMe")?.checked ?? false;

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ username, password , remember })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || "Username or password is incorrect.", "white");
            passwordInput.value = "";
            return;
        }

        showMessage("Login successful!", "white");
        loginForm.reset();

        //Redirect to Home page: include mini delay
        setTimeout(() => {
            window.location.href = "/home"; 
        }, 1000);

        } catch {
            showMessage("Unable to log in. Please try again.", "white");
        }
});