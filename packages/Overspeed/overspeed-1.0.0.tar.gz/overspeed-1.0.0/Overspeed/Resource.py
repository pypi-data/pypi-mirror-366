from . import Common;

CPU = False;
MEMORY = False;
NETWORK = False;
DISK = False;
FILE = False;
LOAD = False;
JOURNAL = False;
DURATION_PERFORMANCE_CPU = Common.Deque(maxlen = 2);
DURATION_PERFORMANCE_MEMORY = Common.Deque(maxlen = 2);
DURATION_PERFORMANCE_NETWORK = Common.Deque(maxlen = 2);
DURATION_PERFORMANCE_DISK = Common.Deque(maxlen = 2);
DURATION_PERFORMANCE_FILE = Common.Deque(maxlen = 2);
DURATION_PERFORMANCE_LOAD = Common.Deque(maxlen = 2);
DURATION_STATISTICS_CPU = Common.Deque(maxlen = 2);
DURATION_STATISTICS_MEMORY = Common.Deque(maxlen = 2);
DURATION_STATISTICS_NETWORK = Common.Deque(maxlen = 2);
DURATION_STATISTICS_DISK = Common.Deque(maxlen = 2);
DURATION_STATISTICS_FILE = Common.Deque(maxlen = 2);
DURATION_STATISTICS_LOAD = Common.Deque(maxlen = 2);

class Resource :
    
    @classmethod
    def Lunch(Self , Context:Common.Simple) -> None :
        Common.Function.Proctitle('Main_Resource');
        if Self.Check(Context) is True :
            Action = list();
            if CPU is True : Action.append('Cpu');
            if MEMORY is True : Action.append('Memory');
            if NETWORK is True : Action.append('Network');
            if DISK is True : Action.append('Disk');
            if FILE is True : Action.append('File');
            if LOAD is True : Action.append('Load');
            Common.Function.Log(f'Resource 启动完成，正在监听[{" | ".join(Action)}]状况');
            Self.Performance(Context);
        else : Common.Function.Log(f'Resource 无法监听，Cpu | Memory | Network | Disk | File | Load 必须开启其中一个');
    
    @staticmethod
    def Check(Context:Common.Simple) -> bool :
        global CPU , MEMORY , NETWORK , DISK , FILE , LOAD , JOURNAL;
        if Context.Config.Resource.get('Cpu') is True : CPU = True;
        if Context.Config.Resource.get('Memory') is True : MEMORY = True;
        if Context.Config.Resource.get('Network') is True : NETWORK = True;
        if Context.Config.Resource.get('Disk') is True : DISK = True;
        if Context.Config.Resource.get('File') is True : FILE = True;
        if Context.Config.Resource.get('Load') is True and Common.Platform.system().lower() == 'linux' : LOAD = True;
        if Context.Config.Resource.get('Journal') is True : JOURNAL = True;
        return CPU | MEMORY | NETWORK | DISK | FILE | LOAD;
    
    @staticmethod
    def Performance(Context:Common.Simple) -> None :
        while True :
            Common.Time.sleep(Context.Config.Resource.get('Sleep'));
            try :
                if CPU is True : DURATION_PERFORMANCE_CPU.append(Performance.Cpu());
                if MEMORY is True : DURATION_PERFORMANCE_MEMORY.append(Performance.Memory());
                if NETWORK is True : DURATION_PERFORMANCE_NETWORK.append(Performance.Network());
                if DISK is True : DURATION_PERFORMANCE_DISK.append(Performance.Disk());
                if FILE is True : DURATION_PERFORMANCE_FILE.append(Performance.File());
                if LOAD is True : DURATION_PERFORMANCE_LOAD.append(Performance.Load());
                if len(DURATION_PERFORMANCE_CPU) == 2 : DURATION_STATISTICS_CPU.append(Statistics.Cpu());
                if len(DURATION_PERFORMANCE_MEMORY) == 2 : DURATION_STATISTICS_MEMORY.append(Statistics.Memory());
                if len(DURATION_PERFORMANCE_NETWORK) == 2 : DURATION_STATISTICS_NETWORK.append(Statistics.Network());
                if len(DURATION_PERFORMANCE_DISK) == 2 : DURATION_STATISTICS_DISK.append(Statistics.Disk());
                if len(DURATION_PERFORMANCE_FILE) == 2 : DURATION_STATISTICS_FILE.append(Statistics.File());
                if len(DURATION_PERFORMANCE_LOAD) == 2 : DURATION_STATISTICS_LOAD.append(Statistics.Load());
                if JOURNAL is True : Journal.Create(Context);
            except : Common.Function.Trace(Context.Journal);

class Journal() :
    
    @classmethod
    def Create(Self , Context:Common.Simple) -> None :
        Source = list();
        if len(DURATION_STATISTICS_CPU) == 2 : Source.append(Self.Cpu());
        if len(DURATION_STATISTICS_MEMORY) == 2 : Source.append(Self.Memory());
        if len(DURATION_STATISTICS_NETWORK) == 2 : Source.append(Self.Network());
        if len(DURATION_STATISTICS_DISK) == 2 : Source.append(Self.Disk());
        if len(DURATION_STATISTICS_FILE) == 2 : Source.append(Self.File());
        if len(DURATION_STATISTICS_LOAD) == 2 : Source.append(Self.Load());
        if not len(Source) == 0 :
            Log = list();
            for Item in Source :
                Log.append(f'|== {"==" * 20}');
                for Index , Value in enumerate(Item) : Log.append(f'|{"--" if Index == 0 else "----"} {Value}');
            Log.append(f'|== {"==" * 20}');
            Context.Journal.put(dict(
                Method = 'Resource' ,
                Body = Log ,
            ));
    
    @staticmethod
    def Cpu() -> list :
        Statistics_Previous , Statistics_Currently = DURATION_STATISTICS_CPU;
        Performance_Previous , Performance_Currently = DURATION_PERFORMANCE_CPU;
        Source = list();
        Source.append('中央处理器');
        Source.append('----' * 10);
        Source.append(' | '.join([
            '系统进程' ,
            f'增长[{Statistics_Currently.Process}]个' ,
            f'趋势[{Statistics_Currently.Process - Statistics_Previous.Process}]个' ,
            f'本次[{Performance_Currently.Process}]个' ,
            f'上次[{Performance_Previous.Process}]个' ,
        ]));
        Source.append('----' * 10);
        Source.append(' | '.join([
            '系统线程' ,
            f'增长[{Statistics_Currently.Thread}]个' ,
            f'趋势[{Statistics_Currently.Thread - Statistics_Previous.Thread}]个' ,
            f'本次[{Performance_Currently.Thread}]个' ,
            f'上次[{Performance_Previous.Thread}]个' ,
        ]));
        Source.append('----' * 10);
        Source.append(' | '.join([
            '核心使用率' ,
            f'增长[{Statistics_Currently.Core}]%' ,
            f'趋势[{Statistics_Currently.Core - Statistics_Previous.Core}]%' ,
            f'本次[{Performance_Currently.Core}]%' ,
            f'上次[{Performance_Previous.Core}]%' ,
        ]));
        Source.append('----' * 10);
        for Index , Value in enumerate(Statistics_Currently.Respective) : Source.append(' | '.join([
            f'内核[{Index + 1}]' ,
            f'增长[{Value}]%' ,
            f'趋势[{Value - Statistics_Previous.Respective[Index]}]%' ,
            f'本次[{Performance_Currently.Respective[Index]}]%' ,
            f'上次[{Performance_Previous.Respective[Index]}]%' ,
        ]));
        for Pid in Statistics_Currently.Expense :
            if Pid in Performance_Currently.Expense and Pid in Performance_Previous.Expense and Pid in Statistics_Previous.Expense :
                Source.append('----' * 10);
                Source.append(' | '.join([
                    f'程序[{Pid}]' ,
                    f'名称[{Statistics_Currently.Expense[Pid].Name}]' ,
                ]));
                Source.append(' | '.join([
                    f'CPU' ,
                    f'增长[{Statistics_Currently.Expense[Pid].Cpu}]%' ,
                    f'趋势[{Statistics_Currently.Expense[Pid].Cpu - Statistics_Previous.Expense[Pid].Cpu}]%' ,
                    f'本次[{Performance_Currently.Expense[Pid].Cpu}]%' ,
                    f'上次[{Performance_Previous.Expense[Pid].Cpu}]%' ,
                ]));
                Source.append(' | '.join([
                    f'MEMORY' ,
                    f'增长[{Statistics_Currently.Expense[Pid].Memory}]%' ,
                    f'趋势[{Statistics_Currently.Expense[Pid].Memory - Statistics_Previous.Expense[Pid].Memory}]%' ,
                    f'本次[{Performance_Currently.Expense[Pid].Memory}]%' ,
                    f'上次[{Performance_Previous.Expense[Pid].Memory}]%' ,
                ]));
        return Source;
    
    @staticmethod
    def Memory() -> list :
        Statistics_Previous , Statistics_Currently = DURATION_STATISTICS_MEMORY;
        Performance_Previous , Performance_Currently = DURATION_PERFORMANCE_MEMORY;
        Source = list();
        Source.append('系统内存');
        Source.append(' | '.join([
            '总内存' ,
            f'[{Performance_Currently.Total}]Mb' ,
        ]));
        Source.append(' | '.join([
            '使用率' ,
            f'增长[{Statistics_Currently.Percent}]%' ,
            f'趋势[{Statistics_Currently.Percent - Statistics_Previous.Percent}]%' ,
            f'本次[{Performance_Currently.Percent}]%' ,
            f'上次[{Performance_Previous.Percent}]%' ,
        ]));
        Source.append(' | '.join([
            '已使用' ,
            f'增长[{Statistics_Currently.Used}]%' ,
            f'趋势[{Statistics_Currently.Used - Statistics_Previous.Used}]%' ,
            f'本次[{Performance_Currently.Used}]Mb' ,
            f'上次[{Performance_Previous.Used}]Mb' ,
        ]));
        Source.append(' | '.join([
            '可用' ,
            f'增长[{Statistics_Currently.Available}]%' ,
            f'趋势[{Statistics_Currently.Available - Statistics_Previous.Available}]%' ,
            f'本次[{Performance_Currently.Available}]Mb' ,
            f'上次[{Performance_Previous.Available}]Mb' ,
        ]));
        Source.append(' | '.join([
            '缓存' ,
            f'增长[{Statistics_Currently.Cached}]%' ,
            f'趋势[{Statistics_Currently.Cached - Statistics_Previous.Cached}]%' ,
            f'本次[{Performance_Currently.Cached}]Mb' ,
            f'上次[{Performance_Previous.Cached}]Mb' ,
        ]));
        return Source;
    
    @staticmethod
    def Network() -> list :
        Statistics_Previous , Statistics_Currently = DURATION_STATISTICS_NETWORK;
        Performance_Previous , Performance_Currently = DURATION_PERFORMANCE_NETWORK;
        Source = list();
        Source.append('系统网络');
        for X in Statistics_Currently.Send.Bytes :
            Source.append('----' * 10);
            Source.append(f'网卡[{X}]');
            Source.append(' | '.join([
                '发送字节' ,
                f'增长[{Statistics_Currently.Send.Bytes[X]}]%' ,
                f'趋势[{Statistics_Currently.Send.Bytes[X] - Statistics_Previous.Send.Bytes[X]}]%' ,
                f'本次[{Performance_Currently.Send.Bytes[X]}]bytes' ,
                f'上次[{Performance_Previous.Send.Bytes[X]}]bytes' ,
            ]));
            Source.append(' | '.join([
                '发送包数' ,
                f'增长[{Statistics_Currently.Send.Packets[X]}]%' ,
                f'趋势[{Statistics_Currently.Send.Packets[X] - Statistics_Previous.Send.Packets[X]}]%' ,
                f'本次[{Performance_Currently.Send.Packets[X]}]个' ,
                f'上次[{Performance_Previous.Send.Packets[X]}]个' ,
            ]));
            Source.append(' | '.join([
                '接收字节' ,
                f'增长[{Statistics_Currently.Receive.Bytes[X]}]%' ,
                f'趋势[{Statistics_Currently.Receive.Bytes[X] - Statistics_Previous.Receive.Bytes[X]}]%' ,
                f'本次[{Performance_Currently.Receive.Bytes[X]}]bytes' ,
                f'上次[{Performance_Previous.Receive.Bytes[X]}]bytes' ,
            ]));
            Source.append(' | '.join([
                '接收包数' ,
                f'增长[{Statistics_Currently.Receive.Packets[X]}]%' ,
                f'趋势[{Statistics_Currently.Receive.Packets[X] - Statistics_Previous.Receive.Packets[X]}]%' ,
                f'本次[{Performance_Currently.Receive.Packets[X]}]个' ,
                f'上次[{Performance_Previous.Receive.Packets[X]}]个' ,
            ]));
            Source.append(' | '.join([
                '入丢包次数' ,
                f'增长[{Statistics_Currently.Drop.In[X]}]%' ,
                f'趋势[{Statistics_Currently.Drop.In[X] - Statistics_Previous.Drop.In[X]}]%' ,
                f'本次[{Performance_Currently.Drop.In[X]}]次' ,
                f'上次[{Performance_Previous.Drop.In[X]}]次' ,
            ]));
            Source.append(' | '.join([
                '出丢包字节' ,
                f'增长[{Statistics_Currently.Drop.Out[X]}]%' ,
                f'趋势[{Statistics_Currently.Drop.Out[X] - Statistics_Previous.Drop.Out[X]}]%' ,
                f'本次[{Performance_Currently.Drop.Out[X]}]次' ,
                f'上次[{Performance_Previous.Drop.Out[X]}]次' ,
            ]));
            Source.append(' | '.join([
                '入错误次数' ,
                f'增长[{Statistics_Currently.Error.In[X]}]%' ,
                f'趋势[{Statistics_Currently.Error.In[X] - Statistics_Previous.Error.In[X]}]%' ,
                f'本次[{Performance_Currently.Error.In[X]}]次' ,
                f'上次[{Performance_Previous.Error.In[X]}]次' ,
            ]));
            Source.append(' | '.join([
                '出错误字节' ,
                f'增长[{Statistics_Currently.Error.Out[X]}]%' ,
                f'趋势[{Statistics_Currently.Error.Out[X] - Statistics_Previous.Error.Out[X]}]%' ,
                f'本次[{Performance_Currently.Error.Out[X]}]次' ,
                f'上次[{Performance_Previous.Error.Out[X]}]次' ,
            ]));
        return Source;
    
    @staticmethod
    def Disk() -> list :
        Statistics_Previous , Statistics_Currently = DURATION_STATISTICS_DISK;
        Performance_Previous , Performance_Currently = DURATION_PERFORMANCE_DISK;
        Source = list();
        Source.append('系统磁盘');
        Source.append(' | '.join([
            '读字节' ,
            f'增长[{Statistics_Currently.Read}]%' ,
            f'趋势[{Statistics_Currently.Read - Statistics_Previous.Read}]%' ,
            f'本次[{Performance_Currently.Read}]bytes' ,
            f'上次[{Performance_Previous.Read}]bytes' ,
        ]));
        Source.append(' | '.join([
            '写字节' ,
            f'增长[{Statistics_Currently.Write}]%' ,
            f'趋势[{Statistics_Currently.Write - Statistics_Previous.Write}]%' ,
            f'本次[{Performance_Currently.Write}]bytes' ,
            f'上次[{Performance_Previous.Write}]bytes' ,
        ]));
        Source.append(' | '.join([
            '忙碌时间' ,
            f'增长[{Statistics_Currently.Time}]ms' ,
            f'趋势[{Statistics_Currently.Time - Statistics_Previous.Time}]ms' ,
            f'本次[{Performance_Currently.Time}]ms' ,
            f'上次[{Performance_Previous.Time}]ms' ,
        ]));
        return Source;
    
    @staticmethod
    def File() -> list :
        Statistics_Previous , Statistics_Currently = DURATION_STATISTICS_FILE;
        Performance_Previous , Performance_Currently = DURATION_PERFORMANCE_FILE;
        Source = list();
        Source.append('系统文件');
        Source.append(' | '.join([
            '文件句柄' ,
            f'增长[{Statistics_Currently}]次' ,
            f'趋势[{Statistics_Currently - Statistics_Previous}]次' ,
            f'本次[{Performance_Currently}]次' ,
            f'上次[{Performance_Previous}]次' ,
        ]));
        return Source;
    
    @staticmethod
    def Load() -> list :
        Statistics_Previous , Statistics_Currently = DURATION_STATISTICS_LOAD;
        Performance_Previous , Performance_Currently = DURATION_PERFORMANCE_LOAD;
        Source = list();
        Source.append('系统负载');
        Source.append(' | '.join([
            '每1分钟' ,
            f'增长[{Statistics_Currently.One}]%' ,
            f'趋势[{Statistics_Currently.One - Statistics_Previous.One}]%' ,
            f'本次[{Performance_Currently.One}]%' ,
            f'上次[{Performance_Previous.One}]%' ,
        ]));
        Source.append(' | '.join([
            '每5分钟' ,
            f'增长[{Statistics_Currently.Five}]%' ,
            f'趋势[{Statistics_Currently.Five - Statistics_Previous.Five}]%' ,
            f'本次[{Performance_Currently.Five}]%' ,
            f'上次[{Performance_Previous.Five}]%' ,
        ]));
        Source.append(' | '.join([
            '每15分钟' ,
            f'增长[{Statistics_Currently.Fifteen}]%' ,
            f'趋势[{Statistics_Currently.Fifteen - Statistics_Previous.Fifteen}]%' ,
            f'本次[{Performance_Currently.Fifteen}]%' ,
            f'上次[{Performance_Previous.Fifteen}]%' ,
        ]));
        return Source;

class Statistics :
    
    @staticmethod
    def Cpu() -> Common.Simple :
        Previous , Currently = DURATION_PERFORMANCE_CPU;
        Source = Common.Simple();
        Source.Process = Currently.Process - Previous.Process;
        Source.Thread = Currently.Thread - Previous.Thread;
        Source.Core = Currently.Core - Previous.Core;
        Source.Respective = list();
        Source.Expense = dict();
        for Index , Value in enumerate(Currently.Respective) : Source.Respective.append(Value - Previous.Respective[Index]);
        for Pid in Currently.Expense :
            if Pid in Previous.Expense : Source.Expense[Pid] = Common.Simple(
                Cpu = Currently.Expense[Pid].Cpu - Previous.Expense[Pid].Cpu ,
                Memory = Currently.Expense[Pid].Memory - Previous.Expense[Pid].Memory ,
                Name = Currently.Expense[Pid].Name ,
            );
        return Source;
    
    @staticmethod
    def Memory() -> Common.Simple :
        Previous , Currently = DURATION_PERFORMANCE_MEMORY;
        Source = Common.Simple();
        Source.Total = Currently.Total - Previous.Total;
        Source.Used = Currently.Used - Previous.Used;
        Source.Available = Currently.Available - Previous.Available;
        Source.Cached = Currently.Cached - Previous.Cached;
        Source.Percent = Currently.Percent - Previous.Percent;
        return Source;
    
    @staticmethod
    def Network() -> Common.Simple :
        Previous , Currently = DURATION_PERFORMANCE_NETWORK;
        Source = Common.Simple(
            Send = Common.Simple(
                Bytes = dict() ,
                Packets = dict() ,
            ) ,
            Receive = Common.Simple(
                Bytes = dict() ,
                Packets = dict() ,
            ) ,
            Drop = Common.Simple(
                In = dict() ,
                Out = dict() ,
            ) ,
            Error = Common.Simple(
                In = dict() ,
                Out = dict() ,
            ) ,
        );
        for X in Currently.Send.Bytes : Source.Send.Bytes[X] = Currently.Send.Bytes[X] - Previous.Send.Bytes[X];
        for X in Currently.Send.Packets : Source.Send.Packets[X] = Currently.Send.Packets[X] - Previous.Send.Packets[X];
        for X in Currently.Receive.Bytes : Source.Receive.Bytes[X] = Currently.Receive.Bytes[X] - Previous.Receive.Bytes[X];
        for X in Currently.Receive.Packets : Source.Receive.Packets[X] = Currently.Receive.Packets[X] - Previous.Receive.Packets[X];
        for X in Currently.Drop.In : Source.Drop.In[X] = Currently.Drop.In[X] - Previous.Drop.In[X];
        for X in Currently.Drop.Out : Source.Drop.Out[X] = Currently.Drop.Out[X] - Previous.Drop.Out[X];
        for X in Currently.Error.In : Source.Error.In[X] = Currently.Error.In[X] - Previous.Error.In[X];
        for X in Currently.Error.Out : Source.Error.Out[X] = Currently.Error.Out[X] - Previous.Error.Out[X];
        return Source;
    
    @staticmethod
    def Disk() -> Common.Simple :
        Previous , Currently = DURATION_PERFORMANCE_DISK;
        Source = Common.Simple();
        Source.Read = Currently.Read - Previous.Read;
        Source.Write = Currently.Write - Previous.Write;
        Source.Time = Currently.Time - Previous.Time;
        return Source;
    
    @staticmethod
    def File() -> int :
        Previous , Currently = DURATION_PERFORMANCE_FILE;
        Source = Currently - Previous;
        return int(Source);
    
    @staticmethod
    def Load() -> Common.Simple :
        Previous , Currently = DURATION_PERFORMANCE_LOAD;
        Source = Common.Simple();
        Source.One = Currently.One - Previous.One;
        Source.Five = Currently.Five - Previous.Five;
        Source.Fifteen = Currently.Fifteen - Previous.Fifteen;
        return Source;

class Performance :
    
    @staticmethod
    def Cpu() -> Common.Simple :
        Source = Common.Simple(
            Process = 0 ,
            Thread = 0 ,
            Core = round(Common.Psutil.cpu_percent() , 10) ,
            Respective = Common.Psutil.cpu_percent(percpu = True) ,
            Expense = dict() ,
        );
        try :
            for X in Common.Psutil.process_iter() :
                try :
                    Source.Process += 1;
                    Source.Thread += X.num_threads();
                except : continue;
        except :
            Source.Process = -1;
            Source.Thread = -1;
        for X in Common.Psutil.Process(Common.Os.getppid()).children(recursive = True) : Source.Expense[X.pid] = Common.Simple(
            Cpu = round(X.cpu_percent() , 10) ,
            Memory = round(X.memory_info().rss / 1024 / 1024 , 10) ,
            Name = X.name() ,
        );
        return Source;
    
    @staticmethod
    def Memory() -> Common.Simple :
        Virtual = Common.Psutil.virtual_memory();
        return Common.Simple(
            Total = round(Virtual.total / 1024 / 1024 , 10) ,
            Used = round(Virtual.used / 1024 / 1024 , 10) ,
            Available = round(Virtual.available / 1024 / 1024 , 10) ,
            Cached = round(getattr(Virtual , 'cached' , 0) / 1024 / 1024 , 10) ,
            Percent = round(Virtual.percent , 10) ,
        );
    
    @staticmethod
    def Network() -> Common.Simple :
        Current = Common.Simple(
            Send = Common.Simple(
                Bytes = dict() ,
                Packets = dict() ,
            ) ,
            Receive = Common.Simple(
                Bytes = dict() ,
                Packets = dict() ,
            ) ,
            Drop = Common.Simple(
                In = dict() ,
                Out = dict() ,
            ) ,
            Error = Common.Simple(
                In = dict() ,
                Out = dict() ,
            ) ,
        );
        Counters = Common.Psutil.net_io_counters(pernic = True)
        for X in Counters :
            Current.Send.Bytes[X] = round(Counters[X].bytes_sent , 10);
            Current.Receive.Bytes[X] = round(Counters[X].bytes_recv , 10);
            Current.Send.Packets[X] = round(Counters[X].packets_sent , 10);
            Current.Receive.Packets[X] = round(Counters[X].packets_recv , 10);
            Current.Drop.In[X] = round(Counters[X].dropin , 10);
            Current.Drop.Out[X] = round(Counters[X].dropout , 10);
            Current.Error.In[X] = round(Counters[X].errin , 10);
            Current.Error.Out[X] = round(Counters[X].errout , 10);
        return Current;
    
    @staticmethod
    def Disk() -> Common.Simple :
        Counters = Common.Psutil.disk_io_counters();
        return Common.Simple(
            Read = round(Counters.read_bytes , 10) ,
            Write = round(Counters.write_bytes , 10) ,
            Time = getattr(Counters , 'busy_time' , 0) ,
        );
    
    @staticmethod
    def File() -> int :
        Process = Common.Psutil.Process();
        try : return Process.num_fds();
        except :
            try : return Process.num_handles();
            except : return -1;
    
    @staticmethod
    def Load() -> Common.Simple :
        Avg = Common.Os.getloadavg();
        Source = Common.Simple(
            One = round(Avg[0] , 10) ,
            Five = round(Avg[1] , 10) ,
            Fifteen = round(Avg[2] , 10) ,
        );
        return Source;