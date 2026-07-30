import { LinearGradient } from "expo-linear-gradient";
import { ScrollView } from "react-native";
import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import { useNavigation } from "@react-navigation/native";

import AuraOrb from "../../components/avatar/AuraOrb";
import AnimatedBackground from "../../components/background/AnimatedBackground";
import QuickActionCard from "../../components/cards/QuickActionCard";

export default function HomeScreen() {
  const navigation = useNavigation<any>();

  const hour = new Date().getHours();

  const greeting =
    hour < 12
      ? "Good Morning"
      : hour < 18
      ? "Good Afternoon"
      : "Good Evening";

  return (
    <LinearGradient
      colors={[
        "#040816",
        "#0D1325",
        "#050816",
      ]}
      style={styles.container}
    >
      <AnimatedBackground />

      <ScrollView
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <Text style={styles.greeting}>
            {greeting}
          </Text>

          <Text style={styles.title}>
            Welcome to AURA
          </Text>

          <Text style={styles.subtitle}>
            Your intelligent AI companion
          </Text>
        </View>

        <View style={styles.orb}>
          <AuraOrb
            size={180}
            state="idle"
          />
        </View>

        <View style={styles.actions}>
          <QuickActionCard
            title="Chat"
            subtitle="Talk naturally with AURA"
            icon="chatbubble-ellipses"
            onPress={() =>
              navigation.navigate("Chat")
            }
          />

          <QuickActionCard
            title="Voice"
            subtitle="Hands-free conversations"
            icon="mic"
          />

          <QuickActionCard
            title="Vision"
            subtitle="Analyze images"
            icon="camera"
          />

          <QuickActionCard
            title="Memory"
            subtitle="Remember important things"
            icon="library"
          />

          <QuickActionCard
            title="Research"
            subtitle="AI-powered research"
            icon="search"
          />

          <QuickActionCard
            title="Settings"
            subtitle="Customize AURA"
            icon="settings"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Recent Conversations
          </Text>

          <TouchableOpacity style={styles.chatCard}>
            <Text style={styles.chatTitle}>
              🚀 Building AURA
            </Text>

            <Text style={styles.chatPreview}>
              Continue building your AI Companion...
            </Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.chatCard}>
            <Text style={styles.chatTitle}>
              📄 Research Assistant
            </Text>

            <Text style={styles.chatPreview}>
              Resume your research session...
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  header: {
    marginTop: 60,
    alignItems: "center",
  },

  greeting: {
    color: "#7D89A7",
    fontSize: 18,
  },

  title: {
    color: "#FFFFFF",
    fontSize: 34,
    fontWeight: "700",
    marginTop: 8,
  },

  subtitle: {
    color: "#98A4C2",
    marginTop: 10,
    fontSize: 16,
  },

  orb: {
    marginTop: 40,
    alignItems: "center",
    marginBottom: 45,
  },

  actions: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    paddingHorizontal: 20,
  },

  section: {
    marginTop: 35,
    paddingHorizontal: 20,
    paddingBottom: 50,
  },

  sectionTitle: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 22,
    marginBottom: 16,
  },

  chatCard: {
    backgroundColor: "rgba(17,27,52,0.8)",
    borderRadius: 18,
    padding: 18,
    marginBottom: 14,
  },

  chatTitle: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 17,
  },

  chatPreview: {
    color: "#9EA9C7",
    marginTop: 8,
    lineHeight: 22,
  },
});