"""Tests for workflow engine."""

import pytest
import asyncio
from pyheart.core.workflow import WorkflowEngine, ProcessDefinition, Task, TaskType


def test_workflow_engine_initialization():
    """Test workflow engine initialization."""
    engine = WorkflowEngine()
    assert len(engine.processes) == 0
    assert len(engine.instances) == 0
    assert TaskType.API_CALL in engine.task_handlers


def test_process_registration():
    """Test process definition registration."""
    engine = WorkflowEngine()
    
    process = ProcessDefinition(
        id="test-process",
        name="Test Process",
        tasks=[
            Task(
                id="task1",
                name="Test Task",
                type=TaskType.NOTIFICATION,
                config={"message": "Hello"}
            )
        ]
    )
    
    engine.register_process(process)
    assert "test-process" in engine.processes
    assert engine.processes["test-process"].name == "Test Process"


@pytest.mark.asyncio
async def test_simple_workflow_execution():
    """Test simple workflow execution."""
    engine = WorkflowEngine()
    
    process = ProcessDefinition(
        id="simple-workflow",
        name="Simple Workflow",
        tasks=[
            Task(
                id="notify",
                name="Send Notification",
                type=TaskType.NOTIFICATION,
                config={"type": "email", "recipient": "test@example.com"}
            )
        ]
    )
    
    engine.register_process(process)
    instance_id = await engine.start_process("simple-workflow")
    
    # Wait for execution
    await asyncio.sleep(0.1)
    
    instance = engine.get_instance_status(instance_id)
    assert instance is not None
    assert instance.process_id == "simple-workflow"


def test_task_dependency_ordering():
    """Test task execution order based on dependencies."""
    engine = WorkflowEngine()
    
    tasks = [
        Task(id="task3", name="Task 3", type=TaskType.NOTIFICATION, dependencies=["task1", "task2"]),
        Task(id="task1", name="Task 1", type=TaskType.NOTIFICATION),
        Task(id="task2", name="Task 2", type=TaskType.NOTIFICATION, dependencies=["task1"])
    ]
    
    ordered_tasks = engine._get_execution_order(tasks)
    task_ids = [task.id for task in ordered_tasks]
    
    assert task_ids.index("task1") < task_ids.index("task2")
    assert task_ids.index("task2") < task_ids.index("task3")


@pytest.mark.asyncio
async def test_workflow_with_dependencies():
    """Test workflow with task dependencies."""
    engine = WorkflowEngine()
    
    process = ProcessDefinition(
        id="dependent-workflow",
        name="Dependent Workflow",
        tasks=[
            Task(
                id="first",
                name="First Task",
                type=TaskType.NOTIFICATION,
                config={"message": "First"}
            ),
            Task(
                id="second",
                name="Second Task",
                type=TaskType.NOTIFICATION,
                dependencies=["first"],
                config={"message": "Second"}
            )
        ]
    )
    
    engine.register_process(process)
    instance_id = await engine.start_process("dependent-workflow")
    
    # Wait for execution
    await asyncio.sleep(0.1)
    
    instance = engine.get_instance_status(instance_id)
    assert len(instance.task_results) == 2
    assert "first" in instance.task_results
    assert "second" in instance.task_results


def test_variable_substitution():
    """Test variable substitution in templates."""
    engine = WorkflowEngine()
    
    template = "Hello ${name}, your age is ${age}"
    variables = {"name": "John", "age": 30}
    
    result = engine._substitute_variables(template, variables)
    assert result == "Hello John, your age is 30"


def test_condition_evaluation():
    """Test condition evaluation."""
    engine = WorkflowEngine()
    
    condition = {"operator": "gt", "left": "$age", "right": "65"}
    variables = {"age": 70}
    
    result = engine._evaluate_condition(condition, variables)
    assert result is True
    
    variables = {"age": 30}
    result = engine._evaluate_condition(condition, variables)
    assert result is False