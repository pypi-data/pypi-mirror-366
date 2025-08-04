"""
Task Worker Library

A Python library for task management with RabbitMQ and polling support.
"""

from .task_client import TaskClient
from .rabbitmq_worker import RabbitMQWorker  
from .task_worker import TaskWorker
from .config import TaskWorkerConfig

__version__ = "1.0.2"
__all__ = ["TaskClient", "RabbitMQWorker", "TaskWorker", "TaskWorkerConfig"] 