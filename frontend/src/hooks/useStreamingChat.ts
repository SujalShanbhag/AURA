import { useState } from "react";

export function useStreamingChat() {
  const [typing, setTyping] = useState(false);

  async function streamText(
    text: string,
    callback: (value: string) => void
  ) {
    setTyping(true);

    let output = "";

    for (const char of text) {
      output += char;

      callback(output);

      await new Promise((r) => setTimeout(r, 18));
    }

    setTyping(false);
  }

  return {
    typing,
    streamText,
  };
}