const signupForm = document.getElementById("signupForm");
const message = document.getElementById("message");

signupForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const usernameInput = document.getElementById("username")
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();

    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
   
    if (!username) {
        showMessage("Please enter a username.", "white");
        return;
    }

    if (!email) {
        showMessage("Please enter an email.", "white");
        return;
    }
    
    if (password !== confirmPassword) {
        showMessage("Passwords must match.", "white");
        return;
    }

    if (password.length < 6) {
        showMessage("Password must be at least 6 characters long.", "white");
        return;
    }

    try {
        const response = await fetch("/api/signup", {
            method: "POST",
            headers: { "Content-Type" : "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({username, email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || "Could not create an account.", "white");
            return;
        }

        showMessage("Account created successfully!", "white");
        signupForm.reset();

        //Redirect to Login page: include mini delay
        setTimeout(() => {
            window.location.href = "/login"; 
        }, 1500);
        
    } catch {
        showMessage("Unable to create an account. Please try again.", "white");
    }
});

function showMessage(text, color) {
    message.textContent = text;
    message.style.color = color;
}