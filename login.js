const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

loginForm.addEventListener("submit", function(event) {
    event.preventDefault();

    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    const normalizedUsername = username.toLowerCase();
    const storageKey = `user_${normalizedUsername}`;
    const savedUser = localStorage.getItem(storageKey);

    //const rememberMe = document.getElementById("rmemeberMe").checked;

    if (savedUser === null) {
        showMessage("Username or password is incorrect.", "white");
        return;
    }

    const userData = JSON.parse(savedUser);

    if (password !== userData.password) {
        showMessage("Username or password is incorrect.", "white");
        passwordInput.value = "";
        return;
    }

    showMessage("Login successful!", "white");

   const rememberMe = document.getElementById("rmemeberMe");

   if (rememberMe.checked) {
    //remebers after browser is closed
    localStorage.setItem("loggedInUser", userData.username);
    sessionStorage.removeItem("loggedInUser");
    } else {
        //remembers while browser session is open
        sessionStorage.setItem("loggedInUser", userData.username);
        localStorage.removeItem("loggedInUser");
   }

    //Claer form
    loginForm.reset();

    //Redirect to Home page: include mini delay
    setTimeout(function() {
        window.location.href = "home.html";
    }, 1000);
});

function showMessage(text, color) {
    message.textContent = text;
    message.style.color = color;
}