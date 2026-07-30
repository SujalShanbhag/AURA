import { create } from "zustand";
import * as SecureStore from "expo-secure-store";

interface AuthState {
  token: string | null;
  refreshToken: string | null;

  load: () => Promise<void>;

  login: (
    access: string,
    refresh: string
  ) => Promise<void>;

  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  refreshToken: null,

  async load() {
    const token = await SecureStore.getItemAsync("token");
    const refresh = await SecureStore.getItemAsync("refresh");

    set({
      token,
      refreshToken: refresh,
    });
  },

  async login(access, refresh) {
    await SecureStore.setItemAsync("token", access);
    await SecureStore.setItemAsync("refresh", refresh);

    set({
      token: access,
      refreshToken: refresh,
    });
  },

  async logout() {
    await SecureStore.deleteItemAsync("token");
    await SecureStore.deleteItemAsync("refresh");

    set({
      token: null,
      refreshToken: null,
    });
  },
}));