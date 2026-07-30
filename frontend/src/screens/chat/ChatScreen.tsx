import { useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import { BlurView } from "expo-blur";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";

import ChatBubble from "../../components/chat/ChatBubble";
import VoiceButton from "../../components/voice/VoiceButton";
import AnimatedBackground from "../../components/background/AnimatedBackground";
import AuraOrb from "../../components/avatar/AuraOrb";

import { streamChat } from "../../services/stream/chatStream";
import { speak } from "../../voice/voice";

import { ChatMessage } from "../../types/chat";

type AuraState =
  | "idle"
  | "thinking"
  | "speaking"
  | "listening";

export default function ChatScreen() {
  const flatListRef = useRef<FlatList>(null);

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [auraState, setAuraState] =
    useState<AuraState>("idle");

  const [messages, setMessages] = useState<
    ChatMessage[]
  >([
    {
      id: "welcome",
      role: "assistant",
      message:
        "👋 Hello! I'm AURA.\n\nHow can I help you today?",
      createdAt: new Date().toISOString(),
    },
  ]);

  async function sendMessage() {
    if (!message.trim() || loading) return;

    const text = message.trim();

    setMessage("");
    setLoading(true);
    setAuraState("thinking");

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      message: text,
      createdAt: new Date().toISOString(),
    };

    const aiMessage: ChatMessage = {
      id: `${Date.now()}-ai`,
      role: "assistant",
      message: "",
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
      aiMessage,
    ]);

    let fullResponse = "";

    streamChat(
      {
        message: text,
      },
      {
        onToken(token) {
          fullResponse += token;

          setMessages((prev) =>
            prev.map((item) =>
              item.id === aiMessage.id
                ? {
                    ...item,
                    message: fullResponse,
                  }
                : item
            )
          );

          requestAnimationFrame(() =>
            flatListRef.current?.scrollToEnd({
              animated: true,
            })
          );
        },

        async onFinish(response) {
          setLoading(false);

          setAuraState("speaking");

          if (response.trim()) {
            await speak(response);
          }

          setAuraState("idle");
        },

        onError() {
          setLoading(false);
          setAuraState("idle");

          setMessages((prev) =>
            prev.map((item) =>
              item.id === aiMessage.id
                ? {
                    ...item,
                    message:
                      "⚠️ Unable to connect to AURA backend.",
                  }
                : item
            )
          );
        },
      }
    );
  }

  return (
    <LinearGradient
      colors={["#050816", "#0B1120", "#111827"]}
      style={styles.container}
    >
      <AnimatedBackground />

      <SafeAreaView style={styles.container}>
        <BlurView
          intensity={30}
          tint="dark"
          style={styles.header}
        >
          <View>
            <Text style={styles.title}>
              AURA
            </Text>

            <Text style={styles.subtitle}>
              AI Companion
            </Text>
          </View>

          <TouchableOpacity style={styles.addButton}>
            <Ionicons
              name="add"
              size={24}
              color="#FFF"
            />
          </TouchableOpacity>
        </BlurView>

        <View style={styles.orbContainer}>
          <AuraOrb
            size={120}
            state={auraState}
          />

          <Text style={styles.status}>
            {auraState.toUpperCase()}
          </Text>
        </View>

        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <ChatBubble message={item} />
          )}
          contentContainerStyle={styles.chatList}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() =>
            flatListRef.current?.scrollToEnd({
              animated: true,
            })
          }
        />

        {loading && (
          <View style={styles.loading}>
            <ActivityIndicator color="#6C63FF" />

            <Text style={styles.loadingText}>
              AURA is thinking...
            </Text>
          </View>
        )}

        <KeyboardAvoidingView
          behavior={
            Platform.OS === "ios"
              ? "padding"
              : undefined
          }
        >
          <BlurView
            intensity={35}
            tint="dark"
            style={styles.bottom}
          >
            <TouchableOpacity>
              <Ionicons
                name="attach"
                size={22}
                color="#888"
              />
            </TouchableOpacity>

            <TextInput
              style={styles.input}
              value={message}
              onChangeText={setMessage}
              placeholder="Message AURA..."
              placeholderTextColor="#888"
              multiline
            />

            <VoiceButton
              onPress={() =>
                setAuraState("listening")
              }
            />

            <TouchableOpacity
              style={styles.sendButton}
              onPress={sendMessage}
            >
              <Ionicons
                name="arrow-up"
                size={22}
                color="#FFF"
              />
            </TouchableOpacity>
          </BlurView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  header: {
    height: 70,
    paddingHorizontal: 18,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "rgba(255,255,255,0.08)",
  },

  title: {
    color: "#FFF",
    fontSize: 28,
    fontWeight: "700",
  },

  subtitle: {
    color: "#888",
    marginTop: 4,
  },

  addButton: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: "#6C63FF",
    justifyContent: "center",
    alignItems: "center",
  },

  orbContainer: {
    alignItems: "center",
    marginVertical: 15,
  },

  status: {
    marginTop: 10,
    color: "#8FA7FF",
    fontWeight: "600",
    letterSpacing: 2,
  },

  chatList: {
    padding: 16,
    paddingBottom: 120,
  },

  loading: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 18,
    paddingBottom: 8,
  },

  loadingText: {
    color: "#AAA",
    marginLeft: 10,
  },

  bottom: {
    flexDirection: "row",
    alignItems: "flex-end",
    margin: 12,
    padding: 12,
    borderRadius: 28,
    overflow: "hidden",
  },

  input: {
    flex: 1,
    color: "#FFF",
    marginHorizontal: 12,
    maxHeight: 120,
    paddingVertical: 10,
    fontSize: 16,
  },

  sendButton: {
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: "#6C63FF",
    justifyContent: "center",
    alignItems: "center",
    marginLeft: 8,
  },
});