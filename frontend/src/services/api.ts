import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

// For Android Emulator use:
// const API_URL = "http://10.0.2.2:8000";

// For Expo Go on your phone use your PC IP:
// const API_URL = "http://192.168.x.x:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;