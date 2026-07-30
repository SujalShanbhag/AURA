import { View, Animated, StyleSheet } from "react-native";
import { useEffect, useRef } from "react";

export default function TypingIndicator() {
  const a = useRef(new Animated.Value(0.2)).current;
  const b = useRef(new Animated.Value(0.2)).current;
  const c = useRef(new Animated.Value(0.2)).current;

  function animate(dot: Animated.Value, delay: number) {
    Animated.loop(
      Animated.sequence([
        Animated.delay(delay),
        Animated.timing(dot, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(dot, {
          toValue: 0.2,
          duration: 300,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }

  useEffect(() => {
    animate(a, 0);
    animate(b, 200);
    animate(c, 400);
  }, []);

  return (
    <View style={styles.row}>
      <Animated.View style={[styles.dot, { opacity: a }]} />
      <Animated.View style={[styles.dot, { opacity: b }]} />
      <Animated.View style={[styles.dot, { opacity: c }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    marginVertical: 10,
    marginLeft: 10,
  },

  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginHorizontal: 4,
    backgroundColor: "#7D5FFF",
  },
});