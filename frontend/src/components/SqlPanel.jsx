import {
  Code2,
  Copy,
  Check,
} from "lucide-react";

import { useState } from "react";


export default function SqlPanel({
  sql,
}) {

  const [copied, setCopied] =
    useState(false);


  if (!sql) {
    return null;
  }


  async function copySql() {

    await navigator.clipboard.writeText(sql);

    setCopied(true);

    setTimeout(() => {
      setCopied(false);
    }, 1500);
  }


  return (
    <div className="sql-card">

      <div className="panel-header">

        <div>
          <div className="panel-title">
            <Code2 size={17} />
            Generated SQL
          </div>

          <div className="panel-subtitle">
            Validated before execution
          </div>
        </div>


        <button
          className="copy-btn"
          onClick={copySql}
        >
          {copied ? (
            <>
              <Check size={15} />
              Copied
            </>
          ) : (
            <>
              <Copy size={15} />
              Copy
            </>
          )}
        </button>

      </div>


      <pre className="sql-code">
        {sql}
      </pre>

    </div>
  );
}