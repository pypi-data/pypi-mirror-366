"""Database utilities and session management."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import MetaData, create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from mlperf.utils.config import get_settings
from mlperf.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Create base class for models
Base = declarative_base()
metadata = MetaData()

# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_sync_engine: Optional[Engine] = None
_async_session_factory: Optional[async_sessionmaker] = None
_sync_session_factory: Optional[sessionmaker] = None


def get_engine() -> AsyncEngine:
    """Get or create async database engine."""
    global _engine
    
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
            pool_recycle=3600,  # Recycle connections after 1 hour
            connect_args={
                "server_settings": {"application_name": settings.APP_NAME},
                "command_timeout": 60,
            } if "postgresql" in settings.DATABASE_URL else {},
        )
        
        logger.info(f"Created async database engine for {settings.DATABASE_URL}")
    
    return _engine


def get_sync_engine() -> Engine:
    """Get or create sync database engine."""
    global _sync_engine
    
    if _sync_engine is None:
        # Convert async URL to sync URL
        sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
        
        _sync_engine = create_engine(
            sync_url,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
            pool_recycle=3600,
            connect_args={
                "application_name": settings.APP_NAME,
            } if "postgresql" in sync_url else {},
        )
        
        # Add event listeners
        @event.listens_for(_sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance."""
            if "sqlite" in sync_url:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
        
        logger.info(f"Created sync database engine for {sync_url}")
    
    return _sync_engine


def get_session_factory() -> async_sessionmaker:
    """Get async session factory."""
    global _async_session_factory
    
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    return _async_session_factory


def get_sync_session_factory() -> sessionmaker:
    """Get sync session factory."""
    global _sync_session_factory
    
    if _sync_session_factory is None:
        _sync_session_factory = sessionmaker(
            bind=get_sync_engine(),
            class_=Session,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    return _sync_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async with get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as context manager."""
    async with get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """Get sync database session."""
    session = get_sync_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def create_tables(engine: Optional[AsyncEngine] = None) -> None:
    """Create all database tables."""
    if engine is None:
        engine = get_engine()
    
    try:
        # Import all models to ensure they're registered
        from mlperf.auth.models import (
            ApiKey,
            AuditLog,
            Base as AuthBase,
            RefreshToken,
            User,
        )
        
        # Merge metadata
        for table in AuthBase.metadata.tables.values():
            table.to_metadata(Base.metadata)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def drop_tables(engine: Optional[AsyncEngine] = None) -> None:
    """Drop all database tables."""
    if engine is None:
        engine = get_engine()
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


async def init_database() -> None:
    """Initialize database with default data."""
    from mlperf.auth.models import User, UserRole
    from mlperf.auth.security import get_password_hash
    
    async with get_db_context() as db:
        try:
            # Check if admin user exists
            from sqlalchemy import select
            
            result = await db.execute(
                select(User).where(User.username == "admin")
            )
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                # Create default admin user
                admin_user = User(
                    username="admin",
                    email="admin@openperformance.ai",
                    full_name="Administrator",
                    hashed_password=get_password_hash("changeme123!"),
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True,
                )
                
                db.add(admin_user)
                await db.commit()
                
                logger.info("Created default admin user (username: admin, password: changeme123!)")
                logger.warning("IMPORTANT: Change the default admin password immediately!")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise


async def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def get_database_info() -> dict:
    """Get database information."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            # Get database version
            if "postgresql" in settings.DATABASE_URL:
                result = await conn.execute("SELECT version()")
                version = result.scalar()
            elif "mysql" in settings.DATABASE_URL:
                result = await conn.execute("SELECT VERSION()")
                version = result.scalar()
            elif "sqlite" in settings.DATABASE_URL:
                result = await conn.execute("SELECT sqlite_version()")
                version = f"SQLite {result.scalar()}"
            else:
                version = "Unknown"
            
            # Get table count
            if "sqlite" in settings.DATABASE_URL:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                )
            else:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
                )
            
            table_count = result.scalar()
            
            return {
                "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
                "version": version,
                "table_count": table_count,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            }
            
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}


def run_migrations() -> None:
    """Run database migrations using Alembic."""
    try:
        from alembic import command
        from alembic.config import Config
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database migrations completed successfully")
        
    except ImportError:
        logger.warning("Alembic not installed, skipping migrations")
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        raise


# Cleanup function for graceful shutdown
async def close_database() -> None:
    """Close database connections."""
    global _engine, _sync_engine
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("Closed async database engine")
    
    if _sync_engine is not None:
        _sync_engine.dispose()
        _sync_engine = None
        logger.info("Closed sync database engine")