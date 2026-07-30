import { BlurView } from "expo-blur";
import { Ionicons } from "@expo/vector-icons";

import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

interface Props {
  title: string;
  subtitle: string;
  icon: keyof typeof Ionicons.glyphMap;
  onPress?: () => void;
}

export default function QuickActionCard({
  title,
  subtitle,
  icon,
  onPress,
}: Props) {
  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={onPress}
      style={styles.wrapper}
    >
      <BlurView
        intensity={35}
        tint="dark"
        style={styles.card}
      >
        <View style={styles.icon}>
          <Ionicons
            name={icon}
            color="#FFFFFF"
            size={26}
          />
        </View>

        <Text style={styles.title}>
          {title}
        </Text>

        <Text style={styles.subtitle}>
          {subtitle}
        </Text>
      </BlurView>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    width: "48%",
    marginBottom: 16,
  },

  card: {
    borderRadius: 22,
    padding: 18,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    minHeight: 150,
    justifyContent: "space-between",
  },

  icon: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: "rgba(108,99,255,0.25)",
    justifyContent: "center",
    alignItems: "center",
  },

  title: {
    color: "#FFFFFF",
    fontSize: 18,
    fontWeight: "700",
    marginTop: 16,
  },

  subtitle: {
    color: "#9EA9C7",
    marginTop: 6,
    lineHeight: 20,
    fontSize: 13,
  },
});