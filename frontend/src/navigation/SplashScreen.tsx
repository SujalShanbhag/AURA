import { useEffect } from "react";
import { View, Text, StyleSheet } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { NativeStackScreenProps } from "@react-navigation/native-stack";

import { RootStackParamList } from "../navigation/AppNavigator";

type Props = NativeStackScreenProps<
  RootStackParamList,
  "Splash"
>;

export default function SplashScreen({
  navigation,
}: Props) {
  useEffect(() => {
    const timer = setTimeout(() => {
      navigation.replace("Login");
    }, 2500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <LinearGradient
      colors={["#070B14", "#111827", "#070B14"]}
      style={styles.container}
    >
      <Text style={styles.logo}>AURA</Text>

      <Text style={styles.tagline}>
        Your AI Companion
      </Text>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  logo: {
    color: "#fff",
    fontSize: 48,
    fontWeight: "700",
  },

  tagline: {
    color: "#B4BECF",
    marginTop: 12,
    fontSize: 18,
  },
});