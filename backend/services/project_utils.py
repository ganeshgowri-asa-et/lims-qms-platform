"""
Project Management Utility Services
- Gantt chart data generation
- Kanban board management
- Resource utilization tracking
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.workflow import Project, Task, Milestone, TaskStatusEnum
from datetime import datetime, timedelta


class GanttChartService:
    """Service for generating Gantt chart data"""

    def __init__(self, db: Session):
        self.db = db

    def generate_project_gantt(self, project_id: int) -> Dict[str, Any]:
        """
        Generate Gantt chart data for a project

        Returns data in format compatible with libraries like dhtmlxGantt,
        Frappe Gantt, or custom visualization
        """
        project = self.db.query(Project).get(project_id)

        if not project:
            raise ValueError("Project not found")

        # Get all tasks
        tasks = self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.is_deleted == False
        ).all()

        # Get all milestones
        milestones = self.db.query(Milestone).filter(
            Milestone.project_id == project_id,
            Milestone.is_deleted == False
        ).all()

        # Build task data
        gantt_tasks = []

        # Add project as root task
        gantt_tasks.append({
            "id": f"project-{project.id}",
            "text": project.name,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "progress": project.progress / 100 if project.progress else 0,
            "type": "project",
            "open": True
        })

        # Add milestones
        for milestone in milestones:
            gantt_tasks.append({
                "id": f"milestone-{milestone.id}",
                "text": milestone.name,
                "start_date": milestone.due_date.isoformat(),
                "end_date": milestone.due_date.isoformat(),
                "type": "milestone",
                "parent": f"project-{project.id}",
                "status": milestone.status.value
            })

        # Add tasks
        for task in tasks:
            task_data = {
                "id": f"task-{task.id}",
                "text": task.title,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.due_date.isoformat() if task.due_date else None,
                "duration": self._calculate_duration(task.start_date, task.due_date),
                "progress": task.progress / 100 if task.progress else 0,
                "type": "task",
                "status": task.status.value,
                "priority": task.priority.value if task.priority else None,
                "assigned_to": task.assigned_to_id
            }

            # Add parent relationship
            if task.parent_task_id:
                task_data["parent"] = f"task-{task.parent_task_id}"
            elif task.milestone_id:
                task_data["parent"] = f"milestone-{task.milestone_id}"
            else:
                task_data["parent"] = f"project-{project.id}"

            gantt_tasks.append(task_data)

        # Build links (dependencies)
        links = []
        link_id = 1

        for task in tasks:
            if task.depends_on:
                for dep_id in task.depends_on:
                    links.append({
                        "id": link_id,
                        "source": f"task-{dep_id}",
                        "target": f"task-{task.id}",
                        "type": "0"  # finish-to-start
                    })
                    link_id += 1

        return {
            "data": gantt_tasks,
            "links": links,
            "project_info": {
                "id": project.id,
                "name": project.name,
                "status": project.status.value,
                "progress": project.progress,
                "budget": project.budget,
                "actual_cost": project.actual_cost
            }
        }

    def _calculate_duration(self, start_date, end_date) -> Optional[int]:
        """Calculate duration in days"""
        if start_date and end_date:
            delta = end_date - start_date
            return delta.days
        return None

    def export_to_mermaid_gantt(self, project_id: int) -> str:
        """
        Export Gantt chart as Mermaid diagram syntax

        Useful for documentation and markdown
        """
        gantt_data = self.generate_project_gantt(project_id)

        mermaid = "gantt\n"
        mermaid += f"    title {gantt_data['project_info']['name']}\n"
        mermaid += "    dateFormat YYYY-MM-DD\n\n"

        # Group by milestone
        milestone_tasks = {}

        for task in gantt_data['data']:
            if task['type'] == 'milestone':
                mermaid += f"    section {task['text']}\n"
                milestone_tasks[task['id']] = []

            elif task['type'] == 'task':
                parent = task.get('parent', '')

                if parent.startswith('milestone-'):
                    if parent not in milestone_tasks:
                        milestone_tasks[parent] = []
                    milestone_tasks[parent].append(task)

        # Add tasks under milestones
        for milestone_id, tasks in milestone_tasks.items():
            for task in tasks:
                status = "done" if task.get('progress', 0) == 1 else "active" if task.get('progress', 0) > 0 else ""
                start = task.get('start_date', '')
                end = task.get('end_date', '')

                if start and end:
                    mermaid += f"    {task['text']} :{status}, {start}, {end}\n"

        return mermaid


class KanbanBoardService:
    """Service for Kanban board management"""

    def __init__(self, db: Session):
        self.db = db

    def generate_kanban_board(
        self,
        project_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate Kanban board data

        Organizes tasks by status columns
        """
        query = self.db.query(Task).filter(Task.is_deleted == False)

        if project_id:
            query = query.filter(Task.project_id == project_id)

        if assigned_to_id:
            query = query.filter(Task.assigned_to_id == assigned_to_id)

        tasks = query.all()

        # Define Kanban columns
        columns = {
            "todo": {
                "id": "todo",
                "title": "To Do",
                "tasks": []
            },
            "in_progress": {
                "id": "in_progress",
                "title": "In Progress",
                "tasks": []
            },
            "in_review": {
                "id": "in_review",
                "title": "In Review",
                "tasks": []
            },
            "blocked": {
                "id": "blocked",
                "title": "Blocked",
                "tasks": []
            },
            "completed": {
                "id": "completed",
                "title": "Completed",
                "tasks": []
            }
        }

        # Organize tasks into columns
        for task in tasks:
            task_card = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if task.priority else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "assigned_to": task.assigned_to_id,
                "progress": task.progress,
                "tags": task.tags,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours
            }

            status_map = {
                TaskStatusEnum.TODO: "todo",
                TaskStatusEnum.IN_PROGRESS: "in_progress",
                TaskStatusEnum.IN_REVIEW: "in_review",
                TaskStatusEnum.BLOCKED: "blocked",
                TaskStatusEnum.COMPLETED: "completed",
                TaskStatusEnum.CANCELLED: "completed"  # Group cancelled with completed
            }

            column_id = status_map.get(task.status, "todo")
            columns[column_id]["tasks"].append(task_card)

        return {
            "columns": list(columns.values()),
            "filters": {
                "project_id": project_id,
                "assigned_to_id": assigned_to_id
            },
            "statistics": {
                "total_tasks": len(tasks),
                "todo": len(columns["todo"]["tasks"]),
                "in_progress": len(columns["in_progress"]["tasks"]),
                "in_review": len(columns["in_review"]["tasks"]),
                "blocked": len(columns["blocked"]["tasks"]),
                "completed": len(columns["completed"]["tasks"])
            }
        }

    def move_task(self, task_id: int, new_status: TaskStatusEnum) -> Task:
        """Move task to different Kanban column (change status)"""
        task = self.db.query(Task).get(task_id)

        if not task:
            raise ValueError("Task not found")

        task.status = new_status

        if new_status == TaskStatusEnum.COMPLETED:
            task.progress = 100
            task.completed_date = datetime.now().date()

        self.db.commit()
        self.db.refresh(task)

        return task


class ResourceUtilizationService:
    """Service for tracking resource utilization"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_team_utilization(
        self,
        user_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate team resource utilization

        Returns workload, capacity, and utilization percentage per user
        """
        from backend.models.workflow import TimeEntry
        from backend.models.user import User

        query = self.db.query(User).filter(User.is_active == True)

        if user_ids:
            query = query.filter(User.id.in_(user_ids))

        users = query.all()

        utilization_data = []

        for user in users:
            # Get time entries for the period
            time_query = self.db.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.is_deleted == False
            )

            if start_date:
                time_query = time_query.filter(TimeEntry.entry_date >= start_date.date())

            if end_date:
                time_query = time_query.filter(TimeEntry.entry_date <= end_date.date())

            total_hours = time_query.with_entities(
                self.db.func.sum(TimeEntry.hours)
            ).scalar() or 0

            # Get assigned tasks
            task_query = self.db.query(Task).filter(
                Task.assigned_to_id == user.id,
                Task.status.in_([TaskStatusEnum.TODO, TaskStatusEnum.IN_PROGRESS]),
                Task.is_deleted == False
            )

            pending_tasks = task_query.count()

            estimated_hours_pending = task_query.with_entities(
                self.db.func.sum(Task.estimated_hours)
            ).scalar() or 0

            # Calculate capacity (assuming 40 hours/week)
            if start_date and end_date:
                weeks = (end_date - start_date).days / 7
                capacity = weeks * 40
            else:
                capacity = 40  # Default to 1 week

            utilization_pct = (float(total_hours) / capacity * 100) if capacity > 0 else 0

            utilization_data.append({
                "user_id": user.id,
                "user_name": user.full_name,
                "total_hours_logged": float(total_hours),
                "capacity_hours": capacity,
                "utilization_percentage": round(utilization_pct, 2),
                "pending_tasks": pending_tasks,
                "estimated_hours_pending": float(estimated_hours_pending),
                "status": "overloaded" if utilization_pct > 100 else "optimal" if utilization_pct > 70 else "available"
            })

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "team_utilization": utilization_data,
            "team_summary": {
                "total_users": len(utilization_data),
                "avg_utilization": round(
                    sum(u["utilization_percentage"] for u in utilization_data) / len(utilization_data), 2
                ) if utilization_data else 0,
                "overloaded_users": len([u for u in utilization_data if u["status"] == "overloaded"]),
                "available_users": len([u for u in utilization_data if u["status"] == "available"])
            }
        }
