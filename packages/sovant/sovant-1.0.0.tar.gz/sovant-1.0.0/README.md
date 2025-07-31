# Sovant Python SDK

Official Python SDK for the Sovant Memory API. Build AI applications with persistent memory, semantic search, and intelligent context management.

> **Note: Coming Soon!** This SDK is currently in development and will be available on PyPI soon. In the meantime, you can use our REST API directly.

## Installation

```bash
# Coming soon
pip install sovant
```

For async support:

```bash
# Coming soon
pip install sovant[async]
```

## Quick Start

```python
from sovant import SovantClient

# Initialize the client
client = SovantClient(api_key="YOUR_API_KEY")

# Create a memory
memory = client.memories.create({
    "content": "User prefers Python for data science projects",
    "type": "preference",
    "metadata": {
        "confidence": 0.95,
        "context": "programming_languages"
    }
})

print(f"Created memory: {memory.id}")

# Search memories
results = client.memories.search({
    "query": "What programming languages does the user prefer?",
    "limit": 5
})

for result in results:
    print(f"- {result.content} (relevance: {result.relevance_score:.2f})")
```

## Features

- 🐍 **Full Type Hints** - Complete type annotations for better IDE support
- 🔄 **Async/Await Support** - Built for modern Python applications
- 🔁 **Automatic Retries** - Configurable retry logic with exponential backoff
- 📦 **Batch Operations** - Efficient bulk create/delete operations
- 🎯 **Smart Search** - Semantic, keyword, and hybrid search modes
- 🧵 **Thread Management** - Organize memories into contextual threads
- 📊 **Analytics** - Built-in insights and statistics
- 🛡️ **Comprehensive Error Handling** - Typed exceptions for all error cases

## Configuration

```python
from sovant import SovantClient, Config

# Using configuration object
config = Config(
    api_key="YOUR_API_KEY",
    base_url="https://api.sovant.ai/v1",  # Optional
    timeout=30,  # Request timeout in seconds
    max_retries=3,  # Number of retries for failed requests
    retry_delay=1.0  # Initial delay between retries
)

client = SovantClient(config)
```

You can also use environment variables:

```bash
export SOVANT_API_KEY="YOUR_API_KEY"
```

```python
from sovant import SovantClient

# Automatically reads from SOVANT_API_KEY env var
client = SovantClient()
```

## Memory Operations

### Create a Memory

```python
from sovant import MemoryType, EmotionType

memory = client.memories.create({
    "content": "User completed the onboarding tutorial",
    "type": MemoryType.EVENT,
    "importance": 0.8,
    "metadata": {
        "step_completed": "tutorial",
        "duration_seconds": 180
    },
    "tags": ["onboarding", "milestone"],
    "emotion": {
        "type": EmotionType.POSITIVE,
        "intensity": 0.7
    },
    "action_items": ["Send welcome email", "Unlock advanced features"]
})
```

### Update a Memory

```python
updated = client.memories.update(memory.id, {
    "importance": 0.9,
    "follow_up_required": True,
    "follow_up_due": "2024-12-31T23:59:59Z"
})
```

### Search Memories

```python
# Semantic search
semantic_results = client.memories.search({
    "query": "user achievements and milestones",
    "search_type": "semantic",
    "limit": 10
})

# Filtered search
from sovant import MemoryType

filtered_results = client.memories.search({
    "query": "preferences",
    "type": [MemoryType.PREFERENCE, MemoryType.DECISION],
    "tags": ["important"],
    "created_after": "2024-01-01",
    "sort_by": "importance",
    "sort_order": "desc"
})
```

### Batch Operations

```python
# Batch create
memories_data = [
    {"content": "User is a data scientist", "type": "observation"},
    {"content": "User works with ML models", "type": "learning"},
    {"content": "User prefers Jupyter notebooks", "type": "preference"}
]

batch_result = client.memories.create_batch(memories_data)
print(f"Created {batch_result.success_count} memories")
print(f"Failed {batch_result.failed_count} memories")

# Batch delete
result = client.memories.delete_batch(["mem_123", "mem_456", "mem_789"])
print(f"Deleted {result['deleted']} memories")
```

## Thread Management

### Create a Thread

```python
thread = client.threads.create({
    "name": "Customer Support Chat",
    "description": "Tracking customer issues and resolutions",
    "tags": ["support", "customer", "priority"]
})
```

### Add Memories to Thread

```python
# Add existing memories
client.threads.add_memories(thread.id, [memory1.id, memory2.id])

# Create and add in one operation
new_memory = client.memories.create({
    "content": "Customer reported login issue",
    "type": "conversation",
    "thread_ids": [thread.id]
})
```

### Get Thread with Memories

```python
# Get thread with all memories included
thread_with_memories = client.threads.get(thread.id, include_memories=True)

print(f"Thread: {thread_with_memories.name}")
print(f"Total memories: {len(thread_with_memories.memories)}")

for memory in thread_with_memories.memories:
    print(f"- {memory.content}")
```

### Thread Analytics

```python
stats = client.threads.get_stats(thread.id)

print(f"Total memories: {stats.memory_count}")
print(f"Average importance: {stats.avg_importance:.2f}")
print(f"Decisions made: {stats.total_decisions}")
print(f"Open questions: {stats.total_questions}")
print(f"Action items: {stats.total_action_items}")
```

## Async Support

```python
import asyncio
from sovant import AsyncSovantClient

async def main():
    # Use async client for better performance
    async with AsyncSovantClient(api_key="YOUR_API_KEY") as client:
        # Create multiple memories concurrently
        memories = await asyncio.gather(
            client.memories.create({"content": "Memory 1"}),
            client.memories.create({"content": "Memory 2"}),
            client.memories.create({"content": "Memory 3"})
        )

        print(f"Created {len(memories)} memories")

        # Async search
        results = await client.memories.search({
            "query": "user preferences",
            "search_type": "semantic"
        })

        for result in results:
            print(f"- {result.content}")

asyncio.run(main())
```

## Error Handling

The SDK provides typed exceptions for different error scenarios:

```python
from sovant import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    NetworkError
)

try:
    memory = client.memories.get("invalid_id")
except NotFoundError:
    print("Memory not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Validation errors: {e.errors}")
except AuthenticationError:
    print("Invalid API key")
except NetworkError:
    print("Network error occurred")
```

## Advanced Usage

### Memory Insights

```python
insights = client.memories.get_insights(
    time_range="last_30_days",
    group_by="type"
)

print(f"Total memories: {insights['total_count']}")
print(f"Type distribution: {insights['type_distribution']}")
print(f"Emotion distribution: {insights['emotion_distribution']}")
print(f"Average importance: {insights['importance_stats']['avg']}")
print(f"Growth rate: {insights['growth_rate']}%")
```

### Related Memories

```python
# Find memories related to a specific memory
related = client.memories.get_related(
    memory_id=memory.id,
    limit=5,
    threshold=0.7  # Minimum similarity score
)

for r in related:
    print(f"- {r.content} (similarity: {r.relevance_score:.2f})")
```

### Thread Operations

```python
# Archive a thread
archived = client.threads.archive(thread.id)

# Search threads
threads = client.threads.search(
    query="customer support",
    status="active",
    tags=["priority"]
)

# Merge threads
merged = client.threads.merge(
    target_id=main_thread.id,
    source_ids=[thread2.id, thread3.id]
)

# Clone a thread
cloned = client.threads.clone(
    thread_id=thread.id,
    name="Cloned Thread",
    include_memories=True
)
```

### Pagination

```python
# List memories with pagination
page1 = client.memories.list(limit=20, offset=0)
print(f"Total memories: {page1.total}")
print(f"Has more: {page1.has_more}")

# Get next page
if page1.has_more:
    page2 = client.memories.list(limit=20, offset=20)
```

## Type Safety

The SDK uses Pydantic for data validation and provides enums for better type safety:

```python
from sovant import MemoryType, EmotionType, ThreadStatus

# Using enums ensures valid values
memory = client.memories.create({
    "content": "Important decision made",
    "type": MemoryType.DECISION,  # Type-safe enum
    "emotion": {
        "type": EmotionType.NEUTRAL,  # Type-safe enum
        "intensity": 0.5
    }
})

# IDE will provide autocompletion for all fields
thread = client.threads.create({
    "name": "Project Planning",
    "status": ThreadStatus.ACTIVE  # Type-safe enum
})
```

## Best Practices

1. **Use batch operations for bulk actions**

   ```python
   # Good - single API call
   batch_result = client.memories.create_batch(memories_list)

   # Avoid - multiple API calls
   for memory_data in memories_list:
       client.memories.create(memory_data)
   ```

2. **Use async client for concurrent operations**

   ```python
   async with AsyncSovantClient() as client:
       results = await asyncio.gather(*tasks)
   ```

3. **Handle errors gracefully**

   ```python
   try:
       result = client.memories.search({"query": "test"})
   except RateLimitError as e:
       await asyncio.sleep(e.retry_after)
       # Retry the request
   ```

4. **Use type hints for better IDE support**

   ```python
   from sovant import Memory, SearchResult

   def process_memory(memory: Memory) -> None:
       print(f"Processing {memory.id}")

   def handle_results(results: list[SearchResult]) -> None:
       for result in results:
           print(f"Score: {result.relevance_score}")
   ```

## Examples

Check out the [examples directory](https://github.com/sovant-ai/python-sdk/tree/main/examples) for complete working examples:

- Basic CRUD operations
- Advanced search techniques
- Thread management workflows
- Async patterns
- Error handling
- Data analysis with pandas integration

## Support

- 📚 [Documentation](https://docs.sovant.ai)
- 💬 [Discord Community](https://discord.gg/sovant)
- 🐛 [Issue Tracker](https://github.com/sovant-ai/python-sdk/issues)
- 📧 [Email Support](mailto:support@sovant.ai)

## License

MIT © Sovant AI
