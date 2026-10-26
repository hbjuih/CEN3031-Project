const deleteButton = document.getElementById("delete-account-btn")
const deleteDeletion = document.getElementById("deletion")
const cancelDelete = document.getElementById("cancel-delete")
const confirmDelete = document.getElementById("confirm-delete")

if (deleteButton && deleteDeletion && cancelDelete && confirmDelete) {
    deleteButton.addEventListener("click", () => {deleteDeletion.hidden = false;});
    
    cancelDelete.addEventListener("click", () => {deleteDeletion.hidden = true;});
    
    deleteDeletion.addEventListener("click", (e) => {
        if (e.target === deleteDeletion) {
            deleteDeletion.hidden = true;
        }
    });
    
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !deleteDeletion.hidden) {
            deleteDeletion.hidden = true;
        }
    });
    
    confirmDelete.addEventListener("click", () => {
        // Connect With Backend Still
        deleteDeletion.hidden = true;
    });
}