from . import Common;

class Websocket :
    
    @classmethod
    def Lunch(Self , Context:Common.Simple) -> None :
        Context.Signal = Common.Simple(
            Method = 'Websocket' ,
            Config = Context.Config.Websocket ,
            Handle = Self.Client ,
        );
        Common.Organic.Lunch(Context);
    
    @classmethod
    async def Client(Self , Context:Common.Simple , Reader:Common.Asyncio.StreamReader , Writer:Common.Asyncio.StreamWriter) -> None :
        try :
            if Common.Organic.Check(Context , 'Black') is True : raise ValueError(406);
            Context.Signal.Request = await Common.Organic.Request(Reader);
            if len(Context.Signal.Request.Header) == 0 : raise ValueError(402);
            if Common.Organic.Check(Context , 'Permission') is True : raise ValueError(405);
            if Context.Signal.Request.Header.get('upgrade' , str()).lower() == 'websocket' :
                await Common.Organic.Upgrade(Context , Writer);
                await Common.Organic.Session(Context , Reader , Writer);
        except ValueError as Error :
            try :
                Context.Signal.Response = dict(Code = Error.args[0]);
                await Common.Organic.Send(Context.Signal , Context.Journal , Writer);
            except : Common.Function.Trace(Context.Journal);
        except : Common.Function.Trace(Context.Journal);