import api from "../api";

interface ChatRequest {
  message: string;
  conversation_id?: string;
  metadata?: Record<string, any>;
}

interface StreamCallbacks {
  onStart?: () => void;
  onToken: (token: string) => void;
  onFinish?: (fullResponse: string) => void;
  onError?: (error: unknown) => void;
}

export async function streamChat(
  body: ChatRequest,
  callbacks: StreamCallbacks
) {
  callbacks.onStart?.();

  try {
    const { data } = await api.post("/api/v1/chat", body);

    const response: string = data.response ?? "";
    let current = "";

    for (const character of response) {
      current += character;
      callbacks.onToken(character);

      await new Promise((resolve) =>
        setTimeout(resolve, 12)
      );
    }

    callbacks.onFinish?.(current);
  } catch (error) {
    callbacks.onError?.(error);
  }
}