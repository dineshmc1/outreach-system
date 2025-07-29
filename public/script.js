document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENT SELECTORS ---
    const outputContainer = document.getElementById('output-container');
    const outputBox = document.getElementById('output-box');
    const loader = document.getElementById('loader');
    const copyBtn = document.getElementById('copy-btn');
    const apiKeyInput = document.getElementById('apiKey');
    const serpApiKeyInput = document.getElementById('serpApiKey'); // NEW: SerpApi input

    // --- LOCAL STORAGE HANDLING ---
    // Load OpenAI API key
    if (localStorage.getItem('openai_api_key')) {
        apiKeyInput.value = localStorage.getItem('openai_api_key');
    }
    apiKeyInput.addEventListener('input', () => {
        localStorage.setItem('openai_api_key', apiKeyInput.value);
    });

    // NEW: Load SerpApi API key
    if (localStorage.getItem('serpapi_api_key')) {
        serpApiKeyInput.value = localStorage.getItem('serpapi_api_key');
    }
    serpApiKeyInput.addEventListener('input', () => {
        localStorage.setItem('serpapi_api_key', serpApiKeyInput.value);
    });

    // --- UI UTILITY FUNCTIONS ---
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
        outputContainer.classList.add('hidden');
    };
    document.querySelector('.tab-link').click();

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
        const data = await handleApiRequest('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
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
        const data = await handleApiRequest('/api/followup', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        if (data && data.followup_email) displayOutput(data.followup_email, true);
    });

    // CSV Upload
    document.getElementById('csv-form').addEventListener('submit', (e) => {
        e.preventDefault();
        if (!apiKeyInput.value) return alert('Please enter your OpenAI API Key.');
        const fileInput = document.getElementById('csv-file');
        if (fileInput.files.length === 0) return alert('Please select a CSV file.');
        showLoader(true);
        outputBox.textContent = '';
        Papa.parse(fileInput.files[0], {
            header: true, skipEmptyLines: true,
            complete: async (results) => {
                const leads = results.data;
                const allSequences = [];
                for (const lead of leads) {
                    const data = await handleApiRequest('/api/sequence', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ api_key: apiKeyInput.value, ...lead }) });
                    if (data) allSequences.push({ lead: lead.name, ...data });
                }
                displayOutput(allSequences);
            }
        });
    });

    // Maps Scraper (MODIFIED)
    document.getElementById('maps-scraper-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
            api_key: serpApiKeyInput.value, // Get key from the new input
            keyword: document.getElementById('maps-keyword').value,
            location: document.getElementById('maps-location').value,
        };
        const data = await handleApiRequest('/api/maps-scrape', {
            method: 'POST', // Use POST to send the key securely
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (data) displayOutput(data);
    });

    // LinkedIn Search
    document.getElementById('linkedin-scraper-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
            search_keyword: document.getElementById('linkedin-keyword').value,
            email: document.getElementById('linkedin-email').value,
            password: document.getElementById('linkedin-password').value
        };
        const data = await handleApiRequest('/api/linkedin-search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        if (data) displayOutput(data);
    });
    
    // Email Verifier
    document.getElementById('email-verifier-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = { email: document.getElementById('verify-email-input').value };
        const data = await handleApiRequest('/api/verify', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
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