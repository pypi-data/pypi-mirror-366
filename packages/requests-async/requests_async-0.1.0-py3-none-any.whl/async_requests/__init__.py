
"""
AsyncRequests - 异步HTTP请求库

一个基于httpx的异步HTTP客户端库，提供简单易用的接口和自动重试机制。

使用方式:
1. 全局实例方式:
   from async_requests import async_requests
   response = await async_requests.get('https://example.com')

2. 全局函数方式:
   from async_requests import get, post
   response = await get('https://example.com')

3. 会话方式:
   from async_requests import session
   async with session() as s:
       response = await s.get('https://example.com')

4. 自定义客户端:
   from async_requests import AsyncRequests
   client = AsyncRequests(timeout=30)
   async with client:
       response = await client.get('https://example.com')
"""

from .async_requests import (
    AsyncRequests,
    AsyncRequestError,
    async_requests,
    get,
    post,
    put,
    delete,
    patch,
    head,
    options,
    get_json,
    post_json,
    download_file,
    batch_get,
    session,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "AsyncRequests",
    "AsyncRequestError", 
    "async_requests",
    "get",
    "post", 
    "put",
    "delete",
    "patch", 
    "head",
    "options",
    "get_json",
    "post_json",
    "download_file",
    "batch_get",
    "session",
]
