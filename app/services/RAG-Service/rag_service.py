from typing import Any, Dict
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from .rag_utils import (
    query_classification_agent_qa,
    query_classification_agent_chapters,
    read_text_file,
    rewrite_query
)

logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval Augmented Generation (RAG) service that enhances LLM responses 
    by providing relevant context from stored documents.
    
    The service performs three parallel operations:
    1. Classifies which chapters are relevant to the query
    2. Finds similar existing Q&A pairs
    3. Rewrites the query for better matching
    
    It then combines this information into context for the LLM.
    """

    def run_parallel_tasks(self, question: str) -> Dict[str, Any]:
        """
        Executes classification and search tasks in parallel for efficiency.
        
        Args:
            question (str): The user's question
            
        Returns:
            Dict containing:
            - chapters_classification: List of relevant chapter IDs
            - most_similar_questions: List of similar Q&A IDs
            - rewrited_query: Optimized version of the question
        """
        results = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            tasks = {
                executor.submit(query_classification_agent_chapters, question): "chapters_classification",
                executor.submit(query_classification_agent_qa, question): "most_similar_questions",
                executor.submit(rewrite_query, question): "rewrited_query",
            }
            for future in tasks:
                task_name = tasks[future]
                try:
                    results[task_name] = future.result()
                except Exception as e:
                    logger.error(f"Error in {task_name}: {e}")
                    results[task_name] = []
        return results

    def build_context(self, question: str) -> str:
        """
        Builds context string from relevant documents based on the question.
        
        Args:
            question (str): The user's question
            
        Returns:
            str: Combined context from Q&A pairs and chapter content
        """
        context = "Here are the most relevant answers to the user's query:\n"
        
        results = self.run_parallel_tasks(question)
        
        # Add similar Q&A pairs
        if results["most_similar_questions"] not in ([0], ["0"]):

            qa_paths = [
                os.path.join("raw-data", "Q-A_text", f"QA{i}.txt") 
                for i in results["most_similar_questions"]
            ]
            for path in qa_paths:
                context += "\n" + read_text_file(path)

        # Add relevant chapter content
        if results["chapters_classification"] not in ([0], ["0"]):
            chapter_paths = [
                os.path.join("raw-data", "chapters_text", f"companies_rules{i}.txt") 
                for i in results["chapters_classification"]
            ]
            for path in chapter_paths:
                context += "\n" + read_text_file(path)

        return context

    def _get_last_message(self, chat_ctx: llm.ChatContext) -> str:
        """Extract and validate the last user message"""
        if not chat_ctx.messages:
            return ""
            
        last_msg = chat_ctx.messages[-1]
        if last_msg.role != "user":
            return ""
            
        return last_msg or ""

    def process_query(self, chat_ctx: llm.ChatContext) -> None:
        """
        Processes a user query and enhances the chat context with relevant information.
        
        Args:
            chat_ctx (llm.ChatContext): The chat context to enhance
        """
        last_user_msg_content = self._get_last_message(chat_ctx)
        
        if last_user_msg_content:
            context = self.build_context(last_user_msg_content)
            if context:
                rag_msg = llm.ChatMessage.create(
                    text="Context:\n" + context,
                    role="assistant",
                )
            # replace last message with RAG, and append user message at the end
            chat_ctx.messages[-1] = rag_msg
            chat_ctx.messages.append(user_msg)

# Create singleton instance
rag_service = RAGService()