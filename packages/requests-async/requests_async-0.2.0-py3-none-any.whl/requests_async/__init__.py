
"""
AsyncRequests - 异步HTTP请求库

一个基于httpx的异步HTTP客户端库，提供简单易用的接口和自动重试机制。

使用方式:
1. 全局实例方式:
   from requests_async import requests_async
   response = await requests_async.get('https://example.com')

2. 全局函数方式:
   from requests_async import get, post
   response = await get('https://example.com')

3. 会话方式:
   from requests_async import session
   async with session() as s:
       response = await s.get('https://example.com')

4. 自定义客户端:
   from requests_async import AsyncRequests
   client = AsyncRequests(timeout=30)
   async with client:
       response = await client.get('https://example.com')
"""

from .requests_async import (
    AsyncRequests,
    AsyncRequestError,
    requests_async,
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

__version__ = "0.2.0"
__author__ = "taisui"
__email__ = "tais00@qq.com"

__all__ = [
    "AsyncRequests",
    "AsyncRequestError", 
    "requests_async",
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
