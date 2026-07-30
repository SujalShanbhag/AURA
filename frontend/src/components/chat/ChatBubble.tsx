import { memo } from "react";
import {
  StyleSheet,
  Text,
  View,
} from "react-native";

import { BlurView } from "expo-blur";
import Markdown from "react-native-markdown-display";

import { ChatMessage } from "../../types/chat";

interface Props {
  message: ChatMessage;
  typing?: boolean;
}

function ChatBubble({
  message,
  typing = false,
}: Props) {
  const isUser = message.role === "user";

  return (
    <View
      style={[
        styles.wrapper,
        isUser
          ? styles.userWrapper
          : styles.aiWrapper,
      ]}
    >
      <BlurView
        intensity={25}
        tint="dark"
        style={[
          styles.bubble,
          isUser
            ? styles.userBubble
            : styles.aiBubble,
        ]}
      >
        {!isUser && (
          <Text style={styles.name}>
            AURA
          </Text>
        )}

        {isUser ? (
          <Text style={styles.userText}>
            {message.message}
          </Text>
        ) : (
          <Markdown
            style={{
              body: styles.aiText,
              paragraph: styles.aiText,
              strong: styles.bold,
              code_inline: styles.inlineCode,
              code_block: styles.codeBlock,
              fence: styles.codeBlock,
            }}
          >
            {typing
              ? `${message.message}▋`
              : message.message}
          </Markdown>
        )}

        <Text style={styles.time}>
          {new Date(
            message.createdAt
          ).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Text>
      </BlurView>
    </View>
  );
}

export default memo(ChatBubble);

const styles = StyleSheet.create({
  wrapper: {
    marginVertical: 8,
    paddingHorizontal: 10,
  },

  userWrapper: {
    alignItems: "flex-end",
  },

  aiWrapper: {
    alignItems: "flex-start",
  },

  bubble: {
    maxWidth: "88%",
    borderRadius: 22,
    padding: 16,
    overflow: "hidden",
  },

  userBubble: {
    backgroundColor: "rgba(108,99,255,0.95)",
  },

  aiBubble: {
    backgroundColor: "rgba(28,36,58,0.82)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.06)",
  },

  name: {
    color: "#8F9BFF",
    fontWeight: "700",
    marginBottom: 8,
    fontSize: 13,
  },

  userText: {
    color: "#fff",
    fontSize: 16,
    lineHeight: 24,
  },

  aiText: {
    color: "#fff",
    fontSize: 16,
    lineHeight: 24,
  },

  bold: {
    fontWeight: "700",
    color: "#fff",
  },

  inlineCode: {
    backgroundColor: "#222C46",
    color: "#8EE3FF",
    padding: 4,
    borderRadius: 6,
    fontFamily: "monospace",
  },

  codeBlock: {
    backgroundColor: "#111827",
    color: "#8EE3FF",
    padding: 14,
    borderRadius: 12,
    fontFamily: "monospace",
    marginVertical: 8,
  },

  time: {
    marginTop: 10,
    color: "#888",
    fontSize: 11,
    alignSelf: "flex-end",
  },
});