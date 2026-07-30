import { useState } from "react";
import {
  StyleSheet,
  View,
  FlatList,
  TextInput,
  TouchableOpacity,
  Text,
} from "react-native";

import ChatBubble from "../../components/chat/ChatBubble";
import { ChatMessage } from "../../types/chat";

export default function ChatScreen() {
  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "assistant",
      message: "Hello! I'm AURA 👋",
      createdAt: new Date().toISOString(),
    },
  ]);

  function sendMessage() {
    if (!message.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      message,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setMessage("");
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={messages}
        renderItem={({ item }) => <ChatBubble message={item} />}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
      />

      <View style={styles.bottom}>
        <TextInput
          value={message}
          onChangeText={setMessage}
          placeholder="Message AURA..."
          placeholderTextColor="#777"
          style={styles.input}
        />

        <TouchableOpacity style={styles.button} onPress={sendMessage}>
          <Text style={styles.buttonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#050816",
  },

  list: {
    padding: 16,
  },

  bottom: {
    flexDirection: "row",
    padding: 14,
    borderTopWidth: 1,
    borderTopColor: "#222",
  },

  input: {
    flex: 1,
    backgroundColor: "#1A2238",
    borderRadius: 15,
    color: "#fff",
    paddingHorizontal: 16,
  },

  button: {
    marginLeft: 10,
    backgroundColor: "#6C63FF",
    paddingHorizontal: 20,
    justifyContent: "center",
    borderRadius: 15,
  },

  buttonText: {
    color: "#fff",
    fontWeight: "700",
  },
});