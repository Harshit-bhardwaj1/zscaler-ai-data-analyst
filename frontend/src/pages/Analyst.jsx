import {
  Send,
  Sparkles,
  Database,
  ShieldCheck,
  BarChart3,
  Loader2,
} from "lucide-react";

import { useEffect, useRef, useState } from "react";

import {
  askAnalyst,
  getHealth,
} from "../services/api";

import Sidebar from "../components/Sidebar";
import ChatMessage from "../components/ChatMessage";
import Workflow from "../components/Workflow";
import EvidenceTable from "../components/EvidenceTable";
import SqlPanel from "../components/SqlPanel";


const initialMessage = {
  role: "assistant",
  content:
    "Hello! I'm your AI Data Analyst. Ask me a business question about the available customer, subscription, usage, support, or revenue data.",
};


export default function Analyst() {

  const [messages, setMessages] =
    useState([initialMessage]);

  const [input, setInput] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [health, setHealth] =
    useState(false);

  const bottomRef =
    useRef(null);


  useEffect(() => {

    checkHealth();

  }, []);


  useEffect(() => {

    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages, loading]);


  async function checkHealth() {

    try {

      const result = await getHealth();

      setHealth(result.status === "healthy");

    } catch {

      setHealth(false);

    }
  }


  function newChat() {

    setMessages([initialMessage]);

    setInput("");
  }


  function useExample(question) {

    setInput(question);
  }


  async function sendMessage() {

    const question = input.trim();

    if (!question || loading) {
      return;
    }


    const userMessage = {
      role: "user",
      content: question,
    };


    const previousHistory = messages
      .filter(
        (message) =>
          message.role === "user" ||
          message.role === "assistant"
      )
      .slice(-10)
      .map((message) => ({
        role: message.role,
        content:
          message.content ||
          message.result?.answer ||
          "",
      }));


    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setInput("");
    setLoading(true);


    try {

      const result = await askAnalyst(
        question,
        previousHistory
      );


      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          result,
        },
      ]);

    } catch (error) {

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          result: {
            success: false,
            answer:
              error?.response?.data?.detail ||
              "Unable to connect to the backend. Make sure FastAPI is running on port 8000.",
          },
        },
      ]);

    } finally {

      setLoading(false);
    }
  }


  function handleKeyDown(event) {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  }


  const latestResult = [...messages]
    .reverse()
    .find(
      (message) =>
        message.role === "assistant" &&
        message.result
    )?.result;


  return (
    <div className="app-shell">

      <Sidebar
        onNewChat={newChat}
        onExample={useExample}
      />


      <main className="main-area">

        <header className="topbar">

          <div>
            <h1>
              AI Data Analyst
            </h1>

            <p>
              Ask questions across multiple business tables
            </p>
          </div>


          <div
            className={`connection-status ${
              health ? "online" : "offline"
            }`}
          >
            <span />

            {health
              ? "Database connected"
              : "Backend offline"}
          </div>

        </header>


        <div className="content-area">

          <section className="chat-section">

            <div className="chat-container">

              {messages.map(
                (message, index) => (
                  <ChatMessage
                    key={index}
                    message={message}
                  />
                )
              )}


              {loading && (
                <div className="message-row assistant-row">

                  <div className="message-avatar bot-avatar">
                    <Sparkles size={18} />
                  </div>

                  <div className="message-content">

                    <div className="message-name">
                      AI Data Analyst
                    </div>

                    <div className="message-bubble assistant-bubble loading-bubble">

                      <Loader2
                        size={17}
                        className="spin"
                      />

                      Analyzing your question...

                    </div>

                  </div>

                </div>
              )}


              <div ref={bottomRef} />

            </div>


            <div className="composer-wrapper">

              <div className="composer">

                <textarea
                  value={input}
                  onChange={(event) =>
                    setInput(event.target.value)
                  }
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a business question..."
                  rows={1}
                  disabled={loading}
                />


                <button
                  className="send-btn"
                  onClick={sendMessage}
                  disabled={
                    loading ||
                    !input.trim()
                  }
                >
                  {loading ? (
                    <Loader2
                      size={19}
                      className="spin"
                    />
                  ) : (
                    <Send size={19} />
                  )}
                </button>

              </div>

              <div className="composer-hint">
                Press Enter to analyze • Shift + Enter for a new line
              </div>

            </div>

          </section>


          <aside className="insights-panel">

            {latestResult ? (
              <>

                <Workflow
                  workflow={
                    latestResult.workflow
                  }
                />


                <div className="info-card">

                  <div className="info-card-title">
                    <Database size={16} />
                    Tables Used
                  </div>

                  <div className="table-tags">

                    {(
                      latestResult.tables_used ||
                      []
                    ).map((table) => (
                      <span key={table}>
                        {table}
                      </span>
                    ))}

                  </div>

                </div>


                <SqlPanel
                  sql={latestResult.sql}
                />


                <EvidenceTable
                  columns={
                    latestResult.columns
                  }
                  rows={
                    latestResult.evidence
                  }
                />


                {latestResult.assumptions?.length >
                  0 && (
                  <div className="info-card">

                    <div className="info-card-title">
                      <ShieldCheck size={16} />
                      Assumptions
                    </div>

                    <ul className="assumptions">

                      {latestResult.assumptions.map(
                        (item, index) => (
                          <li key={index}>
                            {item}
                          </li>
                        )
                      )}

                    </ul>

                  </div>
                )}

              </>
            ) : (

              <div className="empty-insights">

                <div className="empty-icon">
                  <BarChart3 size={25} />
                </div>

                <h3>
                  Analysis Evidence
                </h3>

                <p>
                  Ask a question to see the
                  selected tables, workflow,
                  generated SQL and evidence.
                </p>

              </div>

            )}

          </aside>

        </div>

      </main>

    </div>
  );
}