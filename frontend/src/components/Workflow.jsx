import {
  CheckCircle2,
  Circle,
  Database,
  Search,
  ShieldCheck,
  Play,
  Brain,
  FileCheck,
  MessageSquareText,
} from "lucide-react";


const icons = {
  understand_question: Brain,
  select_tables: Database,
  generate_sql: Search,
  fallback_analysis: Brain,
  validate_sql: ShieldCheck,
  execute_query: Play,
  validate_result: FileCheck,
  explain_result: MessageSquareText,
};


const labels = {
  understand_question: "Understand Question",
  select_tables: "Select Tables",
  generate_sql: "Generate Analysis",
  fallback_analysis: "Fallback Analysis",
  validate_sql: "Validate SQL",
  execute_query: "Execute Query",
  validate_result: "Validate Result",
  explain_result: "Explain Result",
};


export default function Workflow({ workflow = [] }) {

  if (!workflow.length) {
    return null;
  }


  return (
    <div className="workflow-card">

      <div className="panel-header">
        <div>
          <div className="panel-title">
            Agent Workflow
          </div>

          <div className="panel-subtitle">
            Transparent reasoning pipeline
          </div>
        </div>

        <div className="workflow-badge">
          {workflow.length} steps
        </div>
      </div>


      <div className="workflow-list">

        {workflow.map((step, index) => {

          const Icon =
            icons[step.step] || Circle;

          const completed =
            step.status === "completed";

          const failed =
            step.status === "failed";


          return (
            <div
              className="workflow-step"
              key={`${step.step}-${index}`}
            >

              <div
                className={`workflow-icon ${
                  completed
                    ? "completed"
                    : failed
                    ? "failed"
                    : ""
                }`}
              >
                <Icon size={16} />
              </div>


              <div className="workflow-info">

                <div className="workflow-step-title">
                  {labels[step.step] || step.step}
                </div>

                <div className="workflow-step-message">
                  {step.message}
                </div>

                {step.tables && (
                  <div className="workflow-tables">
                    {step.tables.map((table) => (
                      <span key={table}>
                        {table}
                      </span>
                    ))}
                  </div>
                )}

              </div>


              <div className="workflow-check">

                {completed ? (
                  <CheckCircle2
                    size={17}
                  />
                ) : failed ? (
                  "!"
                ) : (
                  "•"
                )}

              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
}