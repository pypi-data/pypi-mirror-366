# requests-async

一个基于httpx的异步HTTP请求库，提供简单易用的接口和自动重试机制。

## 功能特性

- 支持所有HTTP方法(GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- 自动重试机制
- 全局实例和函数接口
- 会话管理
- JSON便利方法
- 批量请求支持
- 文件下载功能
- 自定义客户端配置

## 安装

```bash
pip install requests-async
```

## 快速开始

### 基本使用

```python
from requests_async import requests_async, get

async def main():
    # 使用全局实例
    response = await requests_async.get("https://httpbin.org/get")
    print(response.json())
    
    # 使用全局函数
    response = await get("https://httpbin.org/get")
    print(response.status_code)

asyncio.run(main())
```

### 不同HTTP方法

```python
from requests_async import get, post, put, delete

async def example():
    # GET请求
    response = await get("https://httpbin.org/get")
    
    # POST请求
    response = await post("https://httpbin.org/post", json={"key": "value"})
    
    # PUT请求
    response = await put("https://httpbin.org/put", json={"key": "value"})
    
    # DELETE请求
    response = await delete("https://httpbin.org/delete")
```

### JSON便利方法

```python
from requests_async import get_json, post_json

async def example():
    # 直接获取JSON数据
    data = await get_json("https://httpbin.org/json")
    
    # POST JSON数据并获取JSON响应
    response = await post_json("https://httpbin.org/post", {"name": "测试"})
```

### 会话使用

```python
from requests_async import session

async def example():
    async with session(timeout=15) as s:
        response1 = await s.get("https://httpbin.org/get")
        response2 = await s.post("https://httpbin.org/post", json={"test": "data"})
```

### 批量请求

```python
from requests_async import batch_get

async def example():
    urls = [
        "https://httpbin.org/get?id=1",
        "https://httpbin.org/get?id=2",
        "https://httpbin.org/get?id=3"
    ]
    
    responses = await batch_get(urls)
    for response in responses:
        print(response.status_code)
```

### 自定义客户端

```python
from requests_async import AsyncRequests

async def example():
    client = AsyncRequests(
        timeout=20.0,
        max_retries=5,
        default_headers={"Custom-Header": "Value"}
    )
    
    async with client:
        response = await client.get("https://httpbin.org/headers")
        print(response.json())
```

## 高级配置

### 重试机制

```python
from requests_async import AsyncRequests

# 自定义重试次数和超时
client = AsyncRequests(
    timeout=30.0,
    max_retries=3
)
```

### 错误处理

```python
from requests_async import AsyncRequestError

try:
    response = await get("https://httpbin.org/status/500")
except AsyncRequestError as e:
    print(f"请求失败: {e}")
```

## 贡献

欢迎提交问题和拉取请求！

## 许可证

MIT
