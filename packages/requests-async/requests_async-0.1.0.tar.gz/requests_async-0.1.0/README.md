
# AsyncRequests

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

一个基于 `httpx` 的现代异步HTTP客户端库，提供简洁易用的API和强大的功能。

## ✨ 特性

- 🚀 **现代异步**: 基于 Python asyncio 和 httpx
- 🔄 **自动重试**: 智能重试机制，支持指数退避
- 🎯 **多种使用方式**: 全局函数、实例方法、会话管理
- 📦 **批量请求**: 高效的并发请求处理
- 🛡️ **错误处理**: 完善的异常处理和日志记录
- 🔧 **高度可配置**: 超时、重试、代理、SSL等全面支持
- 📝 **类型提示**: 完整的类型注解支持

## 📦 安装

```bash
pip install httpx loguru
```

然后将 `async_requests.py` 添加到你的项目中。

## 🚀 快速开始

### 基本使用

```python
import asyncio
from async_requests import get, post, async_requests

async def main():
    # 方式1: 使用全局函数
    response = await get('https://api.github.com/users/octocat')
    print(response.json())
    
    # 方式2: 使用全局实例
    response = await async_requests.get('https://httpbin.org/get')
    print(f'状态码: {response.status_code}')

asyncio.run(main())
```

### JSON 便利方法

```python
import asyncio
from async_requests import get_json, post_json

async def main():
    # 直接获取JSON数据
    data = await get_json('https://api.github.com/users/octocat')
    print(f"用户名: {data['login']}")
    
    # POST JSON数据
    response_data = await post_json(
        'https://httpbin.org/post',
        {'name': '张三', 'age': 25}
    )
    print(response_data)

asyncio.run(main())
```

### 会话管理

```python
import asyncio
from async_requests import session

async def main():
    async with session(timeout=30) as s:
        # 设置认证头部
        s.set_default_headers({
            'Authorization': 'Bearer your-token',
            'User-Agent': 'MyApp/1.0'
        })
        
        # 在会话中进行多个请求
        user = await s.get_json('https://api.github.com/user')
        repos = await s.get_json('https://api.github.com/user/repos')
        
        print(f"用户: {user['login']}, 仓库数: {len(repos)}")

asyncio.run(main())
```

### 批量请求

```python
import asyncio
from async_requests import batch_get

async def main():
    urls = [
        'https://api.github.com/users/torvalds',
        'https://api.github.com/users/gvanrossum',
        'https://api.github.com/users/octocat'
    ]
    
    responses = await batch_get(urls)
    
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            print(f"请求 {i+1} 失败: {response}")
        else:
            data = response.json()
            print(f"用户: {data['login']}, 粉丝: {data['followers']}")

asyncio.run(main())
```

## 📚 详细文档

### 支持的HTTP方法

| 方法 | 全局函数 | 实例方法 | 说明 |
|------|----------|----------|------|
| GET | `get()` | `client.get()` | 获取资源 |
| POST | `post()` | `client.post()` | 创建资源 |
| PUT | `put()` | `client.put()` | 更新资源 |
| DELETE | `delete()` | `client.delete()` | 删除资源 |
| PATCH | `patch()` | `client.patch()` | 部分更新 |
| HEAD | `head()` | `client.head()` | 获取头部 |
| OPTIONS | `options()` | `client.options()` | 获取选项 |

### 便利方法

```python
# JSON方法
data = await get_json(url)  # GET并返回JSON
data = await post_json(url, json_data)  # POST JSON并返回JSON

# 文件下载
await download_file(url, 'local_file.zip')

# 批量请求
responses = await batch_get([url1, url2, url3])
```

### 自定义客户端

```python
from async_requests import AsyncRequests

# 创建自定义配置的客户端
client = AsyncRequests(
    timeout=30.0,
    max_retries=5,
    default_headers={'User-Agent': 'MyApp/1.0'}
)

async with client:
    response = await client.get('https://api.example.com')
```

### 高级功能

#### 代理支持

```python
proxies = {
    'http://': 'http://proxy.example.com:8080',
    'https://': 'https://proxy.example.com:8080'
}

response = await get(url, proxies=proxies)
```

#### 自定义超时

```python
# 单次请求超时
response = await get(url, timeout=10)

# 客户端默认超时
client = AsyncRequests(timeout=15)
```

#### SSL验证控制

```python
# 跳过SSL验证（不推荐在生产环境使用）
response = await get(url, verify=False)
```

#### Cookie处理

```python
cookies = {'session_id': 'abc123'}
response = await get(url, cookies=cookies)
```

## ⚙️ 配置选项

### AsyncRequests 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout` | `float` | `10.0` | 请求超时时间（秒） |
| `max_retries` | `int` | `3` | 最大重试次数 |
| `default_headers` | `Dict[str, str]` | `None` | 默认请求头 |

### 重试机制

库会自动重试以下类型的错误：
- 网络连接错误
- 超时错误
- 5xx 服务器错误
- 429 限流错误

重试采用指数退避策略，重试间隔为：0.5s, 1s, 2s, 4s...

## 🔧 错误处理

```python
from async_requests import AsyncRequestError

try:
    response = await get('https://invalid-url.example.com')
except AsyncRequestError as e:
    print(f"请求失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 📊 性能优化建议

1. **使用会话**: 对于多个请求，使用 `session()` 可以复用连接
2. **批量请求**: 使用 `batch_get()` 进行并发请求
3. **合理设置超时**: 根据API响应时间调整超时设置
4. **控制并发数**: 避免同时发起过多请求

## 🤝 使用示例

### API客户端示例

```python
import asyncio
from async_requests import session

class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://api.github.com'
    
    async def get_user(self, username: str):
        async with session() as s:
            s.set_default_headers({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })
            
            user = await s.get_json(f'{self.base_url}/users/{username}')
            return user

async def main():
    github = GitHubAPI('your-token')
    user = await github.get_user('octocat')
    print(f"用户: {user['login']}, 公司: {user.get('company', 'N/A')}")

asyncio.run(main())
```

### 爬虫示例

```python
import asyncio
from async_requests import batch_get

async def crawl_urls(urls):
    """批量爬取URL"""
    responses = await batch_get(urls, timeout=10)
    
    results = []
    for url, response in zip(urls, responses):
        if isinstance(response, Exception):
            results.append({'url': url, 'error': str(response)})
        else:
            results.append({
                'url': url,
                'status': response.status_code,
                'size': len(response.content)
            })
    
    return results

async def main():
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
        'https://httpbin.org/status/200',
        'https://httpbin.org/status/404'
    ]
    
    results = await crawl_urls(urls)
    for result in results:
        print(result)

asyncio.run(main())
```

## 🧪 测试

运行测试脚本：

```bash
python test.py
```

## 🐛 问题报告

如果遇到问题，请在 [GitHub Issues](https://github.com/taisuii/async-requests/issues) 中报告。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [httpx](https://www.python-httpx.org/) - 现代HTTP客户端库
- [loguru](https://github.com/Delgan/loguru) - 简化的日志记录

## 📈 更新日志

### v1.0.0 (2025-08-02)
- ✨ 初始版本发布
- 🚀 支持所有HTTP方法
- 🔄 自动重试机制
- 📦 批量请求支持
- 🛡️ 完善的错误处理
