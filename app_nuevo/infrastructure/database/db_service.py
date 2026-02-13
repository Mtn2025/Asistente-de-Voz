import logging
from typing import Optional, Any
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app_nuevo.infrastructure.database.models import AgentConfig, Call, Transcript

logger = logging.getLogger(__name__)

class DBService:
    """
    Service to handle database operations for legacy compatibility.
    Ideally, this logic should move to repositories, but kept here to verify migration.
    """
    
    async def get_agent_config(self, session: AsyncSession) -> Optional[AgentConfig]:
        """Get the first agent config (singleton pattern assumed)."""
        result = await session.execute(select(AgentConfig).limit(1))
        return result.scalars().first()

    async def update_agent_config(self, session: AsyncSession, **kwargs) -> Optional[AgentConfig]:
        """Update agent config."""
        config = await self.get_agent_config(session)
        if not config:
            # Create if not exists
            config = AgentConfig(**kwargs)
            session.add(config)
        else:
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        await session.commit()
        await session.refresh(config)
        return config

    async def create_call(self, session: AsyncSession, session_id: str, client_type: str) -> int:
        """Create a new call record."""
        call = Call(
            stream_id=session_id,
            client_type=client_type,
            status="active",
            started_at=datetime.utcnow()
        )
        session.add(call)
        await session.commit()
        await session.refresh(call)
        return call.id

    async def end_call(self, session: AsyncSession, call_id: int) -> None:
        """End a call."""
        call = await session.get(Call, call_id)
        if call:
            call.ended_at = datetime.utcnow()
            call.status = "completed"
            if call.started_at:
                call.duration_seconds = (call.ended_at - call.started_at).total_seconds()
            await session.commit()

    async def get_call(self, session: AsyncSession, call_id: int) -> Optional[Call]:
        """Get call by ID."""
        return await session.get(Call, call_id)

    async def update_call_extraction(self, session: AsyncSession, call_id: int, data: dict) -> None:
        """Update call with extracted data."""
        call = await session.get(Call, call_id)
        if call:
            call.extraction_data = data
            await session.commit()

    async def log_transcript(self, session: AsyncSession, session_id: str, role: str, content: str, call_db_id: Optional[int] = None) -> None:
        """Log a transcript."""
        if not call_db_id:
            # Try to find call by session_id if db_id not provided
            result = await session.execute(select(Call).where(Call.stream_id == session_id).order_by(Call.started_at.desc()).limit(1))
            call = result.scalars().first()
            if call:
                call_db_id = call.id
        
        if call_db_id:
            transcript = Transcript(
                call_id=call_db_id,
                role=role,
                content=content,
                timestamp=datetime.utcnow()
            )
            session.add(transcript)
            await session.commit()
        else:
            logger.warning(f"Could not log transcript for session {session_id}: Call not found")

# Global instance for legacy compatibility
db_service = DBService()
