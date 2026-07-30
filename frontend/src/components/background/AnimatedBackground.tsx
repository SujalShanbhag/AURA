import { useEffect } from "react";
import {
  Dimensions,
  StyleSheet,
} from "react-native";

import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
  Easing,
} from "react-native-reanimated";

const { width, height } = Dimensions.get("window");

const PARTICLES = 16;

export default function AnimatedBackground() {
  const animations = Array.from(
    { length: PARTICLES },
    () => useSharedValue(Math.random())
  );

  useEffect(() => {
    animations.forEach((value) => {
      value.value = withRepeat(
        withTiming(1, {
          duration: 6000 + Math.random() * 4000,
          easing: Easing.linear,
        }),
        -1,
        true
      );
    });
  }, []);

  return (
    <>
      {animations.map((value, index) => {
        const size = 8 + Math.random() * 24;

        const left = Math.random() * width;
        const top = Math.random() * height;

        const style = useAnimatedStyle(() => ({
          transform: [
            {
              translateY:
                value.value * -80,
            },
            {
              scale:
                0.8 + value.value * 0.5,
            },
          ],

          opacity:
            0.15 +
            value.value * 0.25,
        }));

        return (
          <Animated.View
            key={index}
            style={[
              styles.particle,
              {
                width: size,
                height: size,
                borderRadius: size / 2,
                left,
                top,
              },
              style,
            ]}
          />
        );
      })}
    </>
  );
}

const styles = StyleSheet.create({
  particle: {
    position: "absolute",
    backgroundColor: "#6C63FF",
  },
});