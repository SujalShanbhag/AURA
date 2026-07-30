import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
} from "react-native-reanimated";

export default function ThinkingAnimation() {
  const rotate = useSharedValue(0);

  rotate.value = withRepeat(
    withTiming(360, { duration: 5000 }),
    -1,
    false
  );

  const style = useAnimatedStyle(() => ({
    transform: [
      {
        rotate: `${rotate.value}deg`,
      },
    ],
  }));

  return (
    <Animated.View
      style={[
        {
          position: "absolute",
          width: 200,
          height: 200,
          borderRadius: 100,
          borderWidth: 1,
          borderColor: "#4F8CFF",
        },
        style,
      ]}
    />
  );
}