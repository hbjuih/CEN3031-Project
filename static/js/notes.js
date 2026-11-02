
const notesList = document.getElementById("notes-list");
const message = document.getElementById("notes-message");
const form = document.getElementById("new-note");
const titleInput = document.getElementById("note-title");
const contentInput = document.getElementById("note-content");
const formHeading = document.getElementById("form-heading");
const cancelButton = document.getElementById("cancel-edit");

let editingId = null;

// Load saved notes from database
async function loadNotes() {
    try {
        const response = await fetch("/api/notes");
        const notes = await response.json();

        if (!response.ok) {
            throw new Error(notes.error || "Could not load notes.");
        }

        notesList.innerHTML = "";

        if (notes.length === 0) {
            message.textContent = "No notes yet. Create one!";
            return;
        }

        message.textContent = "";

        notes.forEach(note => {
            const card = document.createElement("div");
            card.className = "note-card";

            const title = document.createElement("h3");
            title.textContent = note.title;

            const content = document.createElement("p");
            content.textContent = note.content;

            const editButton = document.createElement("button");
            editButton.textContent = "Edit";
            editButton.onclick = () => editNote(note);

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.onclick = () => deleteNote(note.id);

            card.append(title, content, editButton, deleteButton);
            notesList.appendChild(card);
        });

    } catch (error) {
        message.textContent = error.message;
    }
}

// Create a new note or save changes
form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const title = titleInput.value.trim();
    const content = contentInput.value;

    if (!title) return;

    const url = editingId === null
        ? "/api/notes"
        : `/api/notes/${editingId}`;

    const method = editingId === null ? "POST" : "PUT";

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: title,
                content: content
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Could not save note.");
        }

        resetForm();
        await loadNotes();

    } catch (error) {
        message.textContent = error.message;
    }
});

// Fill in the form to edit an existing note
function editNote(note) {
    editingId = note.id;

    titleInput.value = note.title;
    contentInput.value = note.content;

    formHeading.textContent = "Edit Note";
    cancelButton.hidden = false;

    form.scrollIntoView();
}

// Delete a note
async function deleteNote(id) {
    if (!confirm("Delete this note?")) return;

    try {
        const response = await fetch(`/api/notes/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Could not delete note.");
        }

        if (editingId === id) resetForm();

        await loadNotes();

    } catch (error) {
        message.textContent = error.message;
    }
}

// Clear the form
function resetForm() {
    editingId = null;
    form.reset();

    formHeading.textContent = "New Note";
    cancelButton.hidden = true;
}

cancelButton.addEventListener("click", resetForm);

// Load notes when the page opens
loadNotes();
