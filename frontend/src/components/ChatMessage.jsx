import {
  Bot,
  User,
  AlertCircle,
} from "lucide-react";


export default function ChatMessage({ message }) {

  const isUser = message.role === "user";

  const isError =
    message.result &&
    message.result.success === false;


  return (
    <div
      className={`message-row ${
        isUser ? "user-row" : "assistant-row"
      }`}
    >

      <div
        className={`message-avatar ${
          isUser ? "user-avatar" : "bot-avatar"
        }`}
      >
        {isUser ? (
          <User size={17} />
        ) : (
          <Bot size={18} />
        )}
      </div>


      <div className="message-content">

        <div className="message-name">
          {isUser ? "You" : "AI Data Analyst"}
        </div>


        <div
          className={`message-bubble ${
            isUser ? "user-bubble" : "assistant-bubble"
          } ${
            isError ? "error-bubble" : ""
          }`}
        >

          {isError && (
            <div className="error-title">
              <AlertCircle size={16} />
              Analysis could not be completed
            </div>
          )}

          <div className="message-text">
            {formatMessage(
              message.result?.answer ||
              message.content ||
              ""
            )}
          </div>

        </div>

      </div>

    </div>
  );
}


function formatMessage(text) {

  if (!text) {
    return null;
  }

  const parts = text.split("**");

  return parts.map((part, index) => {

    if (index % 2 === 1) {
      return (
        <strong key={index}>
          {part}
        </strong>
      );
    }

    return (
      <span key={index}>
        {part}
      </span>
    );
  });
}