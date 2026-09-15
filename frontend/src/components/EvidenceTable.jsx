import { Table2 } from "lucide-react";


export default function EvidenceTable({
  columns = [],
  rows = [],
}) {

  if (!rows.length) {
    return null;
  }


  return (
    <div className="evidence-card">

      <div className="panel-header">

        <div>
          <div className="panel-title">
            Evidence
          </div>

          <div className="panel-subtitle">
            Data returned from the executed query
          </div>
        </div>

        <div className="evidence-count">
          {rows.length} rows
        </div>

      </div>


      <div className="table-wrapper">

        <table>

          <thead>
            <tr>

              {columns.map((column) => (
                <th key={column}>
                  {column}
                </th>
              ))}

            </tr>
          </thead>


          <tbody>

            {rows.map((row, rowIndex) => (
              <tr key={rowIndex}>

                {columns.map((column) => (
                  <td key={column}>
                    {formatValue(row[column])}
                  </td>
                ))}

              </tr>
            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}


function formatValue(value) {

  if (value === null || value === undefined) {
    return "—";
  }

  if (typeof value === "number") {
    return value.toLocaleString();
  }

  return String(value);
}