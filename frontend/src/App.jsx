
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const PAGE_CSS = `
  * { box-sizing: border-box; }

  body {
    margin: 0;
    background: #f3f6fb;
    color: #172b4d;
    font-family: Arial, sans-serif;
  }

  button, input, textarea, select { font: inherit; }

  .app-shell {
    display: flex;
    min-height: 100vh;
    background: #f3f6fb;
    color: #172b4d;
  }

  .sidebar {
    width: 260px;
    min-height: 100vh;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    padding: 30px 20px;
    background: #142642;
    color: #fff;
  }

  .brand {
    margin: 0 0 8px;
    color: #fff;
    font-size: 29px;
  }

  .brand-subtitle { color: #bdcbe0; margin-bottom: 42px; }

  .sidebar nav { display: grid; gap: 9px; }

  .nav-item {
    width: 100%;
    padding: 13px;
    border: 0;
    border-radius: 9px;
    background: transparent;
    color: #d7e2f2;
    text-align: left;
    cursor: pointer;
  }

  .nav-item:hover, .nav-item.active {
    background: #2b4772;
    color: #fff;
  }

  .sidebar-footer {
    margin-top: auto;
    padding-top: 45px;
    color: #cbd7e8;
    font-size: 13px;
  }

  .status-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    margin-right: 8px;
    border-radius: 50%;
    background: #36ce91;
  }

  .main-content {
    flex: 1;
    min-width: 0;
    padding: 32px;
    color: #172b4d;
  }

  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 28px;
  }

  .topbar h1 { margin: 8px 0; color: #172b4d; font-size: 28px; }

  .eyebrow {
    color: #4266a3;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
  }

  .profile { display: flex; align-items: center; gap: 10px; color: #172b4d; }

  .avatar {
    display: grid;
    place-items: center;
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: #e2eaff;
    color: #2457bb;
    font-weight: 700;
  }

  .welcome-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 42px;
    border-radius: 18px;
    background: linear-gradient(120deg, #254a83, #456bd0);
    color: #fff;
  }

  .welcome-banner h2 {
    margin: 16px 0;
    color: #fff;
    font-size: clamp(25px, 3vw, 36px);
  }

  .welcome-banner p { color: #edf3ff; line-height: 1.7; }
  .welcome-banner .eyebrow { color: #fff; }
  .banner-icon { font-size: 48px; color: #fff; }

  .section { margin: 30px 0; }
  .section h2 { color: #172b4d; }

  .service-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
  }

  .service-card {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    min-height: 220px;
    padding: 23px;
    border: 1px solid #dce5f1;
    border-radius: 14px;
    background: #fff;
    text-align: left;
    cursor: pointer;
  }

  .service-card:hover { border-color: #4269c8; transform: translateY(-2px); }
  .service-icon { font-size: 27px; }
  .service-card h3 { color: #172b4d; }
  .service-card p { color: #586d8b; line-height: 1.7; }
  .card-link { margin-top: auto; color: #2457bb; font-weight: 700; }

  .assistant-panel {
    display: flex;
    gap: 18px;
    align-items: flex-start;
    margin-top: 25px;
    padding: 25px;
    border: 1px solid #dce5f1;
    border-radius: 14px;
    background: #fff;
  }

  .assistant-avatar {
    display: grid;
    place-items: center;
    min-width: 42px;
    height: 42px;
    border-radius: 12px;
    background: #e5edff;
    color: #315bc0;
    font-size: 23px;
  }

  .assistant-panel h3 { margin-top: 4px; color: #172b4d; }
  .assistant-panel p { color: #586d8b; line-height: 1.6; }

  .incident-panel {
    max-width: 950px;
    margin: 0 auto;
    padding: 30px;
    border: 1px solid #dce5f1;
    border-radius: 16px;
    background: #fff;
    box-shadow: 0 4px 18px rgba(20, 38, 66, 0.04);
  }

  .incident-panel h2 { color: #172b4d; }
  .panel-description { color: #586d8b; line-height: 1.7; }

  .back-button {
    padding: 5px 0;
    border: 0;
    background: transparent;
    color: #2457bb;
    cursor: pointer;
  }

  .incident-panel label {
    display: block;
    margin: 20px 0 9px;
    color: #172b4d;
    font-weight: 700;
  }

  .incident-panel textarea,
  .incident-panel input,
  .incident-panel select {
    display: block;
    width: 100%;
    padding: 13px;
    border: 1px solid #bdcbe0;
    border-radius: 8px;
    outline: none;
    background: #fff;
    color: #172b4d;
  }

  .incident-panel textarea { min-height: 130px; resize: vertical; }
  .incident-panel textarea:focus,
  .incident-panel input:focus,
  .incident-panel select:focus { border-color: #315bc0; }

  .incident-panel textarea::placeholder,
  .incident-panel input::placeholder { color: #75849a; }

  .character-count { color: #75849a; text-align: right; font-size: 13px; }

  .primary-button, .secondary-button {
    display: inline-block;
    margin-top: 16px;
    padding: 12px 20px;
    border: 0;
    border-radius: 8px;
    background: #315bc0;
    color: #fff;
    cursor: pointer;
  }

  .primary-button:hover, .secondary-button:hover { background: #24489f; }
  .primary-button:disabled { opacity: .65; cursor: wait; }

  .error-message {
    margin: 16px 0;
    padding: 13px;
    border: 1px solid #f0caca;
    border-radius: 8px;
    background: #fff0f0;
    color: #a51d25;
    overflow-wrap: anywhere;
  }

  .analysis-result {
    margin-top: 26px;
    padding: 22px;
    border: 1px solid #dce5f1;
    border-radius: 12px;
    background: #fff;
  }

  .analysis-result h3, .analysis-result h4 { color: #172b4d; }

  .result-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin: 20px 0;
  }

  .result-field {
    min-width: 0;
    padding: 14px;
    border-radius: 8px;
    background: #f0f5fc;
  }

  .result-field span {
    display: block;
    margin-bottom: 8px;
    color: #586d8b;
    font-size: 13px;
  }

  .result-field strong {
    color: #172b4d;
    overflow-wrap: anywhere;
  }

  .resolution-box {
    padding: 18px;
    border-left: 4px solid #315bc0;
    border-radius: 5px;
    background: #f0f5fc;
    color: #172b4d;
    line-height: 1.7;
  }

  .resolution-box h4, .resolution-box p, .resolution-box li { color: #172b4d; }
  .placeholder-panel { padding: 30px; background: #fff; border-radius: 14px; }

  @media (max-width: 900px) {
    .sidebar { width: 220px; }
    .main-content { padding: 22px; }
    .service-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .result-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }

  @media (max-width: 600px) {
    .app-shell { flex-direction: column; }
    .sidebar { width: 100%; min-height: auto; padding: 20px; }
    .brand-subtitle { margin-bottom: 18px; }
    .sidebar nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .sidebar-footer { padding-top: 20px; }
    .main-content { padding: 16px; }
    .topbar { align-items: flex-start; }
    .welcome-banner { padding: 25px; }
    .banner-icon { display: none; }
    .service-grid, .result-grid { grid-template-columns: 1fr; }
    .incident-panel { padding: 20px; }
  }
`;

function App() {
  const [activeTab, setActiveTab] = useState("Home");
  const [description, setDescription] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [question, setQuestion] = useState("");
  const [knowledge, setKnowledge] = useState(null);
  const [username, setUsername] = useState("demo.employee");
  const [software, setSoftware] = useState("Visual Studio Code");
  const [softwareResult, setSoftwareResult] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string" ? data.detail : "Request failed."
      );
    }

    return data;
  }

  function navigate(tab) {
    setActiveTab(tab);
    setError("");
    setAnalysis(null);
    setKnowledge(null);
    setSoftwareResult(null);

    if (tab === "My Tickets") {
      loadTickets();
    }
  }

  async function analyzeIssue(event) {
    event.preventDefault();
    setError("");
    setAnalysis(null);
    setLoading(true);

    try {
      const data = await apiRequest("/api/incidents/analyze", {
        method: "POST",
        body: JSON.stringify({
          description: description.trim(),
          username,
        }),
      });
      setAnalysis(data);
    } catch (err) {
      setError(err.message || "Cannot connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  async function askKnowledge(event) {
    event.preventDefault();
    setError("");
    setKnowledge(null);
    setLoading(true);

    try {
      const data = await apiRequest("/api/knowledge/ask", {
        method: "POST",
        body: JSON.stringify({ description: question.trim() }),
      });
      setKnowledge(data);
    } catch (err) {
      setError(err.message || "Could not search the knowledge base.");
    } finally {
      setLoading(false);
    }
  }

  async function requestSoftware(event) {
    event.preventDefault();
    setError("");
    setSoftwareResult(null);
    setLoading(true);

    try {
      const data = await apiRequest("/api/provisioning/request", {
        method: "POST",
        body: JSON.stringify({ username, software }),
      });
      setSoftwareResult(data);
    } catch (err) {
      setError(err.message || "Could not submit software request.");
    } finally {
      setLoading(false);
    }
  }

  async function loadTickets() {
    setError("");
    setLoading(true);

    try {
      const data = await apiRequest("/api/incidents");
      setTickets(Array.isArray(data) ? data : data.incidents || []);
    } catch (err) {
      setTickets([]);
      setError(err.message || "Could not load tickets.");
    } finally {
      setLoading(false);
    }
  }

  function renderHome() {
    return (
      <>
        <section className="welcome-banner">
          <div>
            <p className="eyebrow">YOUR IT SUPPORT ASSISTANT</p>
            <h2>How can we help you today?</h2>
            <p>Get answers, report problems, and request software from one place.</p>
          </div>
          <div className="banner-icon">✦</div>
        </section>

        <section className="section">
          <h2>What do you need help with?</h2>
          <div className="service-grid">
            <button className="service-card" onClick={() => navigate("Report an Issue")}>
              <span className="service-icon">🎫</span>
              <h3>Report an Issue</h3>
              <p>Report VPN, login, network, or other IT problems.</p>
              <span className="card-link">Get support →</span>
            </button>

            <button className="service-card" onClick={() => navigate("Knowledge Base")}>
              <span className="service-icon">📚</span>
              <h3>Find an Answer</h3>
              <p>Search IT guides and troubleshooting solutions.</p>
              <span className="card-link">Browse guides →</span>
            </button>

            <button className="service-card" onClick={() => navigate("Software Requests")}>
              <span className="service-icon">💻</span>
              <h3>Request Software</h3>
              <p>Request tools such as VS Code for your work.</p>
              <span className="card-link">View catalogue →</span>
            </button>
          </div>
        </section>

        <section className="assistant-panel">
          <div className="assistant-avatar">✦</div>
          <div>
            <h3>Meet your AI IT assistant</h3>
            <p>Ask a question, troubleshoot a problem, or find the right IT service.</p>
            <button className="primary-button" onClick={() => navigate("Knowledge Base")}>
              Explore assistance →
            </button>
          </div>
        </section>
      </>
    );
  }

  function renderIncidentForm() {
    return (
      <section className="incident-panel">
        <button className="back-button" onClick={() => navigate("Home")}>
          ← Back to Home
        </button>

        <h2>Report an IT issue</h2>
        <p className="panel-description">
          Describe what happened. Sorim.AI will analyze your issue and suggest next steps.
        </p>

        <form onSubmit={analyzeIssue}>
          <label htmlFor="incident-description">Describe your problem</label>
          <textarea
            id="incident-description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Example: My VPN is not connecting and I cannot access the company network."
            rows={5}
            maxLength={2000}
            required
          />
          <p className="character-count">{description.length}/2000 characters</p>

          {error && <div className="error-message" role="alert">{error}</div>}

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Analyzing issue..." : "Analyze Issue →"}
          </button>
        </form>

        {analysis && (
          <div className="analysis-result">
            <p className="eyebrow">INCIDENT ANALYSIS</p>
            <h3>Analysis complete</h3>

            <div className="result-grid">
              {[
                ["Ticket ID", analysis.ticket_id],
                ["Ticket type", analysis.ticket_type],
                ["Category", analysis.category],
                ["Priority", analysis.priority],
                ["Impact", analysis.impact],
                ["Urgency", analysis.urgency],
                ["Assignment group", analysis.assignment_group],
                ["Status", analysis.status],
              ].map(([label, value]) => (
                <div className="result-field" key={label}>
                  <span>{label}</span>
                  <strong>{value ?? "Not available"}</strong>
                </div>
              ))}
            </div>

            <div className="resolution-box">
              <h4>Suggested resolution</h4>
              {Array.isArray(analysis.suggested_resolution) ? (
                <ul>
                  {analysis.suggested_resolution.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ul>
              ) : (
                <p>{analysis.suggested_resolution || "No resolution provided."}</p>
              )}
            </div>

            {analysis.escalation_reason && <p>Escalation: {analysis.escalation_reason}</p>}

            <p>
              Status: {analysis.status || "Open"}. This demo creates an incident
              record in the local database; ServiceNow integration is not configured.
            </p>

            <button
              className="secondary-button"
              onClick={() => {
                setDescription("");
                setAnalysis(null);
                setError("");
              }}
            >
              Report another issue
            </button>
          </div>
        )}
      </section>
    );
  }

  function renderKnowledgeBase() {
    return (
      <section className="incident-panel">
        <h2>Knowledge Base</h2>
        <p className="panel-description">
          Ask an IT question to search help documents and get a grounded answer.
        </p>

        <form onSubmit={askKnowledge}>
          <label htmlFor="knowledge-question">Your question</label>
          <textarea
            id="knowledge-question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Example: My Outlook is not syncing emails. How can I fix it?"
            rows={4}
            required
          />
          {error && <div className="error-message" role="alert">{error}</div>}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Searching..." : "Ask AI →"}
          </button>
        </form>

        {knowledge && (
          <div className="analysis-result">
            <h3>Answer</h3>
            <p>{knowledge.answer}</p>
            <h4>Sources</h4>
            {knowledge.sources?.length ? (
              <ul>
                {knowledge.sources.map((source, index) => (
                  <li key={index}>{source}</li>
                ))}
              </ul>
            ) : (
              <p>
                {knowledge.found
                  ? "No source filenames were returned."
                  : "No matching knowledge found. Contact IT Support for help."}
              </p>
            )}
          </div>
        )}
      </section>
    );
  }

  function renderSoftwareRequests() {
    return (
      <section className="incident-panel">
        <h2>Software Requests</h2>
        <p className="panel-description">
          Submit a software request. Provisioning is simulated in this demo.
        </p>

        <form onSubmit={requestSoftware}>
          <label htmlFor="username">Employee username</label>
          <input
            id="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />

          <label htmlFor="software">Software</label>
          <select
            id="software"
            value={software}
            onChange={(event) => setSoftware(event.target.value)}
          >
            <option>Visual Studio Code</option>
            <option>Google Chrome</option>
            <option>Slack</option>
            <option>Zoom</option>
          </select>

          {error && <div className="error-message" role="alert">{error}</div>}

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Submitting..." : "Submit Request →"}
          </button>
        </form>

        {softwareResult && (
          <div className="analysis-result">
            <h3>Request submitted</h3>
            <p><strong>Request ID:</strong> {softwareResult.request_id}</p>
            <p><strong>Software:</strong> {softwareResult.software}</p>
            <p><strong>Status:</strong> {softwareResult.status}</p>
            <p>{softwareResult.message}</p>
          </div>
        )}
      </section>
    );
  }

  function renderTickets() {
    return (
      <section className="incident-panel">
        <h2>My Tickets</h2>
        <p className="panel-description">Incidents saved in the local helpdesk database.</p>

        {loading && <p>Loading tickets...</p>}
        {!loading && tickets.length === 0 && !error && <p>No tickets found.</p>}

        {tickets.map((ticket, index) => (
          <div
            className="analysis-result"
            key={ticket.id ?? ticket.ticket_id ?? index}
          >
            <h3>Ticket #{ticket.id ?? ticket.ticket_id ?? index + 1}</h3>
            <p>{ticket.description}</p>
            <p><strong>Category:</strong> {ticket.category || "Not available"}</p>
            <p><strong>Priority:</strong> {ticket.priority || "Not available"}</p>
            <p><strong>Status:</strong> {ticket.status || "Open"}</p>
          </div>
        ))}

        {error && <div className="error-message" role="alert">{error}</div>}
        <button className="secondary-button" onClick={loadTickets} disabled={loading}>
          Refresh tickets
        </button>
      </section>
    );
  }

  return (
    <>
      <style>{PAGE_CSS}</style>

      <div className="app-shell">
        <aside className="sidebar">
          <h2 className="brand">Sorim.AI</h2>
          <p className="brand-subtitle">IT Service Desk</p>

          <nav>
            {["Home", "My Tickets", "Knowledge Base", "Software Requests"].map((tab) => (
              <button
                key={tab}
                className={`nav-item ${activeTab === tab ? "active" : ""}`}
                onClick={() => navigate(tab)}
              >
                {tab}
              </button>
            ))}

            {activeTab === "Report an Issue" && (
              <button className="nav-item active">Report an Issue</button>
            )}
          </nav>

          <div className="sidebar-footer">
            <span className="status-dot" />
            AI Assistant Ready
          </div>
        </aside>

        <main className="main-content">
          <header className="topbar">
            <div>
              <p className="eyebrow">EMPLOYEE PORTAL</p>
              <h1>{activeTab === "Report an Issue" ? "IT Support" : activeTab}</h1>
            </div>
            <div className="profile">
              <div className="avatar">E</div>
              <span>Employee</span>
            </div>
          </header>

          {error &&
            activeTab !== "Report an Issue" &&
            activeTab !== "Knowledge Base" &&
            activeTab !== "Software Requests" &&
            activeTab !== "My Tickets" && (
              <div className="error-message" role="alert">{error}</div>
            )}

          {activeTab === "Home" && renderHome()}
          {activeTab === "Report an Issue" && renderIncidentForm()}
          {activeTab === "Knowledge Base" && renderKnowledgeBase()}
          {activeTab === "Software Requests" && renderSoftwareRequests()}
          {activeTab === "My Tickets" && renderTickets()}
        </main>
      </div>
    </>
  );
}

export default App;
