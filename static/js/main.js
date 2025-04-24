// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load connected users
    loadUsers();
    
    // Set up agent form submission
    const agentForm = document.getElementById('agent-form');
    if (agentForm) {
        agentForm.addEventListener('submit', handleAgentQuery);
    }
});

/**
 * Load connected users from the API
 */
async function loadUsers() {
    const usersList = document.getElementById('users-list');
    if (!usersList) return;
    
    try {
        const response = await fetch('/auth/users');
        const data = await response.json();
        
        if (data.users && data.users.length > 0) {
            usersList.innerHTML = '';
            
            data.users.forEach(user => {
                const userCard = document.createElement('div');
                userCard.className = 'user-card';
                
                const statusBadge = user.is_active 
                    ? '<span class="badge badge-success">Active</span>' 
                    : '<span class="badge badge-inactive">Inactive</span>';
                
                userCard.innerHTML = `
                    <div class="user-info">
                        <h3>@${user.twitter_username}</h3>
                        <p>User ID: ${user.id}</p>
                        <p>Status: ${statusBadge}</p>
                    </div>
                    <div class="user-actions">
                        ${user.is_active 
                            ? `<button class="btn" onclick="revokeAccess('${user.id}')">Revoke Access</button>` 
                            : `<a href="/auth/login" class="btn btn-primary">Reconnect</a>`
                        }
                    </div>
                `;
                
                usersList.appendChild(userCard);
            });
        } else {
            usersList.innerHTML = '<p>No connected accounts. <a href="/auth/login">Connect your Twitter account</a> to get started.</p>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        usersList.innerHTML = '<p>Error loading connected accounts. Please try again later.</p>';
    }
}

/**
 * Revoke access for a user
 * @param {string} userId - The user ID to revoke access for
 */
async function revokeAccess(userId) {
    try {
        const response = await fetch(`/auth/revoke/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Reload users list
            loadUsers();
        } else {
            alert('Failed to revoke access. Please try again.');
        }
    } catch (error) {
        console.error('Error revoking access:', error);
        alert('Error revoking access. Please try again later.');
    }
}

/**
 * Handle agent query form submission
 * @param {Event} event - The form submission event
 */
async function handleAgentQuery(event) {
    event.preventDefault();
    
    const queryInput = document.getElementById('agent-query');
    const responseDiv = document.getElementById('agent-response');
    
    if (!queryInput || !responseDiv) return;
    
    const query = queryInput.value.trim();
    if (!query) {
        responseDiv.innerHTML = '<p class="error-message">Please enter a query for the AI agent.</p>';
        return;
    }
    
    // Show loading state
    responseDiv.innerHTML = '<p>Processing your query...</p>';
    
    try {
        // This is a placeholder for the actual agent endpoint
        // In a real implementation, you would also need to select which user to act on behalf of
        const response = await fetch('/twitter/agent?query=' + encodeURIComponent(query));
        const data = await response.json();
        
        if (data.status === 'not_implemented') {
            responseDiv.innerHTML = `
                <p><strong>Agent Response:</strong></p>
                <p>${data.message}</p>
                <p>This is a placeholder for the AI agent functionality that will be implemented in future iterations.</p>
            `;
        } else {
            responseDiv.innerHTML = `
                <p><strong>Agent Response:</strong></p>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;
        }
    } catch (error) {
        console.error('Error with agent query:', error);
        responseDiv.innerHTML = '<p class="error-message">Error processing your query. Please try again later.</p>';
    }
}
