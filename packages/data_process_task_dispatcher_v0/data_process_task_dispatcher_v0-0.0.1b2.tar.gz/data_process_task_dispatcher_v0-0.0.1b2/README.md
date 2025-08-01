# Cerry Test Project

A well-structured Celery project with Redis backend and Flower monitoring.

## Prerequisites

- Python 3.8+
- Redis server
- Poetry (recommended) or pip

## Installation

1. Install dependencies:

```bash
# Using pip
pip install -e .

# Or using Poetry
poetry install
```

2. Start Redis server:

```bash
redis-server
```

## Running the Project

1. Start Celery worker:

```bash
celery -A cerry_test worker --loglevel=info
```

2. Start Celery beat (for periodic tasks):

```bash
celery -A cerry_test beat --loglevel=info
```

3. Start Flower monitoring:

```bash
celery -A cerry_test flower
```

4. Run the example:

```bash
python main.py
```

## Project Structure

```
cerry_test/
├── cerry_test/
│   ├── __init__.py        # Celery app initialization
│   ├── config/
│   │   └── celeryconfig.py # Celery configuration
│   ├── tasks/
│   │   └── example.py     # Example tasks
│   └── logs/              # Log files
├── main.py                # Example usage
├── pyproject.toml         # Project dependencies
└── README.md             # This file
```

## Features

- Redis as message broker and result backend
- Task progress tracking
- Periodic tasks with Celery Beat
- Task chains
- Flower monitoring interface
- Structured logging

## Monitoring

Access Flower monitoring interface at: http://localhost:5555

## Task Examples

1. Simple addition task:

```python
from cerry_test.tasks.example import add
result = add.delay(4, 4)
```

2. Progress tracking task:

```python
from cerry_test.tasks.example import process_data
result = process_data.delay([1, 2, 3, 4, 5])
```

3. Task chain:

```python
from cerry_test.tasks.example import create_processing_chain
chain = create_processing_chain([1, 2, 3])
result = chain()
```
