from typing import Dict, Any
from app.services.assistant_functions import AssistantFnc
from app.services.rag_service import rag_service
from app.logging_config import configure_logging
import datetime

logger = configure_logging()

class AgentFactory:
    @staticmethod
    def create_agent(ctx: JobContext, agent_config: Dict[str, Any], retriever):
        """Create configured VoicePipelineAgent"""
        
        return VoicePipelineAgent(
            vad=ctx.proc.userdata["vad"],
            stt=openai.STT(detect_language=True),
            # before_llm_cb=lambda _assistant, chat_ctx: (
            #     rag_service.process_query(chat_ctx, retriever)
            # ),
            llm=openai.LLM(model="gpt-4o", temperature=agent_config.get("temperature", 0.7)),
            tts=openai.TTS(voice='shimmer',speed=1.0),        
            chat_ctx=llm.ChatContext().append(role="system", text=system_prompt),
            fnc_ctx=fnc_ctx,
        )

    @staticmethod
    def _build_system_prompt(agent_config: Dict[str, Any]) -> str:
        current_time = datetime.datetime.now(datetime.timezone.utc)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        base_instructions = (
            f"You are a multilingual technical assistant. Your interface with users will be voice.\n"
            f"Current date and time: {formatted_time}\n"
            "You will provide weather information for a given location.\n"
            "You can check calendar availability for scheduling meetings.\n"
            "You will test a function out"
            "do not return any text while calling the function.\n"
            "when performing function calls, let user know that you are checking.\n"
            "Requirements:\n"
            "1. Match the user's language automatically\n"
            "2. Prioritize information from verified sources\n"
            "3. If using general knowledge, explicitly state this\n"
            "4. Responses under 2 sentences unless complex topics\n"
            "5. Never invent information - use 'I don't know' when needed\n"
            "6. Ask for the user's timezone and convert the available slots to the user's timezone before mentioning.\n"
            "7. If the user wants to book a slot, confirm the details and proceed with booking.\n"
            "8. If required information is missing, ask the user to provide it.\n"
            "9. For booking slots, only use dates starting from the current date and time shown above. Never use past dates.\n"
            "10. Always ask the user for their preferred date and time for booking.\n"
            f"11. The earliest possible booking time is after {formatted_time}.\n"
            "12. Verify that the requested booking date is in the future before making the booking."
        )
        return f"{base_instructions}\n\nAgent Instructions:\n{agent_config.get('instruction', '')}"