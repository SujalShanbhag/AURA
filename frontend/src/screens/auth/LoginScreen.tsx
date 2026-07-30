import { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
} from "react-native";

import { LinearGradient } from "expo-linear-gradient";

import { login } from "../../api/auth";
import { useAuthStore } from "../../store/authStore";

export default function LoginScreen({ navigation }: any) {
  const auth = useAuthStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  async function onLogin() {
    if (!email || !password) {
      Alert.alert("Missing Information", "Enter email and password.");
      return;
    }

    try {
      setLoading(true);

      const response = await login(email, password);

      await auth.login(
        response.tokens.access_token,
        response.tokens.refresh_token
      );

      navigation.replace("Home");
    } catch (err: any) {
      Alert.alert(
        "Login Failed",
        err?.response?.data?.detail ?? "Unable to login."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <LinearGradient
      colors={["#050816", "#10172A", "#050816"]}
      style={styles.container}
    >
      <Text style={styles.title}>AURA</Text>

      <TextInput
        placeholder="Email"
        placeholderTextColor="#777"
        value={email}
        onChangeText={setEmail}
        style={styles.input}
        autoCapitalize="none"
      />

      <TextInput
        placeholder="Password"
        placeholderTextColor="#777"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={styles.input}
      />

      <TouchableOpacity
        style={styles.button}
        onPress={onLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Login</Text>
        )}
      </TouchableOpacity>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: 25,
  },

  title: {
    fontSize: 42,
    color: "#fff",
    fontWeight: "700",
    marginBottom: 40,
    textAlign: "center",
  },

  input: {
    backgroundColor: "#1A2238",
    color: "#fff",
    borderRadius: 15,
    padding: 18,
    marginBottom: 18,
    fontSize: 16,
  },

  button: {
    backgroundColor: "#6C63FF",
    padding: 18,
    borderRadius: 15,
    alignItems: "center",
    marginTop: 15,
  },

  buttonText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 18,
  },
});