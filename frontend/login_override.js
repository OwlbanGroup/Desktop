// Login Override Functions for Frontend Integration

async function emergencyOverride() {
    const userId = document.getElementById('emergencyUserId').value;
    const reason = document.getElementById('emergencyReason').value;
    const emergencyCode = document.getElementById('emergencyCode').value;

    try {
        const response = await fetch('/api/override/emergency', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId,
                reason,
                emergencyCode
            })
        });

        const data = await response.json();
        document.getElementById('overrideResults').innerHTML = `
            <h3>Emergency Override Result:</h3>
            <p><strong>Success:</strong> ${data.success}</p>
            <p><strong>Message:</strong> ${data.message}</p>
            ${data.data ? `<p><strong>Override ID:</strong> ${data.data.overrideId}</p>` : ''}
        `;
        document.getElementById('overrideResults').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('overrideResults').innerHTML = '<p>Error occurred during emergency override.</p>';
        document.getElementById('overrideResults').style.display = 'block';
    }
}

async function adminOverride() {
    const adminUserId = document.getElementById('adminUserId').value;
    const targetUserId = document.getElementById('targetUserId').value;
    const reason = document.getElementById('adminReason').value;
    const justification = document.getElementById('justification').value;

    try {
        const response = await fetch('/api/override/admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                adminUserId,
                targetUserId,
                reason,
                justification
            })
        });

        const data = await response.json();
        document.getElementById('overrideResults').innerHTML = `
            <h3>Admin Override Result:</h3>
            <p><strong>Success:</strong> ${data.success}</p>
            <p><strong>Message:</strong> ${data.message}</p>
            ${data.data ? `<p><strong>Override ID:</strong> ${data.data.overrideId}</p>` : ''}
        `;
        document.getElementById('overrideResults').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('overrideResults').innerHTML = '<p>Error occurred during admin override.</p>';
        document.getElementById('overrideResults').style.display = 'block';
    }
}

async function technicalOverride() {
    const supportUserId = document.getElementById('supportUserId').value;
    const targetUserId = document.getElementById('techTargetUserId').value;
    const reason = document.getElementById('techReason').value;
    const ticketNumber = document.getElementById('ticketNumber').value;

    try {
        const response = await fetch('/api/override/technical', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                supportUserId,
                targetUserId,
                reason,
                ticketNumber
            })
        });

        const data = await response.json();
        document.getElementById('overrideResults').innerHTML = `
            <h3>Technical Override Result:</h3>
            <p><strong>Success:</strong> ${data.success}</p>
            <p><strong>Message:</strong> ${data.message}</p>
            ${data.data ? `<p><strong>Override ID:</strong> ${data.data.overrideId}</p>` : ''}
        `;
        document.getElementById('overrideResults').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('overrideResults').innerHTML = '<p>Error occurred during technical override.</p>';
        document.getElementById('overrideResults').style.display = 'block';
    }
}

async function validateOverride() {
    const overrideId = document.getElementById('validateOverrideId').value;
    const userId = document.getElementById('validateUserId').value;

    try {
        const response = await fetch(`/api/override/validate/${overrideId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId
            })
        });

        const data = await response.json();
        document.getElementById('overrideResults').innerHTML = `
            <h3>Override Validation Result:</h3>
            <p><strong>Success:</strong> ${data.success}</p>
            <p><strong>Message:</strong> ${data.message}</p>
            ${data.data ? `<p><strong>Valid:</strong> ${data.data.valid}</p>` : ''}
        `;
        document.getElementById('overrideResults').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('overrideResults').innerHTML = '<p>Error occurred during override validation.</p>';
        document.getElementById('overrideResults').style.display = 'block';
    }
}

async function getActiveOverrides() {
    const userId = document.getElementById('activeUserId').value;

    try {
        const response = await fetch(`/api/override/active/${userId}`);
        const data = await response.json();

        let overridesHtml = '<h3>Active Overrides:</h3>';
        if (data.data && data.data.activeOverrides.length > 0) {
            overridesHtml += '<ul>';
            data.data.activeOverrides.forEach(override => {
                overridesHtml += `<li><strong>ID:</strong> ${override.id}, <strong>Type:</strong> ${override.type}, <strong>Expires:</strong> ${override.expiresAt}</li>`;
            });
            overridesHtml += '</ul>';
        } else {
            overridesHtml += '<p>No active overrides found.</p>';
        }

        document.getElementById('overrideResults').innerHTML = overridesHtml;
        document.getElementById('overrideResults').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('overrideResults').innerHTML = '<p>Error occurred while fetching active overrides.</p>';
        document.getElementById('overrideResults').style.display = 'block';
    }
}
