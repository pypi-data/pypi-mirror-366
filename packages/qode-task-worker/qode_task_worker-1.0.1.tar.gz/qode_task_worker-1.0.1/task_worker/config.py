"""
Configuration module for Task Worker library
"""
import os
from typing import Optional
import socket


class TaskWorkerConfig:
    """Configuration class for Task Worker library"""
    
    def __init__(
        self,
        task_management_endpoint: Optional[str] = None,
        rabbitmq_consumer_host: Optional[str] = None,
        task_type: str = "default",
        worker_name: Optional[str] = None,
        polling_interval: int = 5,
        rabbitmq_queue_prefix: str = "task.available",
        prefetch_count: int = 1,
        max_retry_attempts: int = 3,
    ):
        """
        Initialize TaskWorkerConfig
        
        Args:
            task_management_endpoint: URL for task management API
            rabbitmq_consumer_host: RabbitMQ connection URL  
            task_type: Type of tasks this worker processes
            worker_name: Name identifier for this worker
            polling_interval: Seconds to wait between polls in polling mode
            rabbitmq_queue_prefix: Prefix for RabbitMQ queue names
            prefetch_count: Number of messages to prefetch from RabbitMQ
            max_retry_attempts: Maximum retry attempts for failed API calls
        """
        self.task_management_endpoint = (
            task_management_endpoint 
        )
        
        self.rabbitmq_consumer_host = (
            rabbitmq_consumer_host 
        )
        
        self.task_type = task_type
        self.worker_name = worker_name or socket.gethostname()
        self.polling_interval = polling_interval
        self.rabbitmq_queue_prefix = rabbitmq_queue_prefix
        self.prefetch_count = prefetch_count
        self.max_retry_attempts = max_retry_attempts
        
    @property
    def rabbitmq_queue_name(self) -> str:
        """Get the full RabbitMQ queue name"""
        return f"{self.rabbitmq_queue_prefix}.{self.task_type}"
        
    def validate(self) -> None:
        """Validate configuration"""
        if not self.task_management_endpoint:
            raise ValueError("task_management_endpoint is required")
            
        if not self.task_type:
            raise ValueError("task_type is required")
            
        if not self.worker_name:
            raise ValueError("worker_name is required") 