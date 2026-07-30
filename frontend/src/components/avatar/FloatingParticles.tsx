import { View, StyleSheet } from "react-native";

export default function FloatingParticles() {
  return (
    <>
      <View style={[styles.dot, { top: 20, left: 40 }]} />
      <View style={[styles.dot, { top: 60, right: 30 }]} />
      <View style={[styles.dot, { bottom: 40, left: 70 }]} />
      <View style={[styles.dot, { bottom: 20, right: 50 }]} />
    </>
  );
}

const styles = StyleSheet.create({
  dot: {
    position: "absolute",
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#82B1FF",
  },
});