import * as SecureStore from "expo-secure-store";

const ACCESS_TOKEN = "access_token";
const REFRESH_TOKEN = "refresh_token";

export async function saveTokens(
  access: string,
  refresh: string
) {
  await SecureStore.setItemAsync(
    ACCESS_TOKEN,
    access
  );

  await SecureStore.setItemAsync(
    REFRESH_TOKEN,
    refresh
  );
}

export async function getAccessToken() {
  return SecureStore.getItemAsync(
    ACCESS_TOKEN
  );
}

export async function getRefreshToken() {
  return SecureStore.getItemAsync(
    REFRESH_TOKEN
  );
}

export async function logout() {
  await SecureStore.deleteItemAsync(
    ACCESS_TOKEN
  );

  await SecureStore.deleteItemAsync(
    REFRESH_TOKEN
  );
}