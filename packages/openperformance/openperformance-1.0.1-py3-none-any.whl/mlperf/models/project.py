"""Project and organization database models."""

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from mlperf.utils.database import Base


class ProjectRole(str, enum.Enum):
    """Roles within a project."""
    
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectVisibility(str, enum.Enum):
    """Project visibility levels."""
    
    PRIVATE = "private"
    INTERNAL = "internal"  # Visible to organization members
    PUBLIC = "public"


class Organization(Base):
    """Organization model for team collaboration."""
    
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Settings
    settings = Column(JSON, nullable=True, default={})
    features = Column(JSON, nullable=True, default=[])  # Enabled features
    
    # Limits
    max_projects = Column(Integer, default=10)
    max_members = Column(Integer, default=50)
    max_storage_gb = Column(Integer, default=100)
    
    # Billing (for SaaS)
    billing_email = Column(String(255), nullable=True)
    subscription_tier = Column(String(50), default="free")
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    logo_url = Column(String(500), nullable=True)
    tags = Column(JSON, nullable=True, default=[])
    data_metadata = Column(JSON, nullable=True, default={})
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    hardware_profiles = relationship("HardwareProfile", backref="organization")
    
    # Indexes
    __table_args__ = (
        Index("idx_organization_active", "is_active"),
        Index("idx_organization_tier", "subscription_tier"),
    )
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "email": self.email,
            "website": self.website,
            "settings": self.settings or {},
            "features": self.features or [],
            "limits": {
                "max_projects": self.max_projects,
                "max_members": self.max_members,
                "max_storage_gb": self.max_storage_gb,
            },
            "subscription": {
                "tier": self.subscription_tier,
                "expires_at": self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
            },
            "logo_url": self.logo_url,
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Project(Base):
    """Project model for organizing work."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)  # URL-friendly name
    description = Column(Text, nullable=True)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Visibility and access
    visibility = Column(Enum(ProjectVisibility), default=ProjectVisibility.PRIVATE, nullable=False)
    is_template = Column(Boolean, default=False)
    template_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Configuration
    settings = Column(JSON, nullable=True, default={})
    default_benchmark_params = Column(JSON, nullable=True, default={})
    
    # Resource limits
    max_concurrent_runs = Column(Integer, default=5)
    max_storage_gb = Column(Integer, default=10)
    
    # Statistics
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    total_runtime_hours = Column(Float, default=0.0)
    
    # Metadata
    tags = Column(JSON, nullable=True, default=[])
    data_metadata = Column(JSON, nullable=True, default={})
    readme = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    benchmark_runs = relationship("BenchmarkRun", backref="project")
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")
    
    # Self-referential relationship for templates
    template = relationship("Project", remote_side=[id], backref="derived_projects")
    
    # Indexes
    __table_args__ = (
        Index("idx_project_user", "user_id"),
        Index("idx_project_org", "organization_id"),
        Index("idx_project_visibility", "visibility"),
        Index("idx_project_active", "is_active"),
        UniqueConstraint("slug", "organization_id", name="uq_project_slug_org"),
        UniqueConstraint("slug", "user_id", name="uq_project_slug_user"),
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, slug={self.slug})>"
    
    def update_statistics(self, run_status: str, runtime_seconds: float) -> None:
        """Update project statistics after a run."""
        self.total_runs += 1
        if run_status == "completed":
            self.successful_runs += 1
        elif run_status == "failed":
            self.failed_runs += 1
        
        if runtime_seconds:
            self.total_runtime_hours += runtime_seconds / 3600.0
        
        self.last_activity_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "organization_name": self.organization.name if self.organization else None,
            "visibility": self.visibility.value,
            "is_template": self.is_template,
            "template_id": self.template_id,
            "settings": self.settings or {},
            "limits": {
                "max_concurrent_runs": self.max_concurrent_runs,
                "max_storage_gb": self.max_storage_gb,
            },
            "statistics": {
                "total_runs": self.total_runs,
                "successful_runs": self.successful_runs,
                "failed_runs": self.failed_runs,
                "total_runtime_hours": self.total_runtime_hours,
                "success_rate": (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0,
            },
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
        }


class ProjectMember(Base):
    """Project membership and permissions."""
    
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Role and permissions
    role = Column(Enum(ProjectRole), default=ProjectRole.MEMBER, nullable=False)
    permissions = Column(JSON, nullable=True, default=[])  # Custom permissions
    
    # Invitation
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    invited_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    
    # Activity
    last_accessed_at = Column(DateTime, nullable=True)
    contribution_count = Column(Integer, default=0)  # Number of runs, experiments, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    
    # Indexes
    __table_args__ = (
        Index("idx_project_member_user", "user_id"),
        Index("idx_project_member_role", "role"),
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )
    
    def __repr__(self) -> str:
        return f"<ProjectMember(id={self.id}, project_id={self.project_id}, user_id={self.user_id}, role={self.role})>"
    
    def has_permission(self, permission: str) -> bool:
        """Check if member has a specific permission."""
        # Owners have all permissions
        if self.role == ProjectRole.OWNER:
            return True
        
        # Check role-based permissions
        role_permissions = {
            ProjectRole.ADMIN: ["read", "write", "delete", "invite", "settings"],
            ProjectRole.MEMBER: ["read", "write"],
            ProjectRole.VIEWER: ["read"],
        }
        
        if permission in role_permissions.get(self.role, []):
            return True
        
        # Check custom permissions
        return permission in (self.permissions or [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "role": self.role.value,
            "permissions": self.permissions or [],
            "invited_by": self.invited_by,
            "invited_at": self.invited_at.isoformat() if self.invited_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "contribution_count": self.contribution_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }