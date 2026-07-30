import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
} from "react-native-reanimated";

export default function VoicePulse() {
  const scale = useSharedValue(1);

  scale.value = withRepeat(
    withTiming(1.25, { duration: 1200 }),
    -1,
    true
  );

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: 2 - scale.value,
  }));

  return (
    <Animated.View
      style={[
        {
          position: "absolute",
          width: 180,
          height: 180,
          borderRadius: 90,
          borderWidth: 2,
          borderColor: "#6C63FF",
        },
        animatedStyle,
      ]}
    />
  );
}