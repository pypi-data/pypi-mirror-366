import importlib.metadata

__version__ = importlib.metadata.version("mem0-aliyun-nosql")

from mem0.client.main import AsyncMemoryClient, MemoryClient  # noqa
from mem0.memory.main import AsyncMemory, Memory  # noqa
