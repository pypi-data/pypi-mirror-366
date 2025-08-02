from typing import Dict, Any, AsyncGenerator, List
from datetime import datetime
from letta_client import MessageCreate
from .letta_client import get_letta_client
from letta_client import LettaMessageUnion
import json

class ChatService:
    @staticmethod
    def _serialize_datetime(obj: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to convert datetime objects to ISO format strings"""
        for key, value in obj.items():
            if isinstance(value, datetime):
                obj[key] = value.isoformat()
            elif isinstance(value, dict):
                obj[key] = ChatService._serialize_datetime(value)
        return obj

    @staticmethod
    async def send_message_stream(agent_id: str, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Sends a message to an agent and streams back the response chunks
        """
        letta = get_letta_client()
        
        messages = [
            MessageCreate(
                role="user",
                content=message
            )
        ]
        
        # Use the streaming endpoint from Letta
        async for chunk in letta.agents.messages.create_stream(
            agent_id=agent_id,
            messages=messages,
            # stream_tokens=True  # Enable token streaming
        ):
            # Convert to dict and handle datetime serialization
            chunk_dict = chunk.model_dump()
            
            # Skip usage statistics messages
            if chunk_dict.get("message_type") == "usage_statistics" or chunk_dict.get("message_type") == "heartbeat":
                # TODO: Add to analytics
                continue
                
            yield ChatService._serialize_datetime(chunk_dict)

    @staticmethod
    async def get_agent_messages(agent_id: str, limit: int = 50, before_id: str | None = None) -> List[LettaMessageUnion]:
        """
        Retrieves message history for an agent
        
        Args:
            agent_id: The ID of the agent
            limit: Maximum number of messages to return
            before_id: Optional message ID to get messages before
        """
        letta = get_letta_client()
        
        response = await letta.agents.messages.list(
            agent_id=agent_id,
            limit=limit,
            before=before_id
        )
        
        # Filter out system messages and heartbeat messages
        filtered_messages = []
        for message in response:
            # Skip system messages
            if message.message_type == "system_message":
                continue
                
            # Skip heartbeat and login messages
            if (message.message_type == "user_message" and 
                message.content and 
                isinstance(message.content, str)):
                try:
                    content_json = json.loads(message.content)
                    if content_json.get("type") == "heartbeat" or content_json.get("type") == "login":
                        continue
                except (json.JSONDecodeError, AttributeError):
                    pass  # Not JSON or doesn't have type field, keep the message
                    
            filtered_messages.append(message)
        
        return filtered_messages