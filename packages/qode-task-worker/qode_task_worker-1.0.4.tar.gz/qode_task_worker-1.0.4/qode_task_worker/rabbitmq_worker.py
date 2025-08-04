"""
RabbitMQ Worker module for handling message consumption with manual acknowledgment
"""
import pika
import json
import logging
from typing import Callable, Dict, Any, Optional
from .config import TaskWorkerConfig
from .task_client import TaskClient


class RabbitMQWorker:
    """Worker class for consuming RabbitMQ messages with manual acknowledgment"""
    
    def __init__(self, config: TaskWorkerConfig, task_processor: Callable[[Dict[str, Any]], None]):
        """
        Initialize RabbitMQWorker
        
        Args:
            config: TaskWorkerConfig instance
            task_processor: Function to process tasks, should accept task dict
        """
        self.config = config
        self.task_processor = task_processor
        self.task_client = TaskClient(config)
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.channel = None
        
    def _callback(self, ch, method, properties, body):
        """
        RabbitMQ message callback with manual acknowledgment
        """
        try:
            message = json.loads(body.decode('utf-8'))
            self.logger.info(f"Received message from RabbitMQ: {message}")
            
            # Check if message is suitable for processing
            if (message.get('taskType') == self.config.task_type ):                
                self.logger.info("Suitable task found, calling register_task API")
                
                # Get task from API
                task = self.task_client.register_task()
                
                if task:
                    self.logger.info(f"Retrieved task from API: {task.get('id')}")
                    
                    try:
                        # Process the task using the callback
                        result_data = self.task_processor(task)
                        
                        if result_data is not None:
                            # Save the result
                            self.task_client.save_task_result(
                                task_id=task.get('id'),
                                task_data=result_data,
                                task_type=task.get('taskType', self.config.task_type),
                                task_webhook_api=task.get('webhookApi', '')
                            )
                            self.logger.info(f"Successfully processed and saved result for task: {task.get('id')}")
                        
                        # Only acknowledge after successful processing
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        self.logger.info(f"Successfully processed and acknowledged task: {task.get('id')}")
                        
                    except Exception as e:
                        self.logger.error(f"Task processing failed: {e}")
                        # Processing failed, reject and requeue for retry
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                        self.logger.info(f"Message requeued due to processing error: {e}")
                        
                else:
                    self.logger.info("No task available from register_task API")
                    # No task available, acknowledge to remove message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
            else:
                self.logger.info(f"Message not suitable for processing: {message}")
                # Message not suitable, acknowledge to remove it
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse RabbitMQ message: {e}")
            # Malformed message, reject without requeue to avoid infinite loop
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            self.logger.error(f"Error processing RabbitMQ message: {e}")
            # Processing failed, reject and requeue for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            self.logger.info(f"Message requeued due to processing error: {e}")
    
    def connect(self) -> bool:
        """
        Connect to RabbitMQ
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to RabbitMQ: {self.config.rabbitmq_consumer_host}")
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.config.rabbitmq_consumer_host)
            )
            self.channel = self.connection.channel()
            
            # Set QoS to process messages one at a time for better error handling
            self.channel.basic_qos(prefetch_count=self.config.prefetch_count)
            
            return True
            
        except pika.exceptions.AMQPConnectionError as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to RabbitMQ: {e}")
            return False
    
    def start_consuming(self) -> None:
        """
        Start consuming messages from RabbitMQ queue
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ. Call connect() first.")
            
        try:
            self.channel.basic_consume(
                queue=self.config.rabbitmq_queue_name,
                on_message_callback=self._callback,
                auto_ack=False  # IMPORTANT: Manual acknowledgment
            )
            
            self.logger.info(f'Connected to RabbitMQ with manual ack. Consuming queue: {self.config.rabbitmq_queue_name}')
            self.logger.info('Waiting for messages. To exit press CTRL+C')
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            self.logger.info('Interrupted by user')
            self.stop_consuming()
        except Exception as e:
            self.logger.error(f"Error during message consumption: {e}")
            raise
    
    def stop_consuming(self) -> None:
        """Stop consuming messages and close connections"""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
        except Exception as e:
            self.logger.error(f"Error stopping consumer: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to RabbitMQ"""
        return (self.connection is not None and 
                not self.connection.is_closed and 
                self.channel is not None and 
                not self.channel.is_closed) 