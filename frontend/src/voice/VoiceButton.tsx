import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";

import {
  TouchableOpacity,
  StyleSheet,
} from "react-native";

interface Props {
  onPress: () => void;
}

export default function VoiceButton({
  onPress,
}: Props) {
  return (
    <TouchableOpacity
      style={styles.button}
      onPress={async () => {
        await Haptics.impactAsync(
          Haptics.ImpactFeedbackStyle.Medium
        );

        onPress();
      }}
    >
      <Ionicons
        name="mic"
        size={30}
        color="white"
      />
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    position: "absolute",

    right: 20,

    bottom: 90,

    width: 65,

    height: 65,

    borderRadius: 35,

    justifyContent: "center",

    alignItems: "center",

    backgroundColor: "#6C63FF",

    elevation: 8,
  },
});