from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    FORMAL = "formal"
    ENERGETIC = "energetic"


class ResponseLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class HumorLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"


class PersonalityProfile(BaseModel):
    """
    Defines how AURA should communicate.
    """

    name: str

    description: str

    tone: Tone = Tone.FRIENDLY

    response_length: ResponseLength = ResponseLength.MEDIUM

    humor: HumorLevel = HumorLevel.LIGHT

    empathetic: bool = True

    proactive: bool = True

    concise: bool = False

    emoji_enabled: bool = False

    ask_follow_up_questions: bool = True

    creativity: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )


DEFAULT_PERSONALITY = PersonalityProfile(
    name="Aura",
    description="Balanced AI companion.",
)


class PersonalityEngine:
    """
    Builds behavioral instructions that are injected into
    the system prompt before every LLM request.
    """

    def __init__(
        self,
        profile: PersonalityProfile = DEFAULT_PERSONALITY,
    ):
        self.profile = profile

    def build_system_prompt(self) -> str:

        instructions: list[str] = []

        instructions.append(
            f"You are {self.profile.name}, an AI companion."
        )

        instructions.append(
            f"Tone: {self.profile.tone.value}."
        )

        instructions.append(
            f"Preferred response length: "
            f"{self.profile.response_length.value}."
        )

        instructions.append(
            f"Humor: {self.profile.humor.value}."
        )

        if self.profile.empathetic:
            instructions.append(
                "Show empathy when appropriate."
            )

        if self.profile.proactive:
            instructions.append(
                "Offer useful next steps when appropriate."
            )

        if self.profile.concise:
            instructions.append(
                "Avoid unnecessary verbosity."
            )

        if self.profile.emoji_enabled:
            instructions.append(
                "Emojis may be used sparingly."
            )
        else:
            instructions.append(
                "Do not use emojis unless explicitly requested."
            )

        if self.profile.ask_follow_up_questions:
            instructions.append(
                "Ask a follow-up question only when it improves the user's outcome."
            )

        instructions.append(self.profile.description)

        return "\n".join(instructions)

    def update(
        self,
        profile: PersonalityProfile,
    ) -> None:
        """
        Replace the active personality profile.
        """
        self.profile = profile