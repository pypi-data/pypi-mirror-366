"""
Task Client module for handling task management API interactions
"""
import requests
import logging
from typing import Optional, Dict, Any
from .config import TaskWorkerConfig


class TaskClient:
    """Client for interacting with task management APIs"""
    
    def __init__(self, config: TaskWorkerConfig):
        """
        Initialize TaskClient
        
        Args:
            config: TaskWorkerConfig instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def register_task(self) -> Optional[Dict[str, Any]]:
        """
        Register for a new task from the task management API
        
        Returns:
            Task data if available, None otherwise
        """
        try:
            response = requests.patch(
                url=f"{self.config.task_management_endpoint}/api/task/register",
                json={
                    "taskType": self.config.task_type,
                    "workerName": self.config.worker_name,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                task = response.json()
                if task.get("data") is not None:
                    self.logger.info(f"Successfully registered task: {task.get('data', {}).get('id')}")
                    return task.get("data")
                    
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to register task: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during task registration: {e}")
            
        return None
        
    def save_task_result(
        self, 
        task_id: str, 
        task_data: Dict[str, Any], 
        task_type: str, 
        task_webhook_api: str = ""
    ) -> Optional[requests.Response]:
        """
        Save task result to the task management API
        
        Args:
            task_id: ID of the task
            task_data: Result data to save
            task_type: Type of the task
            task_webhook_api: Webhook API endpoint (optional)
            
        Returns:
            Response object if successful, None otherwise
        """
        try:
            response = requests.patch(
                url=f"{self.config.task_management_endpoint}/api/task/finish",
                json={
                    "taskId": task_id,
                    "taskData": task_data,
                    "taskType": task_type,
                    "webhookApi": task_webhook_api,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully saved task result for task: {task_id}")
                return response
            else:
                self.logger.error(f"Failed to save task result, status: {response.status_code}, response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to save task result for task {task_id}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error saving task result for task {task_id}: {e}")
            
        return None 