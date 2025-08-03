"""
Workflow Engine for healthcare process orchestration
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio
from pydantic import BaseModel, Field
import structlog
from dataclasses import dataclass
import json

logger = structlog.get_logger()


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class TaskType(str, Enum):
    """Types of workflow tasks"""
    API_CALL = "api_call"
    TRANSFORMATION = "transformation"
    DECISION = "decision"
    NOTIFICATION = "notification"
    HUMAN_TASK = "human_task"
    SCRIPT = "script"
    PARALLEL = "parallel"
    SEQUENCE = "sequence"


@dataclass
class TaskResult:
    """Result of task execution"""
    status: TaskStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class Task(BaseModel):
    """Workflow task definition"""
    
    id: str
    name: str
    type: TaskType
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = None


class ProcessDefinition(BaseModel):
    """Healthcare process definition"""
    
    id: str
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    tasks: List[Task]
    variables: Dict[str, Any] = Field(default_factory=dict)
    triggers: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowInstance(BaseModel):
    """Running workflow instance"""
    
    id: str
    process_id: str
    status: TaskStatus = TaskStatus.PENDING
    variables: Dict[str, Any] = Field(default_factory=dict)
    task_results: Dict[str, TaskResult] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowEngine:
    """
    Healthcare workflow orchestration engine
    
    Features:
    - Visual workflow designer compatible
    - Async task execution
    - Error handling and retries
    - Human task management
    - Event-driven triggers
    """
    
    def __init__(self):
        self.processes: Dict[str, ProcessDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.task_handlers: Dict[TaskType, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default task handlers"""
        self.task_handlers[TaskType.API_CALL] = self._handle_api_call
        self.task_handlers[TaskType.TRANSFORMATION] = self._handle_transformation
        self.task_handlers[TaskType.DECISION] = self._handle_decision
        self.task_handlers[TaskType.NOTIFICATION] = self._handle_notification
        self.task_handlers[TaskType.PARALLEL] = self._handle_parallel
        self.task_handlers[TaskType.SEQUENCE] = self._handle_sequence
    
    def register_process(self, process: ProcessDefinition):
        """Register a process definition"""
        self.processes[process.id] = process
        logger.info("Registered process", 
                   process_id=process.id,
                   name=process.name)
    
    async def start_process(self, 
                          process_id: str,
                          variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new workflow instance
        
        Args:
            process_id: Process definition ID
            variables: Initial variables
            
        Returns:
            Instance ID
        """
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        
        process = self.processes[process_id]
        
        # Create instance
        instance = WorkflowInstance(
            id=f"{process_id}_{datetime.utcnow().timestamp()}",
            process_id=process_id,
            variables={**process.variables, **(variables or {})}
        )
        
        self.instances[instance.id] = instance
        
        logger.info("Started workflow instance",
                   instance_id=instance.id,
                   process_id=process_id)
        
        # Start execution
        asyncio.create_task(self._execute_instance(instance.id))
        
        return instance.id
    
    async def _execute_instance(self, instance_id: str):
        """Execute workflow instance"""
        instance = self.instances[instance_id]
        process = self.processes[instance.process_id]
        
        instance.status = TaskStatus.RUNNING
        
        try:
            # Execute tasks in dependency order
            for task in self._get_execution_order(process.tasks):
                if instance.status == TaskStatus.CANCELLED:
                    break
                
                await self._execute_task(instance, task)
            
            if instance.status != TaskStatus.CANCELLED:
                instance.status = TaskStatus.COMPLETED
        except Exception as e:
            logger.error("Workflow execution failed",
                       instance_id=instance_id,
                       error=str(e))
            instance.status = TaskStatus.FAILED
        finally:
            instance.updated_at = datetime.utcnow()
    
    async def _execute_task(self, 
                          instance: WorkflowInstance,
                          task: Task) -> TaskResult:
        """Execute a single task"""
        logger.info("Executing task",
                   instance_id=instance.id,
                   task_id=task.id,
                   task_type=task.type)
        
        # Check dependencies
        for dep_id in task.dependencies:
            dep_result = instance.task_results.get(dep_id)
            if not dep_result or dep_result.status != TaskStatus.COMPLETED:
                logger.warning("Skipping task due to failed dependency",
                             task_id=task.id,
                             dependency=dep_id)
                result = TaskResult(status=TaskStatus.SKIPPED)
                instance.task_results[task.id] = result
                return result
        
        # Execute task
        result = TaskResult(
            status=TaskStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        instance.task_results[task.id] = result
        
        try:
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise ValueError(f"No handler for task type {task.type}")
            
            output = await handler(task, instance)
            
            result.status = TaskStatus.COMPLETED
            result.output = output
            result.completed_at = datetime.utcnow()
        except Exception as e:
            logger.error("Task execution failed",
                       task_id=task.id,
                       error=str(e))
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow()
        
        return result
    
    def _get_execution_order(self, tasks: List[Task]) -> List[Task]:
        """Get tasks in execution order based on dependencies"""
        # Simple topological sort
        visited = set()
        order = []
        
        def visit(task: Task):
            if task.id in visited:
                return
            
            visited.add(task.id)
            
            # Visit dependencies first
            for dep_id in task.dependencies:
                dep_task = next((t for t in tasks if t.id == dep_id), None)
                if dep_task:
                    visit(dep_task)
            
            order.append(task)
        
        for task in tasks:
            visit(task)
        
        return order
    
    async def _handle_api_call(self, 
                             task: Task,
                             instance: WorkflowInstance) -> Any:
        """Handle API call task"""
        config = task.config
        
        # Extract configuration
        method = config.get("method", "GET")
        url = config.get("url", "")
        headers = config.get("headers", {})
        body = config.get("body", {})
        
        # Variable substitution
        url = self._substitute_variables(url, instance.variables)
        body = self._substitute_variables(body, instance.variables)
        
        # Make API call (simplified for demo)
        logger.info("Making API call", method=method, url=url)
        
        # In production, would use actual HTTP client
        return {"status": "success", "method": method, "url": url}
    
    async def _handle_transformation(self,
                                   task: Task,
                                   instance: WorkflowInstance) -> Any:
        """Handle data transformation task"""
        config = task.config
        transform = config.get("transform", {})
        
        logger.info("Performing transformation", transform_type=transform.get("type"))
        
        # Simplified transformation
        return {"transformed": True, "type": transform.get("type")}
    
    async def _handle_decision(self,
                             task: Task,
                             instance: WorkflowInstance) -> Any:
        """Handle decision task"""
        config = task.config
        rules = config.get("rules", [])
        
        for rule in rules:
            condition = rule.get("condition", {})
            if self._evaluate_condition(condition, instance.variables):
                # Execute actions
                actions = rule.get("actions", [])
                for action in actions:
                    await self._execute_action(action, instance)
                return True
        
        return False
    
    async def _handle_notification(self,
                                 task: Task,
                                 instance: WorkflowInstance) -> Any:
        """Handle notification task"""
        config = task.config
        
        notification_type = config.get("type", "email")
        recipient = config.get("recipient", "")
        template = config.get("template", "")
        
        logger.info("Sending notification",
                   type=notification_type,
                   recipient=recipient)
        
        return {"sent": True, "timestamp": datetime.utcnow()}
    
    async def _handle_parallel(self,
                             task: Task,
                             instance: WorkflowInstance) -> Any:
        """Handle parallel task execution"""
        subtasks = task.config.get("tasks", [])
        
        # Execute subtasks in parallel
        tasks = []
        for subtask_config in subtasks:
            subtask = Task(**subtask_config)
            tasks.append(self._execute_task(instance, subtask))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def _handle_sequence(self,
                             task: Task,
                             instance: WorkflowInstance) -> Any:
        """Handle sequential task execution"""
        subtasks = task.config.get("tasks", [])
        
        results = []
        for subtask_config in subtasks:
            subtask = Task(**subtask_config)
            result = await self._execute_task(instance, subtask)
            results.append(result)
            
            if result.status == TaskStatus.FAILED:
                break
        
        return results
    
    def _substitute_variables(self, 
                            template: Any,
                            variables: Dict[str, Any]) -> Any:
        """Substitute variables in template"""
        if isinstance(template, str):
            # Simple variable substitution
            for key, value in variables.items():
                template = template.replace(f"${{{key}}}", str(value))
            return template
        elif isinstance(template, dict):
            return {
                k: self._substitute_variables(v, variables)
                for k, v in template.items()
            }
        elif isinstance(template, list):
            return [
                self._substitute_variables(item, variables)
                for item in template
            ]
        return template
    
    def _evaluate_condition(self,
                          condition: Dict[str, Any],
                          variables: Dict[str, Any]) -> bool:
        """Evaluate condition"""
        operator = condition.get("operator", "eq")
        left = condition.get("left", "")
        right = condition.get("right", "")
        
        left_value = self._get_variable_value(left, variables)
        right_value = self._get_variable_value(right, variables)
        
        if operator == "eq":
            return left_value == right_value
        elif operator == "gt":
            return float(left_value) > float(right_value)
        elif operator == "lt":
            return float(left_value) < float(right_value)
        
        return False
    
    def _get_variable_value(self, 
                          expr: str,
                          variables: Dict[str, Any]) -> Any:
        """Get variable value from expression"""
        if expr.startswith("$"):
            var_name = expr[1:]
            return variables.get(var_name)
        return expr
    
    async def _execute_action(self,
                            action: Dict[str, Any],
                            instance: WorkflowInstance):
        """Execute action"""
        action_type = action.get("type", "")
        
        if action_type == "set_variable":
            var_name = action.get("variable", "")
            value = action.get("value", "")
            instance.variables[var_name] = value
        elif action_type == "notification":
            logger.info("Action: notification", recipient=action.get("recipient"))
    
    def get_instance_status(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance status"""
        return self.instances.get(instance_id)
    
    def cancel_instance(self, instance_id: str) -> bool:
        """Cancel workflow instance"""
        instance = self.instances.get(instance_id)
        if instance and instance.status == TaskStatus.RUNNING:
            instance.status = TaskStatus.CANCELLED
            logger.info("Cancelled workflow instance", instance_id=instance_id)
            return True
        return False