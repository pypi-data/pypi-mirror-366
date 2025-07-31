# Overspeed

A Multi Port, Multi Process, Multi Coroutine, High Concurrency Project That Integrates Http, Websocket, System Resource Monitoring, And Detailed Logging.

## Installation

```bash
pip install Overspeed

import Overspeed;

参数注释 Overspeed.Explain();
项目运行 Overspeed.Lunch();
```

## Pressure Measurement
```
Overspeed

Running 10s test @ http://127.0.0.1:1007/
	1000 threads and 1000 connections
		Thread Stats   Avg      Stdev     Max   +/- Stdev
			Latency   169.32ms  343.33ms   1.94s    88.87%
			Req/Sec    16.79     20.98   101.00     85.86%
	28427 requests in 10.11s, 2.47MB read
	Socket errors: connect 0, read 389, write 0, timeout 579
	Requests/sec:   2813.09
	Transfer/sec:    249.99KB

Flask
gunicorn -w 4 -b 0.0.0.0:8000 flask_app:app

Running 10s test @ http://127.0.0.1:1007/
	1000 threads and 1000 connections
		Thread Stats   Avg      Stdev     Max   +/- Stdev
			Latency   121.17ms  238.08ms   1.74s    92.53%
			Req/Sec     8.74     10.40    50.00     82.00%
	10115 requests in 10.10s, 1.53MB read
	Socket errors: connect 0, read 0, write 0, timeout 55
	Requests/sec:   1001.24
	Transfer/sec:    154.63KB

FastAPI
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4

Running 10s test @ http://127.0.0.1:1007/
	1000 threads and 1000 connections
		Thread Stats   Avg      Stdev     Max   +/- Stdev
			Latency   156.08ms  338.01ms   1.90s    91.46%
			Req/Sec    16.06     19.90   111.00     87.27%
	23774 requests in 10.10s, 2.97MB read
	Socket errors: connect 0, read 397, write 0, timeout 484
	Requests/sec:   2353.04
	Transfer/sec:    301.02KB


Django
gunicorn -w 4 -b 0.0.0.0:8000 myproject.wsgi

Running 10s test @ http://127.0.0.1:1007/
	1000 threads and 1000 connections
		Thread Stats   Avg      Stdev     Max   +/- Stdev
			Latency   153.89ms  270.51ms   1.80s    90.15%
			Req/Sec     7.15      8.87    50.00     86.46%
	7840 requests in 10.10s, 2.23MB read
	Socket errors: connect 0, read 0, write 0, timeout 92
	Requests/sec:    776.04
	Transfer/sec:    225.79KB
```

## Parameter Explain
```
########################################################################################################################
================================================================================
主参数[Black] | 注释[黑名单配置]
----------------------------------------
二级参数[Status] | 默认值[False] | 注释[黑名单开关]
二级参数[Callable] | 默认值[None] | 注释[回调函数]
================================================================================
主参数[Cache] | 注释[缓存配置]
----------------------------------------
二级参数[Status] | 默认值[False] | 注释[缓存开关]
二级参数[Callable] | 默认值[None] | 注释[回调函数]
================================================================================
主参数[Http] | 注释[HTTP配置]
----------------------------------------
二级参数[Status] | 默认值[True] | 注释[服务开关]
二级参数[Journal] | 默认值[True] | 注释[日志开关]
二级参数[Cpu] | 默认值[自动获取服务器CPU数量] | 注释[核心数]
二级参数[Port] | 默认值[[31100]] | 注释[端口]
二级参数[Large] | 默认值[2097152] | 注释[请求体容量]
二级参数[Certfile] | 默认值[] | 注释[SSL CERT 文件路径]
二级参数[Keyfile] | 默认值[] | 注释[SSL KEY 文件路径]
二级参数[Callable] | 默认值[None] | 注释[回调函数]
================================================================================
主参数[Idempotent] | 注释[幂等配置]
----------------------------------------
二级参数[Status] | 默认值[False] | 注释[幂等开关]
二级参数[Callable] | 默认值[None] | 注释[回调函数]
================================================================================
主参数[Journal] | 注释[日志配置]
----------------------------------------
二级参数[Thread] | 默认值[100] | 注释[线程并发数]
********************
二级参数[Print]
----------------------------------------
三级参数[Http] | 默认值[False] | 注释[HTTP日志打印开关]
三级参数[Websocket] | 默认值[False] | 注释[WEBSOCKET日志打印开关]
三级参数[Resource] | 默认值[False] | 注释[资源监控日志打印开关]
********************
********************
二级参数[Path]
----------------------------------------
三级参数[Trace] | 默认值[/Runtime/Trace/] | 注释[错误信息路径]
三级参数[Http] | 默认值[/Runtime/Http/] | 注释[HTTP信息路径]
三级参数[Websocket] | 默认值[/Runtime/Websocket/] | 注释[WEBSOCKET信息路径]
三级参数[Resource] | 默认值[/Runtime/Resource/] | 注释[资源监控信息路径]
********************
================================================================================
主参数[Limiting] | 注释[限速配置]
----------------------------------------
二级参数[Status] | 默认值[False] | 注释[限速开关]
二级参数[Callable] | 默认值[None] | 注释[回调函数]
================================================================================
主参数[Permission] | 注释[权限配置]
----------------------------------------
二级参数[Status] | 默认值[False] | 注释[权限开关]
二级参数[Callable] | 默认值[None] | 注释[回调函数]
================================================================================
主参数[Proctitle] | 注释[进程名称]
----------------------------------------
二级参数[Main] | 默认值[Overspeed] | 注释[主进程名称]
二级参数[Main_Http] | 默认值[Overspeed.Http] | 注释[HTTP主进程名称]
二级参数[Main_Http_Server] | 默认值[Overspeed.Http.Server] | 注释[HTTP服务进程名称]
二级参数[Main_Http_Worker] | 默认值[Overspeed.Http.Worker] | 注释[HTTP工作进程名称]
二级参数[Main_Websocket] | 默认值[Overspeed.Websocket] | 注释[WEBSOCKET主进程名称]
二级参数[Main_Websocket_Server] | 默认值[Overspeed.Websocket.Server] | 注释[WEBSOCKET服务进程名称]
二级参数[Main_Websocket_Worker] | 默认值[Overspeed.Websocket.Worker] | 注释[WEBSOCKET工作进程名称]
二级参数[Main_Journal] | 默认值[Overspeed.Journal] | 注释[日志进程名称]
二级参数[Main_Resource] | 默认值[Overspeed.Resource] | 注释[资源监控进程名称]
================================================================================
主参数[Resource] | 注释[资源监控配置]
----------------------------------------
二级参数[Status] | 默认值[True] | 注释[服务开关]
二级参数[Sleep] | 默认值[30] | 注释[监控间隔时间]
二级参数[Journal] | 默认值[True] | 注释[日志开关]
二级参数[Cpu] | 默认值[True] | 注释[核心监控开关]
二级参数[Memory] | 默认值[True] | 注释[内存监控开关]
二级参数[Network] | 默认值[True] | 注释[网络监控开关]
二级参数[Disk] | 默认值[True] | 注释[磁盘监控开关]
二级参数[File] | 默认值[True] | 注释[文件监控开关]
二级参数[Load] | 默认值[True] | 注释[负载监控开关]
================================================================================
主参数[Websocket] | 注释[WEBSOCKET配置]
----------------------------------------
二级参数[Status] | 默认值[True] | 注释[服务开关]
二级参数[Journal] | 默认值[True] | 注释[日志开关]
二级参数[Cpu] | 默认值[自动获取服务器CPU数量] | 注释[核心数]
二级参数[Port] | 默认值[[32100]] | 注释[端口]
二级参数[Certfile] | 默认值[] | 注释[SSL CERT 文件路径]
二级参数[Keyfile] | 默认值[] | 注释[SSL KEY 文件路径]
二级参数[Callable] | 默认值[None] | 注释[回调函数]
二级参数[Connect] | 默认值[60] | 注释[最长链接时间，当为0时不自动断开]
二级参数[Timeout] | 默认值[5] | 注释[最长请求间隔，当为0时不自动断开]
================================================================================
########################################################################################################################
```