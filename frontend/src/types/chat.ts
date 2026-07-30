export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  message: string;
  createdAt: string;
}