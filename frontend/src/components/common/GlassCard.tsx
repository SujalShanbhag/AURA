import { BlurView } from "expo-blur";
import { StyleSheet } from "react-native";

export default function GlassCard({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <BlurView
      intensity={35}
      tint="dark"
      style={styles.card}
    >
      {children}
    </BlurView>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 24,
    padding: 20,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,.08)",
  },
});