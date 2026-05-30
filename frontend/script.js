const API_BASE = "http://127.0.0.1:5000";

async function askQuery() {
    const query = document.getElementById("queryInput").value;

    const response = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: query })
    });

    const data = await response.json();

    document.getElementById("result").textContent =
        JSON.stringify(data, null, 2);
}

async function getInsights() {
    const response = await fetch(`${API_BASE}/insights`);
    const data = await response.json();

    const list = document.getElementById("insightsList");
    list.innerHTML = "";

    data.insights.forEach(insight => {
        const li = document.createElement("li");
        li.textContent = insight;
        list.appendChild(li);
    });
}