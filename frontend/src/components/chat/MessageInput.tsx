import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Text,
} from "react-native";

interface Props {
  value: string;
  onChange: (text: string) => void;
  onSend: () => void;
}

export default function MessageInput({
  value,
  onChange,
  onSend,
}: Props) {
  return (
    <View style={styles.container}>
      <TextInput
        value={value}
        onChangeText={onChange}
        placeholder="Ask AURA anything..."
        placeholderTextColor="#666"
        style={styles.input}
      />

      <TouchableOpacity style={styles.button} onPress={onSend}>
        <Text style={styles.text}>➤</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    padding: 16,
    backgroundColor: "#0A1022",
  },

  input: {
    flex: 1,
    backgroundColor: "#18233E",
    color: "#fff",
    borderRadius: 25,
    paddingHorizontal: 20,
    fontSize: 16,
  },

  button: {
    marginLeft: 12,
    width: 55,
    height: 55,
    borderRadius: 28,
    backgroundColor: "#6C63FF",
    justifyContent: "center",
    alignItems: "center",
  },

  text: {
    color: "#fff",
    fontSize: 22,
  },
});