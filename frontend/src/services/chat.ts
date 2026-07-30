import api from "./api";

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  provider: string;
  model: string;
  created_at: string;
}

export async function sendMessage(
  body: ChatRequest,
  token?: string
): Promise<ChatResponse> {
  const response = await api.post(
    "/api/v1/chat",
    body,
    {
      headers: token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {},
    }
  );

  return response.data;
}