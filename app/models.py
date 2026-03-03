from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# ============ User Model ============
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")

# ============ Task Model ============
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")

# ============ Conversation Model ============
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

# ============ Message Model ============
class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="messages")
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
