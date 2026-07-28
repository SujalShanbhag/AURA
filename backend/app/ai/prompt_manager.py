from __future__ import annotations

from dataclasses import dataclass

from app.ai.models import AIContext


@dataclass(slots=True)
class PromptBundle:
    """
    Fully rendered prompt package sent to an LLM.
    """

    system_prompt: str
    user_prompt: str


class PromptManager:
    """
    Responsible for constructing prompts from AIContext.

    This keeps prompt engineering separate from orchestration.
    """

    def build(
        self,
        context: AIContext,
        user_message: str,
    ) -> PromptBundle:

        sections: list[str] = []

        sections.append(context.system_prompt)

        sections.append("\n## User Profile")

        sections.append(
            f"Name: {context.profile.full_name}"
        )

        sections.append(
            f"Language: {context.profile.language}"
        )

        sections.append(
            f"Timezone: {context.profile.timezone}"
        )

        if context.memories:

            sections.append("\n## Relevant Memories")

            for memory in context.memories:
                sections.append(
                    f"- {memory.content}"
                )

        if context.conversation:

            sections.append("\n## Conversation")

            for message in context.conversation:
                sections.append(
                    f"{message.role.value}: {message.content}"
                )

        sections.append("\n## Instructions")

        sections.append(
            "Use the available context when it improves the answer."
        )

        sections.append(
            "Do not invent facts that are not supported."
        )

        return PromptBundle(
            system_prompt="\n".join(sections),
            user_prompt=user_message,
        )