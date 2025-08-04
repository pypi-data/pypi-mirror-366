# Python 天翼网盘客户端

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/p189client)
![PyPI - Version](https://img.shields.io/pypi/v/p189client)
![PyPI - Downloads](https://img.shields.io/pypi/dm/p189client)
![PyPI - Format](https://img.shields.io/pypi/format/p189client)
![PyPI - Status](https://img.shields.io/pypi/status/p189client)

## 0. 安装

你可以从 [pypi](https://pypi.org/project/p189client/) 安装最新版本

```console
pip install -U p189client
```

## 1. 导入模块和创建实例

导入模块

```python
from p189client import P189Client, P189APIClient
```

## 2. 接口调用

所有需要直接或间接执行 HTTP 请求的接口，都有同步和异步的调用方式，且默认是采用 GET 发送请求数据

```python
# 同步调用
client.method(payload)
client.method(payload, async_=False)

# 异步调用
await client.method(payload, async_=True)
```

从根本上讲，除了几个 `staticmethod`，它们都会调用 `P189Client.request`

```python
url = "https://cloud.189.cn/api/someapi"
response = client.request(url=url, json={...})
```

当你需要构建自己的扩展模块，以增加一些新的天翼网盘的接口时，就需要用到此方法了

```python
from collections.abc import Coroutine
from typing import overload, Any, Literal

from p189client import P189Client

class MyCustom189Client(P189Client):

    @overload
    def foo(
        self, 
        payload: dict, 
        /, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def foo(
        self, 
        payload: dict, 
        /, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def foo(
        self, 
        payload: dict, 
        /, 
        async_: bool = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        api = "https://cloud.189.cn/api/foo"
        return self.request(
            api, 
            method="GET", 
            params=payload, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def bar(
        self, 
        payload: dict, 
        /, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def bar(
        self, 
        payload: dict, 
        /, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def bar(
        self, 
        payload: dict, 
        /, 
        async_: bool = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        api = "https://cloud.189.cn/api/bar"
        return self.request(
            api, 
            method="POST", 
            data=payload, 
            async_=async_, 
            **request_kwargs, 
        )
```

## 3. 检查响应

接口被调用后，如果返回的是 dict 类型的数据（说明原本是 JSON），则可以用 `p189client.check_response` 执行检查。如果检测为正常，则原样返回数据；否则，抛出一个 `p189client.P189OSError` 的实例。

```python
from p189client import check_response

# 检查同步调用
data = check_response(client.method(payload))
# 检查异步调用
data = check_response(await client.method(payload, async_=True))
```

## 4. 辅助工具

一些简单的封装工具可能是必要的，特别是那种实现起来代码量比较少，可以封装成单个函数的。我把平常使用过程中，积累的一些经验具体化为一组工具函数。这些工具函数分别有着不同的功能，如果组合起来使用，或许能解决很多问题。

```python
from p189client import tool
```

## 5. 学习案例
