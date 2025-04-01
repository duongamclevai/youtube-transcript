async function sendRequest() {
    const urlInput = document.getElementById('urlInput');
    const responseElement = document.getElementById('response');
    
    try {
        // Parse the input JSON
        const requestData = JSON.parse(urlInput.value);
        
        // Send the request
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        // Parse and display the response
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
        
        // Add appropriate styling based on response
        if (response.ok) {
            responseElement.classList.remove('text-danger');
            responseElement.classList.add('text-success');
        } else {
            responseElement.classList.remove('text-success');
            responseElement.classList.add('text-danger');
        }
    } catch (error) {
        responseElement.textContent = `Error: ${error.message}`;
        responseElement.classList.remove('text-success');
        responseElement.classList.add('text-danger');
    }
}
