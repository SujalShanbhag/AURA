import api from "./client";

let conversationId: string | null = null;

export async function sendMessage(message: string) {
  const { data } = await api.post("/chat", {
    message,
    conversation_id: conversationId,
    metadata: {},
  });

  conversationId = data.conversation_id;

  return data;
}