from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Task
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# ============ MCP Tool Schemas ============
class AddTaskInput(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None

class ListTasksInput(BaseModel):
    user_id: str
    status: Optional[str] = "all"  # "all", "pending", "completed"

class CompleteTaskInput(BaseModel):
    user_id: str
    task_id: int

class DeleteTaskInput(BaseModel):
    user_id: str
    task_id: int

class UpdateTaskInput(BaseModel):
    user_id: str
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None

# ============ MCP Tools ============

@router.post("/add_task")
async def add_task(input: AddTaskInput, db: Session = Depends(get_session)):
    """
    MCP Tool: Add a new task
    """
    try:
        # Create new task
        task = Task(
            user_id=int(input.user_id),
            title=input.title,
            description=input.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_tasks")
async def list_tasks(input: ListTasksInput, db: Session = Depends(get_session)):
    """
    MCP Tool: List tasks with optional filter
    """
    try:
        query = select(Task).where(Task.user_id == int(input.user_id))
        
        if input.status == "pending":
            query = query.where(Task.completed == False)
        elif input.status == "completed":
            query = query.where(Task.completed == True)
        
        tasks = db.exec(query).all()
        
        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete_task")
async def complete_task(input: CompleteTaskInput, db: Session = Depends(get_session)):
    """
    MCP Tool: Mark a task as complete
    """
    try:
        task = db.get(Task, input.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != int(input.user_id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        task.completed = True
        task.updated_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_task")
async def delete_task(input: DeleteTaskInput, db: Session = Depends(get_session)):
    """
    MCP Tool: Delete a task
    """
    try:
        task = db.get(Task, input.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != int(input.user_id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        db.delete(task)
        db.commit()
        
        return {
            "task_id": task.id,
            "status": "deleted",
            "title": task.title
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_task")
async def update_task(input: UpdateTaskInput, db: Session = Depends(get_session)):
    """
    MCP Tool: Update a task's title or description
    """
    try:
        task = db.get(Task, input.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != int(input.user_id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if input.title is not None:
            task.title = input.title
        if input.description is not None:
            task.description = input.description
        
        task.updated_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
