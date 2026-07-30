import { View, Text, StyleSheet } from "react-native";
import AuraOrb from "../avatar/AuraOrb";

export default function ChatHeader() {
  return (
    <View style={styles.container}>
      <View style={styles.avatar}>
        <AuraOrb />
      </View>

      <View>
        <Text style={styles.title}>AURA</Text>
        <Text style={styles.subtitle}>Online • AI Ready</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 55,
    paddingBottom: 15,
    backgroundColor: "#050816",
  },

  avatar: {
    width: 70,
    height: 70,
    overflow: "hidden",
    marginRight: 15,
  },

  title: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 22,
  },

  subtitle: {
    color: "#82B1FF",
    marginTop: 4,
  },
});