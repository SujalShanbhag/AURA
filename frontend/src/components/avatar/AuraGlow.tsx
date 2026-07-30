import { View, StyleSheet } from "react-native";

export default function AuraGlow() {
  return <View style={styles.glow} />;
}

const styles = StyleSheet.create({
  glow: {
    position: "absolute",
    width: 260,
    height: 260,
    borderRadius: 130,
    backgroundColor: "#4F8CFF",
    opacity: 0.18,
  },
});