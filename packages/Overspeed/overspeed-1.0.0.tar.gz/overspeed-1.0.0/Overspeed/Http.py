from . import Common;

class Http :
    
    @classmethod
    def Lunch(Self , Context:Common.Simple) -> None :
        Context.Signal = Common.Simple(
            Method = 'Http' ,
            Config = Context.Config.Http ,
            Handle = Self.Client ,
        );
        Common.Organic.Lunch(Context);
    
    @classmethod
    async def Client(Self , Context:Common.Simple , Reader:Common.Asyncio.StreamReader , Writer:Common.Asyncio.StreamWriter) -> None :
        try :
            if Common.Organic.Check(Context , 'Black') is True : raise ValueError(406);
            while True :
                Context.Signal.Request = await Common.Organic.Request(Reader);
                if Context.Signal.Request.Status is False : break;
                if Context.Config.Http.get('Journal') is True : Context.Journal.put(dict(
                    Method = 'Http' ,
                    Type = 'Request' ,
                    Body = Context.Signal ,
                ));
                if len(Context.Signal.Request.Header) == 0 : raise ValueError(402);
                if int(Context.Signal.Request.Header.get('content-length' , 0)) > Context.Signal.Config.get('Large') : raise ValueError(413);
                if Context.Signal.Request.Method == 'OPTIONS' : raise ValueError(204);
                if Common.Organic.Check(Context , 'Limiting') is True : raise ValueError(429);
                if Common.Organic.Check(Context , 'Permission') is True : raise ValueError(405);
                Common.Asyncio.create_task(Common.Organic.Task(Common.Copy.deepcopy(Context.Signal) , Context.Journal , Writer));
        except ValueError as Error :
            try :
                Context.Signal.Response = dict(Code = Error.args[0]);
                await Common.Organic.Response(Context.Signal , Context.Journal , Writer);
            except : Common.Function.Trace(Context.Journal);
        except : Common.Function.Trace(Context.Journal);