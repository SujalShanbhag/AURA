import { View, Text, StyleSheet } from "react-native";

export default function GreetingCard() {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>
        Good Evening 👋
      </Text>

      <Text style={styles.subtitle}>
        I'm AURA.

        Ready whenever you are.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#18233E",
    padding: 20,
    borderRadius: 20,
    marginBottom: 20,
  },

  title: {
    color: "white",
    fontSize: 24,
    fontWeight: "700",
  },

  subtitle: {
    color: "#B8C4DD",
    marginTop: 8,
    fontSize: 16,
  },
});