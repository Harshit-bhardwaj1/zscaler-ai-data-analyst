import { useState } from "react";
import {
  BarChart3,
  Database,
  MessageSquare,
  Send,
  Sparkles,
  Table2,
  ChevronRight,
  Loader2,
  Bot,
  User,
} from "lucide-react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const exampleQuestions = [
  "Which customer has the highest churn risk?",
  "Which region has the highest MRR?",
  "Which customers expanded recently?",
  "Which segment has the highest average adoption?",
];

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTable, setSelectedTable] = useState(null);

  const tables = [
    {
      name: "customers",
      description: "Customer and company information",
    },
    {
      name: "subscriptions",
      description: "Subscription and MRR information",
    },
    {
      name: "usage",
      description: "Monthly product usage and adoption",
    },
    {
      name: "support_tickets",
      description: "Customer support issues",
    },
    {
      name: "revenue_events",
      description: "Revenue changes and events",
    },
  ];

  const askQuestion = async (text = question) => {
    const userQuestion = text.trim();

    if (!userQuestion || loading) {
      return;
    }

    setQuestion("");

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: userQuestion,
    };

    // Save the user message immediately for the UI.
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      /*
       * IMPORTANT:
       *
       * The backend needs the previous assistant result, including:
       * - answer
       * - evidence
       * - tables_used
       * - sql
       * - columns
       * - assumptions
       *
       * This allows follow-up questions to reuse the previous analysis.
       */
      const conversationHistory = messages.map((message) => {
        const historyItem = {
          role: message.role,
          content: message.content,
        };

        // Preserve the complete backend result for assistant messages.
        if (message.role === "assistant" && message.data) {
          historyItem.result = message.data;
        }

        return historyItem;
      });

      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
          conversation_history: conversationHistory,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.answer || "No answer was returned.",
        data,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          error.message ||
          "Unable to connect to the analyst backend.",
        error: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    askQuestion();
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={20} />
          </div>

          <div>
            <h1>Data Analyst</h1>
            <span>AI Business Intelligence</span>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={() => {
            setMessages([]);
            setQuestion("");
          }}
        >
          <MessageSquare size={17} />
          New analysis
        </button>

        <div className="sidebar-section">
          <div className="section-title">
            <Database size={15} />
            <span>Data sources</span>
          </div>

          <div className="table-list">
            {tables.map((table) => (
              <button
                key={table.name}
                className={`table-item ${
                  selectedTable === table.name ? "selected" : ""
                }`}
                onClick={() =>
                  setSelectedTable(
                    selectedTable === table.name ? null : table.name
                  )
                }
              >
                <Table2 size={16} />

                <div className="table-info">
                  <strong>{table.name}</strong>
                  <span>{table.description}</span>
                </div>

                <ChevronRight size={14} />
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="status-dot"></div>
          <span>Connected to data</span>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        <header className="topbar">
          <div>
            <div className="topbar-label">
              <BarChart3 size={16} />
              AI DATA ANALYST
            </div>

            <h2>Chat with your business data</h2>
          </div>

          <div className="ai-badge">
            <span className="live-dot"></span>
            Analyst ready
          </div>
        </header>

        <section className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">
                <Sparkles size={30} />
              </div>

              <h3>What would you like to know?</h3>

              <p>
                Ask business questions in plain English. I'll identify the
                relevant tables, analyze the data, validate the result, and
                show you the evidence.
              </p>

              <div className="example-grid">
                {exampleQuestions.map((example) => (
                  <button
                    key={example}
                    className="example-card"
                    onClick={() => askQuestion(example)}
                  >
                    <span>{example}</span>
                    <ChevronRight size={16} />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((message) => (
                <Message
                  key={message.id}
                  message={message}
                />
              ))}

              {loading && (
                <div className="message assistant-message">
                  <div className="avatar assistant-avatar">
                    <Bot size={18} />
                  </div>

                  <div className="message-content">
                    <div className="message-author">AI Analyst</div>

                    <div className="thinking">
                      <Loader2 size={17} className="spin" />
                      <span>
                        Analyzing your question and validating the result...
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Composer */}
        <div className="composer-wrapper">
          <form
            className="composer"
            onSubmit={handleSubmit}
          >
            <div className="composer-icon">
              <Sparkles size={19} />
            </div>

            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question about your business data..."
              disabled={loading}
            />

            <button
              type="submit"
              className="send-button"
              disabled={!question.trim() || loading}
            >
              {loading ? (
                <Loader2 size={19} className="spin" />
              ) : (
                <Send size={19} />
              )}
            </button>
          </form>

          <p className="composer-hint">
            AI can make mistakes. Review the evidence before making business
            decisions.
          </p>
        </div>
      </main>
    </div>
  );
}

function Message({ message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="message user-message">
        <div className="avatar user-avatar">
          <User size={17} />
        </div>

        <div className="message-content">
          <div className="message-author">You</div>
          <div className="user-text">{message.content}</div>
        </div>
      </div>
    );
  }

  const data = message.data;

  return (
    <div className="message assistant-message">
      <div className="avatar assistant-avatar">
        <Bot size={18} />
      </div>

      <div className="message-content">
        <div className="message-author">AI Analyst</div>

        <div className={`answer ${message.error ? "error-answer" : ""}`}>
          {message.content}
        </div>

        {data && <Evidence data={data} />}
      </div>
    </div>
  );
}

function Evidence({ data }) {
  return (
    <div className="evidence">
      {data.workflow && data.workflow.length > 0 && (
        <div className="evidence-card">
          <div className="evidence-title">
            <Sparkles size={15} />
            Analysis workflow
          </div>

          <div className="workflow">
            {data.workflow.map((step, index) => (
              <div
                className="workflow-step"
                key={index}
              >
                <div className="workflow-number">
                  {index + 1}
                </div>

                <div>
                  <strong>
                    {step.step || step.name || `Step ${index + 1}`}
                  </strong>

                  {step.status && (
                    <span className="workflow-status">
                      {step.status}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.tables_used && data.tables_used.length > 0 && (
        <div className="evidence-card">
          <div className="evidence-title">
            <Database size={15} />
            Tables used
          </div>

          <div className="chips">
            {data.tables_used.map((table) => (
              <span
                className="chip"
                key={table}
              >
                {table}
              </span>
            ))}
          </div>
        </div>
      )}

      {data.evidence && data.evidence.length > 0 && (
        <div className="evidence-card">
          <div className="evidence-title">
            <Table2 size={15} />
            Evidence
          </div>

          <div className="evidence-table-wrapper">
            <table>
              <thead>
                <tr>
                  {Object.keys(data.evidence[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {data.evidence.map((row, index) => (
                  <tr key={index}>
                    {Object.keys(data.evidence[0]).map((key) => (
                      <td key={key}>
                        {String(row[key] ?? "-")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {data.assumptions && data.assumptions.length > 0 && (
        <div className="evidence-card assumptions">
          <div className="evidence-title">
            <span>⚠</span>
            Assumptions
          </div>

          <ul>
            {data.assumptions.map((assumption, index) => (
              <li key={index}>{assumption}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;