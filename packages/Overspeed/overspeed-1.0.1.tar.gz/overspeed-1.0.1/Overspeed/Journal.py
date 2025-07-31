from . import Common;

class Journal :
    
    @classmethod
    def Lunch(Self , Context:Common.Simple) -> None :
        Common.Function.Proctitle('Main_Journal');
        if Self.Check(Context) is False : Common.Function.Log(f'Journal 无法监听，Http | Websocket | Resource 必须开启其中一个');
        else :
            Action = list();
            if Context.Config.Http.get('Journal' , False) is True : Action.append('Http');
            if Context.Config.Websocket.get('Journal' , False) is True : Action.append('Websocket');
            if Context.Config.Resource.get('Journal' , False) is True : Action.append('Resource');
            with Common.ThreadPoolExecutor(max_workers = Context.Config.Journal.get('Thread')) as Executor :
                Common.Function.Log(f'Journal 启动完成，正在监听[{" | ".join(Action)}]信息');
                while True :
                    if Context.Journal.qsize() == 0 : continue;
                    Source = Context.Journal.get();
                    if hasattr(Self , Source.get('Method' , None)) is True : Executor.submit(getattr(Self , Source.get('Method')) , Source , Context);
    
    @staticmethod
    def Check(Context:Common.Simple) -> bool :
        return Context.Config.Http.get('Journal' , False) | Context.Config.Websocket.get('Journal' , False) | Context.Config.Resource.get('Journal' , False);
    
    @classmethod
    def Trace(Self , Source:str , Context:Common.Simple) -> None :
        Self.Save(Source.get('Body') , dict(
            Print = True ,
            Path = Context.Config.Journal.get('Path').get('Trace') ,
            Size = Context.Config.Journal.get('Size') ,
            Type = '' ,
        ));
    
    @classmethod
    def Http(Self , Source:dict , Context:Common.Simple) -> None :
        Log = list();
        if Source.get('Type' , None) == 'Request' : Log = Self.Request(Source.get('Body'));
        elif Source.get('Type' , None) == 'Response' : Log = Self.Response(Source.get('Body'));
        if not len(Log) == 0 : Self.Save('\n'.join(Log) , dict(
            Print = Context.Config.Journal.get('Print').get('Http') ,
            Path = Context.Config.Journal.get('Path').get('Http') ,
            Size = Context.Config.Journal.get('Size') ,
            Type = Source.get('Type') ,
        ));
    
    @classmethod
    def Websocket(Self , Source:dict , Context:Common.Simple) -> None :
        Log = list();
        if Source.get('Type' , None) == 'Request' : Log = Self.Request(Source.get('Body'));
        elif Source.get('Type' , None) == 'Response' : Log = Self.Response(Source.get('Body'));
        if not len(Log) == 0 : Self.Save('\n'.join(Log) , dict(
            Print = Context.Config.Journal.get('Print').get('Websocket') ,
            Path = Context.Config.Journal.get('Path').get('Websocket') ,
            Size = Context.Config.Journal.get('Size') ,
            Type = Source.get('Type') ,
        ));
    
    @classmethod
    def Resource(Self , Source:dict , Context:Common.Simple) -> None :
        Self.Save('\n'.join(Source.get('Body')) , dict(
            Print = Context.Config.Journal.get('Print').get('Resource') ,
            Path = Context.Config.Journal.get('Path').get('Resource') ,
            Size = Context.Config.Journal.get('Size') ,
            Type = '' ,
        ));
    
    @classmethod
    def Request(Self , Source:Common.Simple) -> list :
        Log = list();
        try :
            Log.append(' | '.join([
                'Uuid' ,
                f'[{Source.Uuid}]' ,
            ]));
            Log.append(' | '.join([
                'Socket' ,
                f'[{Source.Socket}]' ,
            ]));
            Log.append(' | '.join([
                'Pid' ,
                f'Server[{Source.Pid.Server}]' ,
                f'Worker[{Source.Pid.Worker}]' ,
            ]));
            Log.append('----' * 10);
            Log.append(' | '.join([
                'Network' ,
            ]));
            Log.append(' | '.join([
                'Location' ,
                f'Ip[{Source.Network.Location[0]}]' ,
                f'Port[{Source.Network.Location[1]}]' ,
            ]));
            Log.append(' | '.join([
                'Remote' ,
                f'Ip[{Source.Network.Remote[0]}]' ,
                f'Port[{Source.Network.Remote[1]}]' ,
            ]));
            Log.append('----' * 10);
            Log.append(' | '.join([
                'Cors' ,
                f'[{Source.Request.Cors}]' ,
            ]));
            Log.append(' | '.join([
                'Method' ,
                f'[{Source.Request.Method}]' ,
            ]));
            Log.append(' | '.join([
                'Url' ,
                f'[{Source.Request.Url}]' ,
            ]));
            Log.append(' | '.join([
                'Path' ,
                f'[{Source.Request.Path}]' ,
            ]));
            Log.append('----' * 10);
            Log.append('Query');
            for X in Source.Request.Query : Log.append(' | '.join([
                X ,
                f'[{Common.Json.dumps(Source.Request.Query.get(X)).decode()}]' ,
            ]));
            Log.append('----' * 10);
            Log.append('Body');
            for X in Source.Request.Body : Log.append(' | '.join([
                X ,
                f'[{Common.Json.dumps(Source.Request.Body.get(X)).decode()}]' ,
            ]));
            Log.append('----' * 10);
            Log.append('Header');
            for X in Source.Request.Header : Log.append(' | '.join([
                X ,
                f'[{Common.Json.dumps(Source.Request.Header.get(X)).decode()}]' ,
            ]));
            Log.append('----' * 10);
            Log.append('Original');
            for X in Source.Request.Original.decode().split('\r\n') :
                if X : Log.append(X);
        except : Common.Function.Trace();
        finally : return Self.Change(Log);
    
    @classmethod
    def Response(Self , Source:Common.Simple) -> list :
        Log = list();
        try :
            Log.append(' | '.join([
                'Uuid' ,
                f'[{Source.Uuid}]' ,
            ]));
            for X in Source.Response : Log.append(' | '.join([
                X ,
                f'[{Common.Json.dumps(Source.Response.get(X)).decode()}]' ,
            ]));
        except : Common.Function.Trace();
        finally : return Self.Change(Log);
    
    @staticmethod
    def Change(Source:list) -> list :
        Log = list();
        if not len(Source) == 0 :
            for Item in Source :
                Log.append(f'|-- {Item}');
        return Log;
    
    @staticmethod
    def Save(Source:str , Config:dict) -> None :
        try :
            Calendar = Common.Function.Time(Method = '%Y-%m-%d');
            Hour = Common.Function.Time(Method = '%H');
            Minute = Common.Function.Time(Method = '%M');
            Path = Common.Os.path.realpath('/'.join([
                Common.Os.getcwd() ,
                Config.get('Path') ,
                Config.get('Type') ,
                Calendar ,
                Hour ,
            ]));
            if Common.Os.path.exists(Path) is False : Common.Os.makedirs(Path , exist_ok = True);
            Log = '\n'.join([
                f'|## {"##" * 50}' ,
                f'|| {Common.Function.Time(Method = True)}' ,
                '' ,
                Source ,
                f'|## {"##" * 50}' ,
                '' ,
            ]);
            with open(Common.Os.path.normpath(f'{Path}/{Minute}.log') , 'a' , encoding = 'utf-8') as File : Common.Function.Log(Log , File = File);
            if Config.get('Print') is True : Common.Function.Log(Log);
        except : Common.Function.Trace();