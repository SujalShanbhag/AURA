import { View, StyleSheet, Animated, Easing } from "react-native";
import { useEffect, useRef } from "react";

export default function AuraOrb() {
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(scale, {
          toValue: 1.08,
          duration: 1800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(scale, {
          toValue: 1,
          duration: 1800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  return (
    <Animated.View
      style={[
        styles.orb,
        {
          transform: [{ scale }],
        },
      ]}
    />
  );
}

const styles = StyleSheet.create({
  orb: {
    width: 170,
    height: 170,
    borderRadius: 85,
    backgroundColor: "#6C63FF",
    alignSelf: "center",
    marginVertical: 30,
  },
});