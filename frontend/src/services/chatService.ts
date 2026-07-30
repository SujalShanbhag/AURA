import api from "../api/client";

let conversationId: string | null = null;

export async function sendChat(message: string) {
  const response = await api.post("/chat", {
    message,
    conversation_id: conversationId,
    metadata: {},
  });

  conversationId = response.data.conversation_id;

  return response.data;
}