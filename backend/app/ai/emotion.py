from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field


class Emotion(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    SAD = "sad"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    ANXIOUS = "anxious"
    CURIOUS = "curious"


class EmotionResult(BaseModel):
    emotion: Emotion
    confidence: float = Field(ge=0.0, le=1.0)
    detected_keywords: list[str] = Field(default_factory=list)


class EmotionEngine:
    """
    Rule-based emotion detector.

    Designed to be replaced by an ML or LLM implementation later
    without changing the rest of the application.
    """

    KEYWORDS: dict[Emotion, tuple[str, ...]] = {
        Emotion.HAPPY: (
            "happy",
            "great",
            "awesome",
            "good",
            "wonderful",
            "fantastic",
            "love",
        ),
        Emotion.EXCITED: (
            "excited",
            "can't wait",
            "amazing",
            "incredible",
            "finally",
            "yay",
        ),
        Emotion.SAD: (
            "sad",
            "cry",
            "depressed",
            "unhappy",
            "heartbroken",
            "lonely",
        ),
        Emotion.ANGRY: (
            "angry",
            "hate",
            "furious",
            "annoyed",
            "mad",
        ),
        Emotion.FRUSTRATED: (
            "frustrated",
            "stuck",
            "doesn't work",
            "broken",
            "issue",
            "problem",
            "error",
            "failed",
        ),
        Emotion.CONFUSED: (
            "confused",
            "don't understand",
            "how",
            "why",
            "what",
        ),
        Emotion.ANXIOUS: (
            "worried",
            "anxious",
            "nervous",
            "stress",
            "panic",
        ),
        Emotion.CURIOUS: (
            "learn",
            "explain",
            "teach",
            "curious",
            "tell me",
        ),
    }

    def detect(self, text: str) -> EmotionResult:
        """
        Detect the dominant emotion from user text.
        """

        normalized = text.lower()

        scores: dict[Emotion, int] = {
            emotion: 0
            for emotion in Emotion
        }

        detected: dict[Emotion, list[str]] = {
            emotion: []
            for emotion in Emotion
        }

        for emotion, keywords in self.KEYWORDS.items():
            for keyword in keywords:
                if re.search(
                    re.escape(keyword),
                    normalized,
                ):
                    scores[emotion] += 1
                    detected[emotion].append(keyword)

        best = Emotion.NEUTRAL
        highest = 0

        for emotion, score in scores.items():
            if score > highest:
                highest = score
                best = emotion

        if highest == 0:
            return EmotionResult(
                emotion=Emotion.NEUTRAL,
                confidence=1.0,
            )

        confidence = min(
            1.0,
            0.35 + (highest * 0.2),
        )

        return EmotionResult(
            emotion=best,
            confidence=confidence,
            detected_keywords=detected[best],
        )

    def response_guidance(
        self,
        result: EmotionResult,
    ) -> str:
        """
        Produce guidance that can be appended to
        the system prompt.
        """

        match result.emotion:

            case Emotion.HAPPY:
                return (
                    "Maintain the user's positive mood while remaining helpful."
                )

            case Emotion.EXCITED:
                return (
                    "Match the user's enthusiasm without exaggerating."
                )

            case Emotion.SAD:
                return (
                    "Respond with warmth and empathy. Avoid being overly cheerful."
                )

            case Emotion.ANGRY:
                return (
                    "Remain calm, respectful, and solution-focused."
                )

            case Emotion.FRUSTRATED:
                return (
                    "Prioritize actionable troubleshooting steps."
                )

            case Emotion.CONFUSED:
                return (
                    "Explain concepts clearly with simple examples."
                )

            case Emotion.ANXIOUS:
                return (
                    "Use a reassuring tone and provide structured next steps."
                )

            case Emotion.CURIOUS:
                return (
                    "Provide educational explanations with useful detail."
                )

            case _:
                return (
                    "Respond naturally while remaining accurate and helpful."
                )