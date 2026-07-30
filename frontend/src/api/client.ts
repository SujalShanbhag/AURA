import axios from "axios";
import * as SecureStore from "expo-secure-store";

// Android Emulator
const BASE_URL = "http://10.0.2.2:8000/api/v1";

// Physical device
// const BASE_URL = "http://YOUR_PC_IP:8000/api/v1";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
});

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;