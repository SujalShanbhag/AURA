import { useEffect } from "react";
import { StyleSheet, View } from "react-native";

import Animated, {
  Easing,
  interpolate,
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
} from "react-native-reanimated";

interface Props {
  size?: number;
  state?: "idle" | "thinking" | "speaking" | "listening";
}

export default function AuraOrb({
  size = 180,
  state = "idle",
}: Props) {
  const pulse = useSharedValue(0);
  const rotate = useSharedValue(0);

  useEffect(() => {
    pulse.value = withRepeat(
      withTiming(1, {
        duration:
          state === "thinking"
            ? 700
            : state === "speaking"
            ? 500
            : 2500,
        easing: Easing.inOut(Easing.ease),
      }),
      -1,
      true
    );

    rotate.value = withRepeat(
      withTiming(360, {
        duration: 9000,
        easing: Easing.linear,
      }),
      -1,
      false
    );
  }, [state]);

  const ringStyle = useAnimatedStyle(() => ({
    transform: [
      {
        rotate: `${rotate.value}deg`,
      },
    ],
  }));

  const glowStyle = useAnimatedStyle(() => ({
    transform: [
      {
        scale: interpolate(
          pulse.value,
          [0, 1],
          [1, 1.15]
        ),
      },
    ],
    opacity: interpolate(
      pulse.value,
      [0, 1],
      [0.45, 0.9]
    ),
  }));

  const coreStyle = useAnimatedStyle(() => ({
    transform: [
      {
        scale: interpolate(
          pulse.value,
          [0, 1],
          [1, 1.06]
        ),
      },
    ],
  }));

  return (
    <View
      style={{
        width: size,
        height: size,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Animated.View
        style={[
          styles.glow,
          {
            width: size,
            height: size,
            borderRadius: size / 2,
          },
          glowStyle,
        ]}
      />

      <Animated.View
        style={[
          styles.outerRing,
          {
            width: size,
            height: size,
            borderRadius: size / 2,
          },
          ringStyle,
        ]}
      />

      <Animated.View
        style={[
          styles.middleRing,
          {
            width: size * 0.82,
            height: size * 0.82,
            borderRadius: size,
          },
          {
            transform: [
              {
                rotate: "-45deg",
              },
            ],
          },
        ]}
      />

      <Animated.View
        style={[
          styles.core,
          {
            width: size * 0.45,
            height: size * 0.45,
            borderRadius: size,
          },
          coreStyle,
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  glow: {
    position: "absolute",
    backgroundColor: "#6C63FF",
  },

  outerRing: {
    position: "absolute",
    borderWidth: 2,
    borderColor: "#6C63FF",
  },

  middleRing: {
    position: "absolute",
    borderWidth: 2,
    borderColor: "#38BDF8",
    opacity: 0.8,
  },

  core: {
    backgroundColor: "#FFFFFF",
    shadowColor: "#6C63FF",
    shadowOpacity: 1,
    shadowRadius: 40,
    shadowOffset: {
      width: 0,
      height: 0,
    },
    elevation: 30,
  },
});