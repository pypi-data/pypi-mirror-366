import os
from letta_client import AsyncLetta, LettaEnvironment
from contextvars import ContextVar
from typing import Optional

LETTA_URL = os.getenv("LETTA_URL")

letta_client: ContextVar[Optional[object]] = ContextVar('letta_client', default=None)

def get_letta_client():
    """
    Get regular client that respects RLS policies
    """
    client = letta_client.get()
    if client is not None:
        return client
    
    client = AsyncLetta(
        base_url=LETTA_URL,
    )
    letta_client.set(client)
    
    return client
