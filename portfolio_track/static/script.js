// Handle CSV upload form submission with loading animation and basic validation
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const loading = document.getElementById("loading");

    if (form && fileInput) {
        form.addEventListener("submit", (e) => {
            const file = fileInput.files[0];
            if (!file) {
                alert("Please select a CSV file before uploading.");
                e.preventDefault();
                return;
            }

            if (!file.name.endsWith(".csv")) {
                alert("Invalid file format. Please upload a CSV file only.");
                e.preventDefault();
                return;
            }

            // Show loading screen
            if (loading) loading.style.display = "block";
        });

        // File drag-and-drop support
        fileInput.addEventListener("dragover", (e) => {
            e.preventDefault();
            fileInput.classList.add("dragging");
        });

        fileInput.addEventListener("dragleave", () => {
            fileInput.classList.remove("dragging");
        });

        fileInput.addEventListener("drop", (e) => {
            e.preventDefault();
            fileInput.classList.remove("dragging");
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
            }
        });
    }

    // Fake Google Login
    const loginBtn = document.getElementById("fakeGoogleLogin");
    const userDisplay = document.getElementById("userDisplay");

    if (loginBtn) {
        // Restore login state on page load
        const user = localStorage.getItem("pfa_user");
        if (user) {
            if (userDisplay) { userDisplay.textContent = user; userDisplay.style.display = "inline-block"; }
            loginBtn.textContent = "Sign out";
        }

        loginBtn.addEventListener("click", () => {
            const currentUser = localStorage.getItem("pfa_user");
            if (currentUser) {
                // Sign out
                localStorage.removeItem("pfa_user");
                if (userDisplay) { userDisplay.style.display = "none"; userDisplay.textContent = ""; }
                loginBtn.textContent = "Sign in with Google";
            } else {
                // Fake sign in
                const fakeName = prompt("Enter your name:", "Sarthak Gupta");
                if (fakeName) {
                    localStorage.setItem("pfa_user", fakeName);
                    if (userDisplay) { userDisplay.textContent = fakeName; userDisplay.style.display = "inline-block"; }
                    loginBtn.textContent = "Sign out";
                }
            }
        });
    }

    // Tab switching
    const analysisBtn = document.getElementById("analysisTabBtn");
    const geminiBtn = document.getElementById("geminiTabBtn");
    const monthlyBtn = document.getElementById("monthlyTabBtn");
    const chatbotBtn = document.getElementById("chatbotTabBtn");
    const analysisTab = document.getElementById("analysisTab");
    const geminiTab = document.getElementById("geminiTab");
    const monthlyTab = document.getElementById("monthlyTab");
    const chatbotTab = document.getElementById("chatbotTab");

    function switchTab(targetTab) {
        // Hide all tabs
        [analysisTab, geminiTab, monthlyTab, chatbotTab].forEach(tab => {
            if (tab) tab.style.display = "none";
        });
        // Remove active class from all buttons
        [analysisBtn, geminiBtn, monthlyBtn, chatbotBtn].forEach(btn => {
            if (btn) btn.classList.remove("active");
        });
        // Show target tab and activate button
        if (targetTab === "analysis" && analysisTab && analysisBtn) {
            analysisTab.style.display = "block";
            analysisBtn.classList.add("active");
        } else if (targetTab === "gemini" && geminiTab && geminiBtn) {
            geminiTab.style.display = "block";
            geminiBtn.classList.add("active");
        } else if (targetTab === "monthly" && monthlyTab && monthlyBtn) {
            monthlyTab.style.display = "block";
            monthlyBtn.classList.add("active");
        } else if (targetTab === "chatbot" && chatbotTab && chatbotBtn) {
            chatbotTab.style.display = "block";
            chatbotBtn.classList.add("active");
        }
    }

    if (analysisBtn) analysisBtn.addEventListener("click", () => switchTab("analysis"));
    if (geminiBtn) geminiBtn.addEventListener("click", () => switchTab("gemini"));
    if (monthlyBtn) monthlyBtn.addEventListener("click", () => switchTab("monthly"));
    if (chatbotBtn) chatbotBtn.addEventListener("click", () => switchTab("chatbot"));

    // Chatbot functionality
    const chatInput = document.getElementById("chatInput");
    const chatSend = document.getElementById("chatSend");
    const chatMessages = document.getElementById("chatMessages");

    function sendChatMessage() {
        const query = chatInput.value.trim();
        if (!query) return;

        // Add user message to chat
        const userMsg = document.createElement("div");
        userMsg.className = "user-message";
        userMsg.textContent = query;
        chatMessages.appendChild(userMsg);
        chatInput.value = "";

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Send to backend
        fetch("/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        })
        .then(res => res.json())
        .then(data => {
            const botMsg = document.createElement("div");
            botMsg.className = "bot-message";
            botMsg.textContent = data.response || "Sorry, I couldn't process that.";
            chatMessages.appendChild(botMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(err => {
            const botMsg = document.createElement("div");
            botMsg.className = "bot-message error";
            botMsg.textContent = "Error communicating with server.";
            chatMessages.appendChild(botMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }

    if (chatSend) {
        chatSend.addEventListener("click", sendChatMessage);
    }

    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendChatMessage();
            }
        });
    }
});

// Result page chart enhancement
function renderSpendingChart(summary) {
    const ctx = document.getElementById("spendingChart");
    if (!ctx || !summary) return;

    const labels = Object.keys(summary);
    const dataValues = Object.values(summary);

    new Chart(ctx, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                label: "Spending (₹)",
                data: dataValues,
                borderWidth: 1,
                backgroundColor: [
                    "#007bff",
                    "#28a745",
                    "#ffc107",
                    "#dc3545",
                    "#6610f2",
                    "#20c997",
                    "#fd7e14"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#333",
                        font: { size: 14 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ₹${context.formattedValue}`;
                        }
                    }
                }
            }
        }
    });
}

// Render a date-based time series (line chart)
function renderTimeSeries(dates, totals) {
    const ctx = document.getElementById("timeChart").getContext('2d');
    if (!ctx || !dates || !totals) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Daily Spending (₹)',
                data: totals,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0,123,255,0.08)',
                fill: true,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { display: true, title: { display: true, text: 'Date' } },
                y: { display: true, title: { display: true, text: 'Spending (₹)' } }
            },
            plugins: { tooltip: { mode: 'index', intersect: false } }
        }
    });
}

// Render per-category stacked bar chart across dates
function renderCategorySeries(dates, categorySeries) {
    const ctxEl = document.getElementById("categoryChart");
    if (!ctxEl || !dates || !categorySeries) return;
    const ctx = ctxEl.getContext('2d');

    const colors = [
        '#007bff', '#28a745', '#ffc107', '#dc3545', '#6610f2', '#20c997', '#fd7e14', '#6c757d'
    ];

    const categories = Object.keys(categorySeries || {});
    const datasets = categories.map((cat, i) => ({
        label: cat,
        data: categorySeries[cat],
        backgroundColor: colors[i % colors.length],
        stack: 'stack1'
    }));

    new Chart(ctx, {
        type: 'bar',
        data: { labels: dates, datasets: datasets },
        options: {
            responsive: true,
            scales: {
                x: { stacked: true, title: { display: true, text: 'Date' } },
                y: { stacked: true, title: { display: true, text: 'Spending (₹)' } }
            },
            plugins: { legend: { position: 'bottom' } }
        }
    });
}
