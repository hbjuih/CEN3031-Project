const btn = document.getElementById("profile-button");
const dropdown = document.getElementById("dropdown");

if (btn && dropdown) {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const opening = dropdown.hidden;
        dropdown.classList.toggle("show");
    });

    document.addEventListener("click", () => {
        dropdown.classList.remove("show");
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            dropdown.classList.remove("show");
        }
    });
}