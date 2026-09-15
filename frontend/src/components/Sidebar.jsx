import {
  BarChart3,
  Database,
  MessageSquare,
  Plus,
  Sparkles,
} from "lucide-react";


export default function Sidebar({
  onNewChat,
  onExample,
}) {
  const examples = [
    "Which customer has the highest churn risk?",
    "Which region has the highest MRR?",
    "What are the recent expansion events?",
    "Which segment has the highest average adoption?",
    "Show customers with low adoption and support tickets.",
  ];


  return (
    <aside className="sidebar">

      <div className="brand">
        <div className="brand-icon">
          <Sparkles size={20} />
        </div>

        <div>
          <div className="brand-title">
            AI Data Analyst
          </div>

          <div className="brand-subtitle">
            Zscaler Product Builder
          </div>
        </div>
      </div>


      <button
        className="new-chat-btn"
        onClick={onNewChat}
      >
        <Plus size={18} />
        New Analysis
      </button>


      <div className="sidebar-section">

        <div className="section-label">
          <MessageSquare size={14} />
          Example Questions
        </div>

        <div className="examples">

          {examples.map((example, index) => (
            <button
              key={index}
              className="example-btn"
              onClick={() => onExample(example)}
            >
              {example}
            </button>
          ))}

        </div>
      </div>


      <div className="sidebar-section">

        <div className="section-label">
          <Database size={14} />
          Data Sources
        </div>

        <div className="data-source">
          <BarChart3 size={16} />

          <div>
            <div className="source-title">
              PostgreSQL
            </div>

            <div className="source-status">
              ● Connected
            </div>
          </div>
        </div>

      </div>


      <div className="sidebar-footer">
        <div className="footer-dot" />
        Prototype Mode
      </div>

    </aside>
  );
}