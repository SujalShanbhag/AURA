import React from "react";

import {
  StyleProp,
  StyleSheet,
  ViewStyle,
} from "react-native";

import { BlurView } from "expo-blur";

interface Props {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  intensity?: number;
}

export default function GlassCard({
  children,
  style,
  intensity = 45,
}: Props) {
  return (
    <BlurView
      intensity={intensity}
      tint="dark"
      style={[styles.container, style]}
    >
      {children}
    </BlurView>
  );
}

const styles = StyleSheet.create({
  container: {
    overflow: "hidden",

    borderRadius: 26,

    padding: 20,

    borderWidth: 1,

    borderColor: "rgba(255,255,255,0.08)",

    backgroundColor: "rgba(255,255,255,0.06)",
  },
});