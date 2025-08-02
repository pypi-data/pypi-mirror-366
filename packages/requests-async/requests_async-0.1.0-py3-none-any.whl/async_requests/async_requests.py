
from loguru import logger
from typing import Optional, Dict, Any, Union, List
import httpx
from httpx import Response
import asyncio
import atexit
from contextlib import asynccontextmanager


class AsyncRequestError(Exception):
    """异步请求异常"""
    pass


class AsyncRequests:
    def __init__(self, timeout: float = 10.0, max_retries: int = 3, 
                 default_headers: Optional[Dict[str, str]] = None):
        """
        初始化异步请求客户端
        :param timeout: 默认超时时间（秒）
        :param max_retries: 最大重试次数
        :param default_headers: 默认请求头
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
        self._default_headers: Dict[str, str] = default_headers.copy() if default_headers else {}
        self._is_global_instance = False

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    def _mark_as_global(self):
        """标记为全局实例"""
        self._is_global_instance = True

    async def _ensure_client(self):
        """确保客户端已初始化"""
        if self._client is None or self._client.is_closed:
            client_headers = self._default_headers.copy() if self._default_headers else {}
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers=client_headers
            )

    async def close(self):
        """关闭客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        判断是否应该重试
        :param exception: 异常实例
        :param attempt: 当前尝试次数（从1开始）
        :return: 是否应该重试
        """
        if attempt >= self.max_retries:
            return False
        # 网络相关错误应该重试
        if isinstance(exception, (httpx.NetworkError, httpx.TimeoutException)):
            return True
        # HTTP状态码错误，只对特定状态码重试
        if isinstance(exception, httpx.HTTPStatusError):
            # 5xx服务器错误和429限流错误可以重试
            return exception.response.status_code >= 500 or exception.response.status_code == 429
        return False

    async def _make_request(self, method: str, url: str, **kwargs) -> Response:
        """
        执行请求的核心方法
        :param method: HTTP方法
        :param url: 请求URL
        :param kwargs: 请求参数
        :return: 响应对象
        """
        await self._ensure_client()
        
        # 提取自定义参数
        proxies = kwargs.pop('proxies', None)
        cookies = kwargs.pop('cookies', None)
        allow_redirects = kwargs.pop('allow_redirects', True)
        verify = kwargs.pop('verify', True)
        timeout = kwargs.pop('timeout', self.timeout)
        
        # 安全地合并默认头部和自定义头部
        headers = kwargs.get('headers') or {}
        if self._default_headers:
            merged_headers = self._default_headers.copy()
            if headers:
                merged_headers.update(headers)
            kwargs['headers'] = merged_headers
        elif headers:
            kwargs['headers'] = headers
        
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # 为每次尝试创建独立的客户端配置
                if proxies or cookies:
                    # 如果有代理或cookies，使用临时客户端
                    client_kwargs = {
                        'follow_redirects': allow_redirects,
                        'verify': verify,
                        'timeout': httpx.Timeout(timeout)
                    }
                    
                    if proxies:
                        client_kwargs['proxies'] = proxies
                    
                    async with httpx.AsyncClient(**client_kwargs) as temp_client:
                        if cookies:
                            # 安全地处理cookies
                            if isinstance(cookies, dict):
                                temp_client.cookies.update(cookies)
                        response = await temp_client.request(method, url, **kwargs)
                else:
                    # 使用复用的客户端
                    response = await self._client.request(method, url, timeout=timeout, **kwargs)
                
                # 检查HTTP状态码
                response.raise_for_status()
                return response
                
            except Exception as e:
                last_exception = e
                if self._should_retry(e, attempt):
                    logger.warning(f"{method} 请求失败 {url}，正在进行第 {attempt} 次重试: {str(e)}")
                    # 重试前等待一段时间（指数退避）
                    await asyncio.sleep(0.5 * (2 ** (attempt - 1)))
                else:
                    logger.error(f"{method} 请求失败 {url}，不再重试: {str(e)}")
                    break
        
        # 如果到这里说明所有重试都失败了
        raise AsyncRequestError(f"请求失败，已达到最大重试次数 {self.max_retries}") from last_exception

    async def get(self, url: str, params=None, headers=None, cookies=None, 
                  proxies=None, allow_redirects=True, **kwargs) -> Response:
        """
        异步 GET 请求
        """
        return await self._make_request(
            'GET', url, 
            params=params, 
            headers=headers, 
            cookies=cookies,
            proxies=proxies,
            allow_redirects=allow_redirects,
            **kwargs
        )

    async def post(self, url: str, params=None, data=None, json=None, headers=None, 
                   cookies=None, proxies=None, allow_redirects=True, 
                   verify=True, **kwargs) -> Response:
        """
        异步 POST 请求
        """
        return await self._make_request(
            'POST', url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            proxies=proxies,
            allow_redirects=allow_redirects,
            verify=verify,
            **kwargs
        )

    async def put(self, url: str, params=None, data=None, json=None, headers=None,
                  cookies=None, proxies=None, allow_redirects=True,
                  verify=True, **kwargs) -> Response:
        """
        异步 PUT 请求
        """
        return await self._make_request(
            'PUT', url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            proxies=proxies,
            allow_redirects=allow_redirects,
            verify=verify,
            **kwargs
        )

    async def delete(self, url: str, params=None, headers=None,
                     cookies=None, proxies=None, allow_redirects=True,
                     verify=True, **kwargs) -> Response:
        """
        异步 DELETE 请求
        """
        return await self._make_request(
            'DELETE', url,
            params=params,
            headers=headers,
            cookies=cookies,
            proxies=proxies,
            allow_redirects=allow_redirects,
            verify=verify,
            **kwargs
        )

    async def patch(self, url: str, params=None, data=None, json=None, headers=None,
                    cookies=None, proxies=None, allow_redirects=True,
                    verify=True, **kwargs) -> Response:
        """
        异步 PATCH 请求
        """
        return await self._make_request(
            'PATCH', url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            proxies=proxies,
            allow_redirects=allow_redirects,
            verify=verify,
            **kwargs
        )

    async def head(self, url: str, params=None, headers=None,
                   cookies=None, proxies=None, allow_redirects=True,
                   verify=True, **kwargs) -> Response:
        """
        异步 HEAD 请求
        """
        return await self._make_request(
            'HEAD', url,
            params=params,
            headers=headers,
            cookies=cookies,
            proxies=proxies,
            allow_redirects=allow_redirects,
            verify=verify,
            **kwargs
        )

    async def options(self, url: str, params=None, headers=None,
                      cookies=None, proxies=None, allow_redirects=True,
                      verify=True, **kwargs) -> Response:
        """
        异步 OPTIONS 请求
        """
        return await self._make_request(
            'OPTIONS', url,
            params=params,
            headers=headers,
            cookies=cookies,
            proxies=proxies,
            allow_redirects=allow_redirects,
            verify=verify,
            **kwargs
        )

    # 便利方法
    async def get_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        GET请求并返回JSON数据
        """
        response = await self.get(url, **kwargs)
        return response.json()

    async def post_json(self, url: str, json_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        POST JSON数据并返回JSON响应
        """
        response = await self.post(url, json=json_data, **kwargs)
        return response.json()

    async def download_file(self, url: str, file_path: str, chunk_size: int = 8192, **kwargs):
        """
        下载文件
        :param url: 文件URL
        :param file_path: 保存路径
        :param chunk_size: 分块大小
        :param kwargs: 其他请求参数
        """
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', url, **kwargs) as response:
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size):
                        f.write(chunk)
        logger.info(f"文件已下载: {file_path}")

    def set_default_headers(self, headers: Dict[str, str]):
        """
        设置默认请求头
        """
        if headers and isinstance(headers, dict):
            self._default_headers.update(headers)

    def clear_default_headers(self):
        """
        清空默认请求头
        """
        self._default_headers.clear()

    async def batch_get(self, urls: List[str], **kwargs) -> List[Response]:
        """
        批量GET请求
        :param urls: URL列表
        :param kwargs: 其他请求参数
        :return: 响应列表
        """
        tasks = [self.get(url, **kwargs) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)


# 简化全局实例管理器
class _GlobalAsyncRequests(AsyncRequests):
    """全局异步请求实例管理器 - 简化版本"""
    
    def __init__(self):
        super().__init__()
        self._mark_as_global()


# 全局实例
_global_manager = _GlobalAsyncRequests()

# 创建便利的全局接口
async def get(url: str, **kwargs) -> Response:
    """全局GET请求"""
    return await _global_manager.get(url, **kwargs)

async def post(url: str, **kwargs) -> Response:
    """全局POST请求"""
    return await _global_manager.post(url, **kwargs)

async def put(url: str, **kwargs) -> Response:
    """全局PUT请求"""
    return await _global_manager.put(url, **kwargs)

async def delete(url: str, **kwargs) -> Response:
    """全局DELETE请求"""
    return await _global_manager.delete(url, **kwargs)

async def patch(url: str, **kwargs) -> Response:
    """全局PATCH请求"""
    return await _global_manager.patch(url, **kwargs)

async def head(url: str, **kwargs) -> Response:
    """全局HEAD请求"""
    return await _global_manager.head(url, **kwargs)

async def options(url: str, **kwargs) -> Response:
    """全局OPTIONS请求"""
    return await _global_manager.options(url, **kwargs)

async def get_json(url: str, **kwargs) -> Dict[str, Any]:
    """全局GET JSON请求"""
    return await _global_manager.get_json(url, **kwargs)

async def post_json(url: str, json_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """全局POST JSON请求"""
    return await _global_manager.post_json(url, json_data, **kwargs)

async def download_file(url: str, file_path: str, **kwargs):
    """全局文件下载"""
    return await _global_manager.download_file(url, file_path, **kwargs)

async def batch_get(urls: List[str], **kwargs) -> List[Response]:
    """全局批量GET请求"""
    return await _global_manager.batch_get(urls, **kwargs)

@asynccontextmanager
async def session(**kwargs):
    """
    创建一个会话上下文管理器
    使用示例:
        async with session(timeout=30) as s:
            response = await s.get('https://example.com')
    """
    client = AsyncRequests(**kwargs)
    try:
        yield client
    finally:
        await client.close()

# 程序退出时清理资源
def _cleanup_on_exit():
    """程序退出时的清理函数"""
    try:
        loop = asyncio.get_running_loop()
        if loop and not loop.is_closed():
            loop.create_task(_global_manager.close())
    except RuntimeError:
        # 如果没有运行的事件循环，创建一个新的来清理
        try:
            asyncio.run(_global_manager.close())
        except:
            pass

atexit.register(_cleanup_on_exit)

# 为了保持向后兼容性，保留原来的全局实例
async_requests = _global_manager
