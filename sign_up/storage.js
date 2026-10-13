const signupForm = document.getElementById("signupForm");
const message = document.getElementById("message");

signupForm.addEventListener("submit", function(event) {
    event.preventDefault();

    const usernameInput = document.getElementById("username")
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();

    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
   
    //Betty = betty
    const normalizedUsername = username.toLowerCase();

    if (username === "") {
        showMessage("Please enter a username.", "white");
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

    //unique key creation using username
    const storageKey = `user_${normalizedUsername}`;

    //check for existing username
    if (localStorage.getItem(storageKey) !== null) {
        showMessage("That username is already taken; please try again.", "white");
        usernameInput.focus()
        return;
    }

    const userData = {
        username: username,
        email: email,
        password: password,
        createdAt: new Date().toISOString()
    };

    //dynamically save user data
    localStorage.setItem(storageKey, JSON.stringify(userData));

    showMessage(`${username}'s account created successfully!`, "white");

    //Claer form
    signupForm.reset();

    //Redirect to Login page: include mini delay
    setTimeout(function() {
        window.location.href = "login.html";
    }, 1500);
});

function showMessage(text, color) {
    message.textContent = text;
    message.style.color = color;
}