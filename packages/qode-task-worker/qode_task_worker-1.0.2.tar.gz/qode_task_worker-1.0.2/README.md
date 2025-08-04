# Task Worker Library

A Python library for task management with RabbitMQ and polling support. This library provides a unified interface for consuming tasks from a task management API with automatic fallback between RabbitMQ and polling modes.

## Features

- **Dual Mode Support**: RabbitMQ with manual acknowledgment/nack and polling fallback
- **Automatic Fallback**: Seamlessly switches to polling if RabbitMQ is unavailable
- **Manual Acknowledgment**: Proper message handling with ack/nack for RabbitMQ
- **Configurable**: Flexible configuration for different environments
- **Error Handling**: Robust error handling with retry mechanisms
- **Logging**: Comprehensive logging for debugging and monitoring

## Installation

```bash
pip install task-worker
```

For development:
```bash
pip install task-worker[dev]
```

## Quick Start

```python
import logging
from task_worker import TaskWorker, TaskWorkerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define your task processing function
def process_my_task(task):
    """Your custom task processing logic"""
    task_id = task.get('id')
    metadata = task.get('metadata', {})
    
    print(f"Processing task {task_id}: {metadata}")
    
    # Your business logic here
    # ...
    
    # The library handles task registration and result saving
    # You just need to process the task data

# Configure the worker
config = TaskWorkerConfig(
    task_management_endpoint="https://your-task-api.com",
    rabbitmq_consumer_host="amqps://user:pass@your-rabbitmq.com/vhost",
    task_type="your-task-type",
    worker_name="my-worker",
    polling_interval=5
)

# Create and start the worker
worker = TaskWorker(config, process_my_task)
worker.start()  # This will run indefinitely
```

## Configuration

### TaskWorkerConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_management_endpoint` | str | ENV or default URL | Task management API endpoint |
| `rabbitmq_consumer_host` | str | ENV or None | RabbitMQ connection URL |
| `task_type` | str | "default" | Type of tasks to process |
| `worker_name` | str | hostname | Worker identifier |
| `polling_interval` | int | 5 | Seconds between polls in polling mode |
| `rabbitmq_queue_prefix` | str | "task.available" | RabbitMQ queue prefix |
| `prefetch_count` | int | 1 | RabbitMQ prefetch count |
| `max_retry_attempts` | int | 3 | Max retry attempts for API calls |

### Environment Variables

The library automatically reads from these environment variables:

- `TASK_MANAGEMENT_ENDPOINT`: Task management API URL
- `RABBITMQ_CONSUMER_HOST`: RabbitMQ connection string

## Advanced Usage

### Custom Task Result Saving

```python
from task_worker import TaskWorker, TaskWorkerConfig, TaskClient

config = TaskWorkerConfig(
    task_management_endpoint="https://your-api.com",
    task_type="processing"
)

task_client = TaskClient(config)

def advanced_task_processor(task):
    task_id = task.get('id')
    
    try:
        # Your processing logic
        result_data = {
            "meetingId": task.get('metadata', {}).get('meetingId'),
            "taskName": task.get('taskType'),
            "taskId": task_id,
            "moduleName": "YOUR_MODULE",
            "result": {"status": "completed", "data": "..."},
            "count": 1,
        }
        
        # Save result manually if needed
        task_client.save_task_result(
            task_id=task_id,
            task_data=result_data,
            task_type=task.get('taskType', ''),
            task_webhook_api=task.get('webhookApi', '')
        )
        
    except Exception as e:
        logging.error(f"Processing failed for task {task_id}: {e}")
        raise  # Re-raise to trigger nack in RabbitMQ mode

worker = TaskWorker(config, advanced_task_processor)
worker.start()
```

### RabbitMQ Only Mode

```python
from task_worker import RabbitMQWorker, TaskWorkerConfig

config = TaskWorkerConfig(
    task_management_endpoint="https://your-api.com",
    rabbitmq_consumer_host="amqps://user:pass@rabbitmq.com/vhost",
    task_type="urgent-tasks"
)

def process_urgent_task(task):
    # Process urgent tasks only via RabbitMQ
    pass

# Use RabbitMQ worker directly (no polling fallback)
rabbitmq_worker = RabbitMQWorker(config, process_urgent_task)

if rabbitmq_worker.connect():
    rabbitmq_worker.start_consuming()
else:
    print("Failed to connect to RabbitMQ")
```

### Status Monitoring

```python
worker = TaskWorker(config, process_task)

# Get worker status
status = worker.get_status()
print(f"Mode: {status['mode']}")
print(f"Task Type: {status['task_type']}")
print(f"RabbitMQ Connected: {status['rabbitmq_connected']}")

# Check if running in RabbitMQ mode
if worker.is_running_rabbitmq_mode():
    print("Running with RabbitMQ")
else:
    print("Running in polling mode")
```

## Error Handling

The library provides robust error handling:

### RabbitMQ Mode
- **Message Parsing Errors**: Messages are nacked without requeue to prevent infinite loops
- **Task Processing Errors**: Messages are nacked with requeue for retry by other workers
- **Connection Failures**: Automatic fallback to polling mode

### Polling Mode
- **API Failures**: Logged and retried after polling interval
- **Processing Errors**: Logged (no requeue mechanism in polling)

### Custom Error Handling

```python
def robust_task_processor(task):
    try:
        # Your processing logic
        process_task_logic(task)
        
    except TemporaryError as e:
        logging.warning(f"Temporary error, will retry: {e}")
        raise  # This will trigger nack with requeue in RabbitMQ
        
    except PermanentError as e:
        logging.error(f"Permanent error, not retrying: {e}")
        # Don't raise - this will ack the message
        
    except Exception as e:
        logging.error(f"Unknown error: {e}")
        raise  # Let the library handle it
```

## Message Format

Expected RabbitMQ message format:

```json
{
  "taskType": "your-task-type",
  "metadata": {
    "additional": "data"
  }
}
```

Task API response format:

```json
{
  "data": {
    "id": "task-id-123",
    "taskType": "your-task-type", 
    "metadata": {
      "meetingId": "meeting-123",
      "cheatingType": "browser",
      "batchTranscript": "..."
    },
    "webhookApi": "https://callback-url.com"
  }
}
```

## Testing

```python
# For testing, you can mock the task processor
def mock_task_processor(task):
    print(f"Mock processing task: {task}")

config = TaskWorkerConfig(
    task_management_endpoint="http://localhost:4000",
    task_type="test",
    polling_interval=1  # Faster polling for testing
)

worker = TaskWorker(config, mock_task_processor)
worker.start()
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request 