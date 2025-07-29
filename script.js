document.addEventListener('DOMContentLoaded', () => {
    // --- UTILITY FUNCTIONS ---
    const outputContainer = document.getElementById('output-container');
    const outputBox = document.getElementById('output-box');
    const loader = document.getElementById('loader');
    const copyBtn = document.getElementById('copy-btn');
    const apiKeyInput = document.getElementById('apiKey');

    // Load API key from local storage
    if (localStorage.getItem('openai_api_key')) {
        apiKeyInput.value = localStorage.getItem('openai_api_key');
    }
    
    // Save API key to local storage on change
    apiKeyInput.addEventListener('input', () => {
        localStorage.setItem('openai_api_key', apiKeyInput.value);
    });

    const showLoader = (show) => {
        outputContainer.classList.remove('hidden');
        loader.classList.toggle('hidden', !show);
        outputBox.classList.toggle('hidden', show);
    };

    const displayOutput = (data, isText = false) => {
        outputBox.textContent = isText ? data : JSON.stringify(data, null, 2);
        showLoader(false);
    };
    
    const displayError = (error) => {
        outputBox.textContent = `Error: ${error.message}`;
        showLoader(false);
    };
    
    // --- TAB SWITCHING ---
    window.openTab = (evt, tabName) => {
        document.querySelectorAll('.tab-content').forEach(tc => tc.style.display = "none");
        document.querySelectorAll('.tab-link').forEach(tl => tl.classList.remove('active'));
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.classList.add('active');
        outputContainer.classList.add('hidden'); // Hide output on tab switch
    };
    document.querySelector('.tab-link').click(); // Open first tab by default

    // --- GENERIC API REQUEST HANDLER ---
    const handleApiRequest = async (endpoint, options = {}) => {
        showLoader(true);
        try {
            const response = await fetch(endpoint, options);
            const responseData = await response.json();
            if (!response.ok) {
                throw new Error(responseData.detail || `HTTP error! Status: ${response.status}`);
            }
            return responseData;
        } catch (error) {
            displayError(error);
            // Return null or throw to signify failure to the caller
            return null;
        }
    };
    
    // --- FORM EVENT LISTENERS ---

    // Cold Email
    document.getElementById('cold-email-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
            api_key: apiKeyInput.value,
            name: document.getElementById('ce-name').value,
            role: document.getElementById('ce-role').value,
            company: document.getElementById('ce-company').value,
            pain_point: document.getElementById('ce-pain').value,
            offer: document.getElementById('ce-offer').value,
            tone: document.getElementById('ce-tone').value
        };
        const data = await handleApiRequest('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (data && data.email) displayOutput(data.email, true);
    });

    // Follow-Up
    document.getElementById('follow-up-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
            api_key: apiKeyInput.value,
            role: document.getElementById('fu-role').value,
            company: document.getElementById('fu-company').value,
            context: document.getElementById('fu-context').value,
            delay_days: parseInt(document.getElementById('fu-delay').value),
            tone: document.getElementById('fu-tone').value
        };
        const data = await handleApiRequest('/api/followup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (data && data.followup_email) displayOutput(data.followup_email, true);
    });

    // CSV Upload
    document.getElementById('csv-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('csv-file');
        if (!apiKeyInput.value) return alert('Please enter your OpenAI API Key.');
        if (fileInput.files.length === 0) return alert('Please select a CSV file.');
        
        showLoader(true);
        outputBox.textContent = ''; // Clear previous results

        Papa.parse(fileInput.files[0], {
            header: true,
            skipEmptyLines: true,
            complete: async (results) => {
                const leads = results.data;
                const allSequences = [];
                let hasError = false;
                for (const lead of leads) {
                    const body = { api_key: apiKeyInput.value, ...lead };
                    const data = await handleApiRequest('/api/sequence', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(body),
                    });

                    if (data) {
                        allSequences.push({ lead: lead.name, ...data });
                        outputBox.textContent += `Generated sequence for ${lead.name}...\n`;
                    } else {
                        outputBox.textContent += `ERROR generating for ${lead.name}. See details above.\n`;
                        hasError = true;
                    }
                }
                if (!hasError) {
                   displayOutput(allSequences); // Show final JSON object
                }
            }
        });
    });

    // Maps Scraper
    document.getElementById('maps-scraper-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const params = new URLSearchParams({
            keyword: document.getElementById('maps-keyword').value,
            location: document.getElementById('maps-location').value,
        });
        const data = await handleApiRequest(`/api/maps-scrape?${params}`);
        if (data) displayOutput(data);
    });

    // LinkedIn Scraper
    document.getElementById('linkedin-scraper-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
            profile_url: document.getElementById('linkedin-url').value,
            email: document.getElementById('linkedin-email').value,
            password: document.getElementById('linkedin-password').value
        };
        const data = await handleApiRequest('/api/linkedin-scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (data) displayOutput(data);
    });
    
    // Email Verifier
    document.getElementById('email-verifier-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = { email: document.getElementById('verify-email-input').value };
        const data = await handleApiRequest('/api/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (data) displayOutput(data);
    });

    // Copy Button
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(outputBox.textContent).then(() => {
            copyBtn.textContent = 'Copied!';
            setTimeout(() => { copyBtn.textContent = 'Copy to Clipboard'; }, 2000);
        });
    });
});