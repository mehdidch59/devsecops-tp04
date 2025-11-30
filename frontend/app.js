const API_BASE_URL = '/api';

// DOM elements
const userForm = document.getElementById('user-form');
const userIdInput = document.getElementById('user-id');
const userNameInput = document.getElementById('user-name');
const userMailInput = document.getElementById('user-mail');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');
const formTitle = document.getElementById('form-title');
const usersTbody = document.getElementById('users-tbody');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');

// Load users on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
});

// Form submission handler
userForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userId = userIdInput.value;
    const userData = {
        name: userNameInput.value.trim(),
        mail: userMailInput.value.trim()
    };

    try {
        if (userId) {
            await updateUser(userId, userData);
        } else {
            await createUser(userData);
        }
        resetForm();
        loadUsers();
    } catch (error) {
        showError(error.message);
    }
});

// Cancel edit
cancelBtn.addEventListener('click', () => {
    resetForm();
});

// API functions
async function loadUsers() {
    try {
        loadingDiv.style.display = 'block';
        errorDiv.style.display = 'none';
        
        const response = await fetch(`${API_BASE_URL}/users`);
        
        if (!response.ok) {
            throw new Error(`Failed to load users: ${response.statusText}`);
        }
        
        const users = await response.json();
        displayUsers(users);
        loadingDiv.style.display = 'none';
    } catch (error) {
        loadingDiv.style.display = 'none';
        showError(`Error loading users: ${error.message}`);
    }
}

async function createUser(userData) {
    const response = await fetch(`${API_BASE_URL}/users`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create user');
    }

    return await response.json();
}

async function updateUser(userId, userData) {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update user');
    }

    return await response.json();
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete user');
        }

        loadUsers();
    } catch (error) {
        showError(`Error deleting user: ${error.message}`);
    }
}

// UI functions
function displayUsers(users) {
    usersTbody.innerHTML = '';
    
    if (users.length === 0) {
        usersTbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No users found</td></tr>';
        return;
    }

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.mail}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-edit" onclick="editUser(${user.id}, '${user.name}', '${user.mail}')">Edit</button>
                    <button class="btn-delete" onclick="deleteUser(${user.id})">Delete</button>
                </div>
            </td>
        `;
        usersTbody.appendChild(row);
    });
}

function editUser(id, name, mail) {
    userIdInput.value = id;
    userNameInput.value = name;
    userMailInput.value = mail;
    formTitle.textContent = 'Edit User';
    submitBtn.textContent = 'Update User';
    cancelBtn.style.display = 'inline-block';
    
    // Scroll to form
    document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    userIdInput.value = '';
    userNameInput.value = '';
    userMailInput.value = '';
    formTitle.textContent = 'Add New User';
    submitBtn.textContent = 'Add User';
    cancelBtn.style.display = 'none';
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Make deleteUser and editUser available globally for onclick handlers
window.deleteUser = deleteUser;
window.editUser = editUser;

