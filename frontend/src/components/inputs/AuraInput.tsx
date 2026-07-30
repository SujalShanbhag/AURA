import React, { useState } from "react";
import {
  Pressable,
  StyleSheet,
  TextInput,
  View,
} from "react-native";

import { Ionicons } from "@expo/vector-icons";

import { Colors, Spacing } from "../../theme";

interface AuraInputProps {
  placeholder: string;
  value: string;
  onChangeText: (text: string) => void;
  secureTextEntry?: boolean;
}

export default function AuraInput({
  placeholder,
  value,
  onChangeText,
  secureTextEntry = false,
}: AuraInputProps) {
  const [hidden, setHidden] = useState(
    secureTextEntry
  );

  return (
    <View style={styles.container}>
      <TextInput
        placeholder={placeholder}
        placeholderTextColor={Colors.placeholder}
        value={value}
        onChangeText={onChangeText}
        secureTextEntry={hidden}
        style={styles.input}
      />

      {secureTextEntry && (
        <Pressable
          onPress={() => setHidden(!hidden)}
        >
          <Ionicons
            name={
              hidden
                ? "eye-off-outline"
                : "eye-outline"
            }
            size={22}
            color={Colors.textSecondary}
          />
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.inputBackground,
    borderRadius: Spacing.radius,
    paddingHorizontal: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },

  input: {
    flex: 1,
    color: Colors.text,
    paddingVertical: 16,
    fontSize: 16,
  },
});