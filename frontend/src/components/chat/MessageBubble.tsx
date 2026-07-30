import { StyleSheet, Text, View } from "react-native";
import { ChatMessage } from "../../types/chat";

export default function MessageBubble({
  message,
}: {
  message: ChatMessage;
}) {
  const user = message.role === "user";

  return (
    <View
      style={[
        styles.bubble,
        user ? styles.user : styles.ai,
      ]}
    >
      <Text style={styles.text}>{message.message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  bubble: {
    padding: 16,
    borderRadius: 22,
    marginVertical: 8,
    maxWidth: "82%",
  },

  user: {
    backgroundColor: "#6C63FF",
    alignSelf: "flex-end",
  },

  ai: {
    backgroundColor: "#18233E",
    alignSelf: "flex-start",
  },

  text: {
    color: "#fff",
    fontSize: 16,
    lineHeight: 24,
  },
});