import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export async function askAnalyst(question, conversationHistory = []) {
  const response = await api.post("/api/chat", {
    question,
    conversation_history: conversationHistory,
  });

  return response.data;
}

export async function getTables() {
  const response = await api.get("/api/tables");

  return response.data;
}

export async function getHealth() {
  const response = await api.get("/health");

  return response.data;
}

export default api;