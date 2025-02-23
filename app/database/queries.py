from typing import Dict, Optional
from app.database import get_pool
import asyncpg
import logging
from datetime import datetime, timezone
import json
from app.logging_config import configure_logging

logger = configure_logging()

async def get_agent_by_id(agent_id: int) -> Optional[Dict]:
    """
    Retrieve an agent by ID from the database with model details.
    Returns: Agent dict or None if not found
    """
    query = """
        SELECT 
            a.id, a.model_id, a.name, a.instructions, a.welcome_message,
            a.temperature, a.category_meta_data, a.tone_of_voice,
            m.name AS model_name
        FROM agents a
        INNER JOIN models m ON a.model_id = m.id
        WHERE a.id = $1
    """
    
    try:
        async with get_pool().acquire() as conn:
            record = await conn.fetchrow(query, agent_id)
            return dict(record) if record else None
            
    except asyncpg.PostgresError as e:
        logger.error(f"Error fetching agent {agent_id}: {str(e)}")
        raise
    
async def save_transcription(agent_id: int, room_id: str, role: str, new_text: str, channel_id: int = 1):
    """
    Save transcription to PostgreSQL chat_histories table, appending new text as JSON.
    Args:
        agent_id: The ID of the agent
        room_id: The chat session ID
        role: The role of the message sender
        new_text: The message content
        channel_id: The channel ID (defaults to 0)
    """
    query = """
        INSERT INTO chat_histories (
            id, created_at, updated_at, chat_session_id, 
            chat_content, agent_id, channel_id
        )
        VALUES (
            nextval('chat_histories_id_seq'),
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            $1,
            $2::jsonb,
            $3,
            $4
        )
        ON CONFLICT (chat_session_id)
        DO UPDATE SET 
            chat_content = chat_histories.chat_content || EXCLUDED.chat_content,
            updated_at = CURRENT_TIMESTAMP;
    """
    json_text = json.dumps([{"timestamp": datetime.now(timezone.utc).isoformat(), role: new_text}])
    
    try:
        async with get_pool().acquire() as conn:
            await conn.execute(
                query, 
                room_id,
                json_text,
                agent_id,
                channel_id
            )
    except asyncpg.PostgresError as e:
        logger.error(f"Error inserting chat history: {str(e)}")
        raise