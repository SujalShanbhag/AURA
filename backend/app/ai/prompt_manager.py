from __future__ import annotations

from dataclasses import dataclass, field

from app.ai.models import AIContext
from app.ai.models import ChatMessage
from app.ai.models import MessageRole


@dataclass(slots=True)
class PromptBundle:
    """
    Provider-independent prompt package.

    Providers can transform this bundle into the
    format required by their SDK.
    """

    system_prompt: str

    messages: list[ChatMessage] = field(default_factory=list)


class PromptManager:
    """
    Constructs provider-independent prompts from AIContext.
    """

    def build(
        self,
        context: AIContext,
        user_message: str,
    ) -> PromptBundle:

        system_sections: list[str] = [
            context.system_prompt,
            "",
            "## User Profile",
            f"Name: {context.profile.full_name}",
            f"Language: {context.profile.language}",
            f"Timezone: {context.profile.timezone}",
        ]

        if context.memories:
            system_sections.append("")
            system_sections.append("## Relevant Memories")

            for memory in context.memories:
                system_sections.append(f"- {memory.content}")

        messages = list(context.conversation)

        messages.append(
            ChatMessage(
                role=MessageRole.USER,
                content=user_message,
            )
        )

        return PromptBundle(
            system_prompt="\n".join(system_sections),
            messages=messages,
        )