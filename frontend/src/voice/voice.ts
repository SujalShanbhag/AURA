import * as Speech from "expo-speech";

export async function speak(text: string) {
  Speech.stop();

  Speech.speak(text, {
    language: "en-US",
    pitch: 1,
    rate: 0.95,
  });
}

export function stopSpeaking() {
  Speech.stop();
}