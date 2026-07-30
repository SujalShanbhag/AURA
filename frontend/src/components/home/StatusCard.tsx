import { View, Text, StyleSheet } from "react-native";

export default function StatusCard() {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>
        AURA Status
      </Text>

      <Text style={styles.item}>
        🟢 Backend Connected
      </Text>

      <Text style={styles.item}>
        🟢 AI Online
      </Text>

      <Text style={styles.item}>
        🟢 Memory Active
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#18233E",
    borderRadius: 20,
    padding: 20,
    marginTop: 20,
  },

  title: {
    color: "white",
    fontWeight: "700",
    fontSize: 22,
    marginBottom: 15,
  },

  item: {
    color: "#B8C4DD",
    marginBottom: 8,
    fontSize: 16,
  },
});