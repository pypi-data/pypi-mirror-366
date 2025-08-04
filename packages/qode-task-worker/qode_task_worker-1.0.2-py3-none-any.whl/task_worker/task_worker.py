"""
Main Task Worker module that combines RabbitMQ and polling modes
"""
import time
import logging
from typing import Callable, Dict, Any, Optional
import requests.exceptions

from .config import TaskWorkerConfig
from .task_client import TaskClient
from .rabbitmq_worker import RabbitMQWorker


class TaskWorker:
    """
    Main task worker that supports both RabbitMQ and polling modes with automatic fallback
    """
    
    def __init__(self, config: TaskWorkerConfig, task_processor: Callable[[Dict[str, Any]], None]):
        """
        Initialize TaskWorker
        
        Args:
            config: TaskWorkerConfig instance
            task_processor: Function to process tasks, should accept task dict
        """
        self.config = config
        self.task_processor = task_processor
        self.task_client = TaskClient(config)
        self.rabbitmq_worker = None
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        self.config.validate()
        
        # Initialize RabbitMQ worker if configured
        if self.config.rabbitmq_consumer_host:
            self.rabbitmq_worker = RabbitMQWorker(config, task_processor)
    
    def process_task_with_callback(
        self, 
        task_processor_callback: Callable[[Dict[str, Any]], Dict[str, Any]], 
        task_type: str = None,
        webhook_api: str = ""
    ) -> bool:
        """
        Complete task processing flow: register -> process -> save result
        
        Args:
            task_processor_callback: Function that processes task and returns result data
            task_type: Optional task type override
            webhook_api: Optional webhook API endpoint
            
        Returns:
            True if task was processed successfully, False otherwise
        """
        try:
            task = self.task_client.register_task()
            
            if task is None:
                self.logger.debug("No task available")
                return False
            
            task_id = task.get('id')
            self.logger.info(f"Processing task: {task_id}")
            
            result_data = task_processor_callback(task)
            
            if result_data is None:
                self.logger.warning(f"No result data returned for task: {task_id}")
                return False
            
            actual_task_type = task_type or task.get('taskType', self.config.task_type)
            actual_webhook = webhook_api or task.get('webhookApi', '')
            
            self.task_client.save_task_result(
                task_id=task_id,
                task_data=result_data,
                task_type=actual_task_type,
                task_webhook_api=actual_webhook
            )
            
            self.logger.info(f"Successfully processed and saved result for task: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in task processing flow: {e}")
            return False
    
    def start(self) -> None:
        """
        Start the task worker. Tries RabbitMQ first, falls back to polling if needed.
        """
        self.logger.info("Starting Task Worker...")
        
        # Try RabbitMQ mode first if configured
        if self.config.rabbitmq_consumer_host and self.rabbitmq_worker:
            self.logger.info("RabbitMQ configured, attempting to connect...")
            
            if self.rabbitmq_worker.connect():
                try:
                    self.rabbitmq_worker.start_consuming()
                    return  # RabbitMQ mode successful
                except Exception as e:
                    self.logger.error(f"RabbitMQ consumption failed: {e}")
                    self.logger.info("Falling back to polling mode...")
            else:
                self.logger.info("RabbitMQ connection failed, falling back to polling mode...")
        else:
            self.logger.info("RabbitMQ not configured, using polling mode...")
        
        # Fallback to polling mode
        self._start_polling_mode()
    
    def _start_polling_mode(self) -> None:
        """
        Start polling mode - continuously polls for tasks
        """
        self.logger.info(f"Starting polling mode with {self.config.polling_interval}s intervals...")
        
        while True:
            try:
                task = self.task_client.register_task()
                
                if task is None:
                    self.logger.debug(f"No task available, sleeping for {self.config.polling_interval} seconds...")
                    time.sleep(self.config.polling_interval)
                    continue
                
                try:
                    # Process the task
                    self.task_processor(task)
                    self.logger.info(f"Successfully processed task in polling mode: {task.get('id')}")
                    
                except Exception as e:
                    self.logger.error(f"Task processing failed in polling mode: {e}")
                    # In polling mode, we can't requeue, so we just log the error
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to register task in polling mode: {e}")
                time.sleep(self.config.polling_interval)
                
            except KeyboardInterrupt:
                self.logger.info('Polling mode interrupted by user')
                break
                
            except Exception as e:
                self.logger.error(f"Unexpected error in polling mode: {e}")
                time.sleep(self.config.polling_interval)
    
    def stop(self) -> None:
        """
        Stop the task worker
        """
        self.logger.info("Stopping Task Worker...")
        
        if self.rabbitmq_worker and self.rabbitmq_worker.is_connected():
            self.rabbitmq_worker.stop_consuming()
            
        self.logger.info("Task Worker stopped")
    
    def is_running_rabbitmq_mode(self) -> bool:
        """
        Check if currently running in RabbitMQ mode
        
        Returns:
            True if running in RabbitMQ mode, False if polling mode
        """
        return (self.rabbitmq_worker is not None and 
                self.rabbitmq_worker.is_connected())
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the task worker
        
        Returns:
            Dictionary with status information
        """
        return {
            "mode": "rabbitmq" if self.is_running_rabbitmq_mode() else "polling",
            "task_type": self.config.task_type,
            "worker_name": self.config.worker_name,
            "task_management_endpoint": self.config.task_management_endpoint,
            "rabbitmq_configured": self.config.rabbitmq_consumer_host is not None,
            "rabbitmq_connected": self.is_running_rabbitmq_mode(),
            "polling_interval": self.config.polling_interval
        } 