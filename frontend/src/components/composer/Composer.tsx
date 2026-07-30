import React from "react";
import {
  StyleSheet,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import { BlurView } from "expo-blur";

import {
  Ionicons,
  MaterialCommunityIcons,
} from "@expo/vector-icons";

interface Props {
  value: string;
  onChangeText(text: string): void;
  onSend(): void;
  onVoice(): void;
  onAttachment(): void;
  onCamera(): void;
  onGallery(): void;
}

export default function Composer({
  value,
  onChangeText,
  onSend,
  onVoice,
  onAttachment,
  onCamera,
  onGallery,
}: Props) {
  return (
    <BlurView
      intensity={35}
      tint="dark"
      style={styles.container}
    >
      <TouchableOpacity
        onPress={onAttachment}
      >
        <Ionicons
          name="attach"
          size={22}
          color="#BBBBBB"
        />
      </TouchableOpacity>

      <TouchableOpacity
        onPress={onCamera}
        style={styles.icon}
      >
        <Ionicons
          name="camera"
          size={22}
          color="#BBBBBB"
        />
      </TouchableOpacity>

      <TouchableOpacity
        onPress={onGallery}
        style={styles.icon}
      >
        <Ionicons
          name="image"
          size={22}
          color="#BBBBBB"
        />
      </TouchableOpacity>

      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder="Ask AURA anything..."
        placeholderTextColor="#777"
        multiline
        style={styles.input}
      />

      <TouchableOpacity
        style={styles.icon}
      >
        <MaterialCommunityIcons
          name="emoticon-outline"
          size={22}
          color="#BBBBBB"
        />
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.voice}
        onPress={onVoice}
      >
        <Ionicons
          name="mic"
          size={20}
          color="white"
        />
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.send}
        onPress={onSend}
      >
        <Ionicons
          name="arrow-up"
          size={22}
          color="#FFF"
        />
      </TouchableOpacity>
    </BlurView>
  );
}

const styles = StyleSheet.create({
  container: {
    margin: 12,
    borderRadius: 30,
    paddingHorizontal: 15,
    paddingVertical: 12,
    flexDirection: "row",
    alignItems: "flex-end",
    overflow: "hidden",
  },

  input: {
    flex: 1,
    color: "white",
    fontSize: 16,
    maxHeight: 120,
    marginHorizontal: 12,
    paddingVertical: 8,
  },

  icon: {
    marginLeft: 10,
  },

  voice: {
    width: 42,
    height: 42,
    borderRadius: 21,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#3B82F6",
    marginLeft: 8,
  },

  send: {
    width: 46,
    height: 46,
    borderRadius: 23,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#6C63FF",
    marginLeft: 8,
  },
});