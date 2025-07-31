from .Scheduler import Lunch;

def Explain() :
    from .Common import Config , Function;
    Objective = dict(
        Proctitle = dict(
            Comment = '进程名称' ,
            Field = dict(
                Main = '主进程名称' ,
                Main_Http = 'HTTP主进程名称' ,
                Main_Http_Server = 'HTTP服务进程名称' ,
                Main_Http_Worker = 'HTTP工作进程名称' ,
                Main_Websocket = 'WEBSOCKET主进程名称' ,
                Main_Websocket_Server = 'WEBSOCKET服务进程名称' ,
                Main_Websocket_Worker = 'WEBSOCKET工作进程名称' ,
                Main_Journal = '日志进程名称' ,
                Main_Resource = '资源监控进程名称' ,
            ) ,
        ) ,
        Http = dict(
            Comment = 'HTTP配置' ,
            Field = dict(
                Status = '服务开关' ,
                Journal = '日志开关' ,
                Cpu = '核心数' ,
                Port = '端口' ,
                Large = '请求体容量' ,
                Certfile = 'SSL CERT 文件路径' ,
                Keyfile = 'SSL KEY 文件路径' ,
                Callable = '回调函数' ,
            ) ,
        ) ,
        Websocket = dict(
            Comment = 'WEBSOCKET配置' ,
            Field = dict(
                Status = '服务开关' ,
                Journal = '日志开关' ,
                Cpu = '核心数' ,
                Port = '端口' ,
                Certfile = 'SSL CERT 文件路径' ,
                Keyfile = 'SSL KEY 文件路径' ,
                Callable = '回调函数' ,
                Connect = '最长链接时间，当为0时不自动断开' ,
                Timeout = '最长请求间隔，当为0时不自动断开' ,
            ) ,
        ) ,
        Resource = dict(
            Comment = '资源监控配置' ,
            Field = dict(
                Status = '服务开关' ,
                Sleep = '监控间隔时间' ,
                Journal = '日志开关' ,
                Cpu = '核心监控开关' ,
                Memory = '内存监控开关' ,
                Network = '网络监控开关' ,
                Disk = '磁盘监控开关' ,
                File = '文件监控开关' ,
                Load = '负载监控开关' ,
            ) ,
        ) ,
        Journal = dict(
            Comment = '日志配置' ,
            Field = dict(
                Print = dict(
                    Http = 'HTTP日志打印开关' ,
                    Websocket = 'WEBSOCKET日志打印开关' ,
                    Resource = '资源监控日志打印开关' ,
                ) ,
                Path = dict(
                    Trace = '错误信息路径' ,
                    Http = 'HTTP信息路径' ,
                    Websocket = 'WEBSOCKET信息路径' ,
                    Resource = '资源监控信息路径' ,
                ) ,
                Thread = '线程并发数' ,
            ) ,
        ) ,
        Black = dict(
            Comment = '黑名单配置' ,
            Field = dict(
                Status = '黑名单开关' ,
                Callable = '回调函数' ,
            ) ,
        ) ,
        Limiting = dict(
            Comment = '限速配置' ,
            Field = dict(
                Status = '限速开关' ,
                Callable = '回调函数' ,
            ) ,
        ) ,
        Permission = dict(
            Comment = '权限配置' ,
            Field = dict(
                Status = '权限开关' ,
                Callable = '回调函数' ,
            ) ,
        ) ,
        Idempotent = dict(
            Comment = '幂等配置' ,
            Field = dict(
                Status = '幂等开关' ,
                Callable = '回调函数' ,
            ) ,
        ) ,
        Cache = dict(
            Comment = '缓存配置' ,
            Field = dict(
                Status = '缓存开关' ,
                Callable = '回调函数' ,
            ) ,
        ) ,
    );
    Source = list();
    for Index in dir(Config) :
        if Index.startswith('__') is True : continue;
        Source.append(' | '.join([
            f'主参数[{Index}]' ,
            f'注释[{Objective.get(Index).get("Comment")}]' ,
        ]));
        Source.append('----' * 10);
        for Key in getattr(Config , Index) :
            if isinstance(getattr(Config , Index).get(Key) , dict) is True :
                Source.append('****' * 5);
                Source.append(' | '.join([
                    f'二级参数[{Key}]' ,
                ]));
                Source.append('----' * 10);
                for X in getattr(Config , Index).get(Key) : Source.append(' | '.join([
                    f'三级参数[{X}]' ,
                    f'默认值[{getattr(Config , Index).get(Key).get(X)}]' ,
                    f'注释[{Objective.get(Index).get("Field").get(Key).get(X)}]' ,
                ]));
                Source.append('****' * 5);
            else : Source.append(' | '.join([
                f'二级参数[{Key}]' ,
                f'默认值[{getattr(Config , Index).get(Key)}]' ,
                f'注释[{Objective.get(Index).get("Field").get(Key)}]' ,
            ]));
        Source.append('====' * 20);
    if not len(Source) == 0 :
        Source.insert(0 , '====' * 20);
        Source.insert(0 , '####' * 30);
        Source.append('####' * 30);
    Function.Log('\n'.join(Source));