# Task

Types:

```python
from chunkr_ai.types import (
    AutoGenerationConfig,
    BoundingBox,
    ChunkProcessing,
    IgnoreGenerationConfig,
    LlmGenerationConfig,
    LlmProcessing,
    PictureGenerationConfig,
    SegmentProcessing,
    TableGenerationConfig,
    Task,
)
```

Methods:

- <code title="patch /task/{task_id}/parse">client.task.<a href="./src/chunkr_ai/resources/task.py">update</a>(task_id, \*\*<a href="src/chunkr_ai/types/task_update_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">Task</a></code>
- <code title="get /tasks">client.task.<a href="./src/chunkr_ai/resources/task.py">list</a>(\*\*<a href="src/chunkr_ai/types/task_list_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">SyncTasksPage[Task]</a></code>
- <code title="delete /task/{task_id}">client.task.<a href="./src/chunkr_ai/resources/task.py">delete</a>(task_id) -> None</code>
- <code title="get /task/{task_id}/cancel">client.task.<a href="./src/chunkr_ai/resources/task.py">cancel</a>(task_id) -> None</code>
- <code title="get /task/{task_id}">client.task.<a href="./src/chunkr_ai/resources/task.py">get</a>(task_id, \*\*<a href="src/chunkr_ai/types/task_get_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">Task</a></code>
- <code title="post /task/parse">client.task.<a href="./src/chunkr_ai/resources/task.py">parse</a>(\*\*<a href="src/chunkr_ai/types/task_parse_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">Task</a></code>

# Health

Types:

```python
from chunkr_ai.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/chunkr_ai/resources/health.py">check</a>() -> str</code>
