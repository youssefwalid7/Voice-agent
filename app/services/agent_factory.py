from app.services.rag_service import rag_service
from app.logging_config import configure_logging
from app.services.mci_prompt import mci_prompt


logger = configure_logging()

class AgentFactory:
    """
    Factory class for creating and configuring voice-enabled AI agents.
    Integrates speech-to-text, RAG-enhanced LLM, and text-to-speech capabilities.
    """
    
    @staticmethod
    def create_agent(ctx: JobContext):
        """
        Creates a configured VoicePipelineAgent with all necessary components.
        
        Args:
            ctx (JobContext): Context containing room and connection info
            
        Returns:
            VoicePipelineAgent: Configured voice-enabled agent
        """
        return VoicePipelineAgent(
            # Voice Activity Detection
            vad=ctx.proc.userdata["vad"],
            
            # Speech-to-Text with language detection
            stt=openai.STT(detect_language=True),
            
            # # RAG enhancement before LLM processing
            # before_llm_cb=lambda _assistant, chat_ctx: (
            #     rag_service.process_query(chat_ctx)
            # ),
            
            # Language Model
            llm=google.LLM(model="gemini-2.0-flash-exp", temperature="0.8"),
            
            # Text-to-Speech
            tts=openai.TTS(voice='shimmer',speed=1.0),
            
            # Initial chat context with system prompt
            chat_ctx=llm.ChatContext().append(role="system", text=mci_prompt),
        )
