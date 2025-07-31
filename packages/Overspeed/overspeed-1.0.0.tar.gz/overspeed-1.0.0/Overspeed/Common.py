import os as Os;
import ssl as Ssl;
import copy as Copy;
import time as Time;
import uuid as Uuid;
import orjson as Json;
import socket as Socket;
import base64 as Base64;
import struct as Struct;
import psutil as Psutil;
import shutil as Shutil;
import hashlib as Hashlib;
import asyncio as Asyncio;
import platform as Platform;
import functools as Functools;
import traceback as Traceback;
import subprocess as Subprocess;
from urllib import parse as Parse;
import multiprocessing as Processing;
from http.cookies import SimpleCookie;
from collections import deque as Deque;
from datetime import datetime as Datetime;
from types import SimpleNamespace as Simple;
from concurrent.futures import ThreadPoolExecutor;
from setproctitle import setproctitle as Setproctitle;
try : from uvloop import EventLoopPolicy;
except : pass;

class Function :
    
    @staticmethod
    def Proctitle(Source:str) -> None :
        Setproctitle(f'{Config.Proctitle.get(Source)}.{Os.getpid()}');
    
    @staticmethod
    def Trace(Journal = None) -> None :
        if Journal is None : print(Traceback.format_exc() , end = '\n');
        else : Journal.put(dict(
            Method = 'Trace' ,
            Body = Traceback.format_exc() ,
        ));
    
    @staticmethod
    def Log(Source:str , File = None) -> None :
        print(Source , end = '\n' , file = File);
    
    @classmethod
    def Configure(Self , Source:dict) -> Simple :
        Anonymous = Simple();
        for Primary in dir(Config) :
            if Primary.startswith('__') is True or isinstance(getattr(Config , Primary) , dict) is False : continue;
            if Primary not in Source or len(Source.get(Primary)) == 0 : setattr(Anonymous , Primary , getattr(Config , Primary));
            else : setattr(Anonymous , Primary , Self.Nesting(getattr(Config , Primary) , Source.get(Primary)));
        return Anonymous;
    
    @classmethod
    def Nesting(Self , Originally:dict , Source:dict) -> dict :
        for Primary in Originally :
            if Primary not in Source : continue;
            if isinstance(Source.get(Primary) , dict) is True : Originally[Primary] = Self.Nesting(Originally.get(Primary) , Source.get(Primary));
            else : Originally[Primary] = Source.get(Primary);
        return Originally;
    
    @staticmethod
    def Sysctl(Primary:str , Default:str|None = None) -> str :
        try : return str(Subprocess.run(['sysctl' , '-n' , Primary] , capture_output = True , text = True , check = True).stdout.strip());
        except : return Default;
    
    @staticmethod
    def Hash(Source:str) -> str :
        if isinstance(Source , bytes) is False : Source = Source.encode();
        Data = Hashlib.sha1(Source).digest();
        return Base64.b64encode(Data).decode();
    
    @classmethod
    def Ssl(Self , Source:dict) -> Ssl.SSLContext|None :
        if Source.get('Certfile') == '' or Source.get('Keyfile') == '' : return None;
        Primary = f'CTX_{Self.Hash(Json.dumps(dict(
            Certfile = Source.get('Certfile') ,
            Keyfile = Source.get('Keyfile') ,
        )))}';
        if hasattr(Self , Primary) is False :
            Ctx = Ssl.SSLContext(Ssl.PROTOCOL_TLS_SERVER);
            Ctx.load_cert_chain(certfile = f'{Os.getcwd()}{Source.get("Certfile")}' , keyfile = f'{Os.getcwd()}{Source.get("Keyfile")}');
            Ctx.set_ciphers('ECDHE+AESGCM');
            Ctx.options |= Ssl.OP_NO_COMPRESSION;
            setattr(Self , Primary , Ctx);
        return getattr(Self , Primary);
    
    @staticmethod
    def Bytes(Source , Suffix = 'B') :
        for Unit in ['' , 'K' , 'M' , 'G' , 'T' , 'P'] :
            if abs(Source) < 1024 : return f'{Source:.2f}{Unit}{Suffix}';
            Source /= 1024;
        return f'{Source:.2f}Y{Suffix}';
    
    @staticmethod
    def Time(Method = None , Utc = True , Int = None) :
        Calendar = Datetime.utcnow() if Utc is True else Datetime.now();
        if isinstance(Int , bool) is True :
            Timestamp = Calendar.timestamp();
            return int(Timestamp) if Int is True else Timestamp;
        elif isinstance(Method , str) is True or isinstance(Method , bool) is True :
            if Method is True : Strftime = '%Y-%m-%d %H:%M:%S';
            elif Method is False : Strftime = '%Y-%m-%d';
            else : Strftime = Method;
            return Calendar.strftime(Strftime);
        else : return Calendar;
    
    @staticmethod
    def Uuid() -> str :
        return str(Uuid.uuid4()).replace('-' , '');

class Config :
    
    Proctitle = dict(
        Main = 'Overspeed' ,
        Main_Http = 'Overspeed.Http' ,
        Main_Http_Server = 'Overspeed.Http.Server' ,
        Main_Http_Worker = 'Overspeed.Http.Worker' ,
        Main_Websocket = 'Overspeed.Websocket' ,
        Main_Websocket_Server = 'Overspeed.Websocket.Server' ,
        Main_Websocket_Worker = 'Overspeed.Websocket.Worker' ,
        Main_Journal = 'Overspeed.Journal' ,
        Main_Resource = 'Overspeed.Resource' ,
    );
    Http = dict(
        Status = True ,
        Journal = True ,
        Cpu = Os.cpu_count() ,
        Port = [31100] ,
        Large = 2097152 ,
        Certfile = '' ,
        Keyfile = '' ,
        Callable = None ,
    );
    Websocket = dict(
        Status = True ,
        Journal = True ,
        Cpu = Os.cpu_count() ,
        Port = [32100] ,
        Certfile = '' ,
        Keyfile = '' ,
        Callable = None ,
        Connect = 60 ,
        Timeout = 5 ,
    );
    Resource = dict(
        Status = True ,
        Sleep = 30 ,
        Journal = True ,
        Cpu = True ,
        Memory = True ,
        Network = True ,
        Disk = True ,
        File = True ,
        Load = True ,
    );
    Journal = dict(
        Thread = 100 ,
        Print = dict(
            Http = False ,
            Websocket = False ,
            Resource = False ,
        ) ,
        Path = dict(
            Trace = '/Runtime/Trace/' ,
            Http = '/Runtime/Http/' ,
            Websocket = '/Runtime/Websocket/' ,
            Resource = '/Runtime/Resource/' ,
        ) ,
    );
    Black = dict(
        Status = False ,
        Callable = None ,
    );
    Limiting = dict(
        Status = False ,
        Callable = None ,
    );
    Permission = dict(
        Status = False ,
        Callable = None ,
    );
    Idempotent = dict(
        Status = False ,
        Callable = None ,
    );
    Cache = dict(
        Status = False ,
        Callable = None ,
    );

SOCKET_HOST = '0.0.0.0';
SOCKET_WAITTIME = 5;
SOCKET_LISTEN = int(Function.Sysctl('net.core.somaxconn' , 1024));
SOCKET_BREAK_EMPTY = b'';
SOCKET_BREAK_NEWLINE = b'\r\n';
SOCKET_CORS = SOCKET_BREAK_NEWLINE.join([
    b'Access-Control-Allow-Origin:*' ,
    b'Access-Control-Allow-Methods:GET,POST,PUT,DELETE,OPTIONS' ,
    b'Access-Control-Allow-Headers:*' ,
    SOCKET_BREAK_EMPTY ,
]);
SOCKET_RESPONSE = SOCKET_BREAK_NEWLINE.join([
    b'HTTP/1.1 %s' ,
    b'Content-Type:%s' ,
    b'Content-Length:%d' ,
    b'Connection:%s' ,
    b'%s' ,
    b'%s' ,
]);
SOCKET_UPGRADE = SOCKET_BREAK_NEWLINE.join([
    b'HTTP/1.1 101 Switching Protocols' ,
    b'Upgrade:websocket' ,
    b'Connection:Upgrade' ,
    b'Sec-WebSocket-Accept:%s' ,
    SOCKET_BREAK_EMPTY ,
    SOCKET_BREAK_EMPTY ,
]);
SOCKET_CONNECTION_KEEP = b'keep-alive';
SOCKET_CONNECTION_CLOSE = b'close';
SOCKET_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';
SOCKET_FIN = 0b10000000;
SOCKET_OPCODE = 0b00001111;
SOCKET_PAYLOAD = 0b01111111;
SOCKET_UNPACK_H = '>H';
SOCKET_UNPACK_Q = '>Q';
SOCKET_TYPE_HTML = b'text/html';
SOCKET_TYPE_PLAIN = b'text/plain';
SOCKET_TYPE_STREAM = b'text/event-stream';
SOCKET_TYPE_XML = b'application/xml';
SOCKET_TYPE_JSON = b'application/json';
SOCKET_TYPE_DATA = b'multipart/form-data';
SOCKET_TYPE_FORM = b'application/x-www-form-urlencoded';
SOCKET_CODE_200 = b'200 OK';
SOCKET_CODE_204 = b'204 No Content';
SOCKET_CODE_301 = b'301 Moved Permanently';
SOCKET_CODE_302 = b'302 Found';
SOCKET_CODE_400 = b'400 Bad Request';
SOCKET_CODE_401 = b'401 Unauthorized';
SOCKET_CODE_402 = b'402 Bad Internal';
SOCKET_CODE_403 = b'403 Forbidden';
SOCKET_CODE_404 = b'404 Not Found';
SOCKET_CODE_405 = b'405 Method Not Allowed';
SOCKET_CODE_406 = b'406 Not Acceptable';
SOCKET_CODE_407 = b'407 Body Error';
SOCKET_CODE_408 = b'408 Request Timeout';
SOCKET_CODE_413 = b'413 Payload Too Large';
SOCKET_CODE_415 = b'415 Unsupported Media Type';
SOCKET_CODE_429 = b'429 Too Many Requests';
SOCKET_CODE_500 = b'500 Internal Server Error';
SOCKET_CODE_502 = b'502 Bad Gateway';
SOCKET_CODE_503 = b'503 Service Unavailable';
SOCKET_CODE_504 = b'504 Gateway Timeout';

class Organic :
    
    @classmethod
    def Lunch(Self , Context:Simple) -> None :
        Function.Proctitle(f'Main_{Context.Signal.Method}');
        try : Asyncio.set_event_loop_policy(EventLoopPolicy());
        except : pass;
        Process:list[Processing.Process] = list();
        for Port in Context.Signal.Config.get('Port') : Process.append(Processing.Process(target = Self.Server , args = (Context , Port)));
        for X in Process : X.start();
        for X in Process : X.join();
    
    @classmethod
    def Server(Self , Context:Simple , Port:int) -> None :
        Function.Proctitle(f'Main_{Context.Signal.Method}_Server');
        Server = Socket.socket(Socket.AF_INET , Socket.SOCK_STREAM);
        Server.setsockopt(Socket.SOL_SOCKET , Socket.SO_REUSEADDR , 1);
        try : Server.setsockopt(Socket.SOL_SOCKET , Socket.SO_REUSEPORT , 1);
        except : pass;
        Server.setsockopt(Socket.IPPROTO_TCP , Socket.TCP_NODELAY , 1);
        Server.setsockopt(Socket.SOL_SOCKET , Socket.SO_SNDBUF , 1 << 20);
        Server.setsockopt(Socket.SOL_SOCKET , Socket.SO_RCVBUF , 1 << 20);
        Server.bind((SOCKET_HOST , Port));
        Server.listen(SOCKET_LISTEN);
        Server.setblocking(False);
        if Platform.system().lower() == 'linux' :
            Process:list[Processing.Process] = list();
            for _ in range(0 , Context.Signal.Config.get('Cpu')) : Process.append(Processing.Process(target = Self.Worker , args = (Context , Server) , daemon = True));
            for X in Process : X.start();
            for X in Process : X.join();
        else : Self.Worker(Context , Server);
    
    @classmethod
    def Worker(Self , Context:Simple , Server:Socket.socket) -> None :
        Function.Proctitle(f'Main_{Context.Signal.Method}_Worker');
        Sockname = Server.getsockname();
        Function.Log(f'{Context.Signal.Method} 启动完成，正在监听端口[{Sockname[1]}]，PID[{Os.getpid()}]');
        Asyncio.run(Self.Running(Context , Server));
    
    @classmethod
    async def Running(Self , Context:Simple , Server:Socket.socket) -> None :
        Serve = await Asyncio.start_server(
            Functools.partial(Self.Handle , Context) ,
            sock = Server ,
            backlog = SOCKET_LISTEN ,
            reuse_port = True ,
            ssl = Function.Ssl(Context.Signal.Config) ,
        );
        async with Serve : await Serve.serve_forever();
    
    @classmethod
    async def Handle(Self , Context:Simple , Reader:Asyncio.StreamReader , Writer:Asyncio.StreamWriter) -> None :
        try :
            Socket = Writer.get_extra_info('socket');
            Context.Signal.Uuid = Function.Uuid();
            Context.Signal.Socket = Socket.fileno();
            Context.Signal.Network = Simple(
                Location = list(Socket.getsockname()) ,
                Remote = list(Socket.getpeername()) ,
            );
            Context.Signal.Pid = Simple(
                Server = Os.getppid() ,
                Worker = Os.getpid() ,
            );
            Context.Signal.Request = Simple(
                Status = False ,
                Cors = False ,
                Original = SOCKET_BREAK_EMPTY ,
                Method = str() ,
                Url = str() ,
                Path = str() ,
                Query = dict() ,
                Header = dict() ,
                Body = dict() ,
            );
            Context.Signal.Response = dict();
            await Context.Signal.Handle(Context , Reader , Writer);
        except : Function.Trace(Context.Journal);
        finally :
            try : await Self.Close(Writer);
            except : pass;
    
    @staticmethod
    async def Request(Reader:Asyncio.StreamReader) -> Simple :
        Anonymous = Simple(
            Status = False ,
            Cors = False ,
            Original = SOCKET_BREAK_EMPTY ,
            Method = str() ,
            Url = str() ,
            Path = str() ,
            Query = dict() ,
            Header = dict() ,
            Body = dict() ,
        );
        try :
            Line = await Asyncio.wait_for(Reader.readline() , timeout = SOCKET_WAITTIME);
            Anonymous.Original += Line;
            Data = Line.decode(errors = 'ignore').strip();
            Anonymous.Method , Anonymous.Url , _ = Data.split();
            while True :
                try :
                    Line = await Reader.readline();
                    if Line in (SOCKET_BREAK_EMPTY , SOCKET_BREAK_NEWLINE) : break;
                    Anonymous.Original += Line;
                    Data = Line.decode(errors = 'ignore').strip();
                    if ':' not in Data : continue;
                    Primary , Item = Data.split(':' , 1);
                    if Primary.lower() == 'cookie' :
                        Cookie = SimpleCookie();
                        Cookie.load(Item);
                        Anonymous.Header['cookie'] = dict();
                        for Key , Value in Cookie.items() : Anonymous.Header['cookie'][Key.lower().strip()] = Value.value.strip();
                    else : Anonymous.Header[Primary.lower().strip()] = Item.strip();
                except : break;
            Close = SOCKET_CONNECTION_CLOSE.decode();
            if Anonymous.Header.get('sec-fetch-mode' , 'none').lower() == 'cors' or 'referer' in Anonymous.Header : Anonymous.Cors = True;
            Parser = Parse.urlparse(Anonymous.Url);
            Anonymous.Path = Parser.path;
            Query = Parse.parse_qs(Parser.query , keep_blank_values = True);
            if not len(Query) == 0 :
                for Key , Value in Query.items() : Anonymous.Query[Key.strip()] = Value[0].strip() if len(Value) == 1 else Value;
            Length = int(Anonymous.Header.get('content-length' , 0));
            if not Length == 0 and Anonymous.Method == 'POST' :
                Body = await Reader.readexactly(Length);
                Anonymous.Original += SOCKET_BREAK_NEWLINE + Body;
                try : Anonymous.Body = Json.loads(Body);
                except :
                    Body = Body.decode();
                    Parser = Parse.parse_qs(Body , keep_blank_values = True);
                    if len(Parser) == 0 : Anonymous.Body = Body;
                    else :
                        for Key , Value in Parser.items() : Anonymous.Body[Key.strip()] = Value[0].strip() if len(Value) == 1 else Value;
            Anonymous.Status = True;
        except : pass;
        finally : return Anonymous;
    
    @staticmethod
    async def Close(Writer:Asyncio.StreamWriter) -> None :
        if Writer.is_closing() is True : await Asyncio.sleep(0);
        else :
            Writer.close();
            await Writer.wait_closed();
    
    @staticmethod
    async def Response(Context:Simple , Journal:Processing.Queue , Writer:Asyncio.StreamWriter) -> None :
        if Writer.is_closing() is True : await Asyncio.sleep(0);
        else :
            Code = Context.Response.get('Code' , 200);
            Body = Context.Response.get('Body' , str());
            RESPONSE_CODE = globals().get(f'SOCKET_CODE_{Code}' , SOCKET_CODE_404);
            if not Code == 200 and Body == '' : Body = RESPONSE_CODE;
            if Body is None : Body = SOCKET_BREAK_EMPTY;
            if isinstance(Body , str) is True : Body = Body.encode();
            Accept = Context.Request.Header.get('content-type' , Context.Request.Header.get('accept' , SOCKET_TYPE_HTML.decode()));
            if SOCKET_TYPE_JSON.decode() in Accept : Type = 'json';
            elif SOCKET_TYPE_FORM.decode() in Accept : Type = 'form';
            elif SOCKET_TYPE_STREAM.decode() in Accept : Type = 'stream';
            elif SOCKET_TYPE_HTML.decode() in Accept : Type = 'html';
            elif SOCKET_TYPE_XML.decode() in Accept : Type = 'xml';
            elif SOCKET_TYPE_PLAIN.decode() in Accept : Type = 'plain';
            elif SOCKET_TYPE_DATA.decode() in Accept : Type = 'data';
            else : Type = '';
            RESPONSE_TYPE = globals().get(f'SOCKET_TYPE_{Type.upper()}' , SOCKET_TYPE_HTML);
            RESPONSE_CORS = SOCKET_CORS if Context.Request.Cors is True else SOCKET_BREAK_EMPTY;
            Writer.write(SOCKET_RESPONSE % (
                RESPONSE_CODE ,
                RESPONSE_TYPE ,
                len(Body) ,
                SOCKET_CONNECTION_KEEP ,
                RESPONSE_CORS ,
                Body ,
            ));
            await Writer.drain();
            if Context.Config.get('Journal') is True : Journal.put(dict(
                Method = 'Http' ,
                Type = 'Response' ,
                Body = Context ,
            ));
    
    @staticmethod
    async def Send(Context:Simple , Journal:Processing.Queue , Writer:Asyncio.StreamWriter) -> None :
        if Writer.is_closing() is True : await Asyncio.sleep(0);
        else :
            Code = Context.Response.get('Code' , 200);
            Body = Context.Response.get('Body' , str());
            if Body is None : Body = SOCKET_BREAK_EMPTY.decode();
            if not Code == 200 and Body == '' : Body = globals().get(f'SOCKET_CODE_{Code}' , SOCKET_CODE_404).decode();
            Context.Response['Body'] = Body;
            Data = Json.dumps(Context.Response);
            Header = bytearray();
            Header.append(0x81);
            Length = len(Data);
            if Length <= 125 : Header.append(Length);
            elif Length < 65535 :
                Header.append(126);
                Header += Struct.pack(SOCKET_UNPACK_H , Length);
            else :
                Header.append(127);
                Header += Struct.pack(SOCKET_UNPACK_Q , Length);
            Writer.write(Header + Data);
            await Writer.drain();
            if Context.Config.get('Journal') is True : Journal.put(dict(
                Method = 'Websocket' ,
                Type = 'Response' ,
                Body = Context ,
            ));
    
    @classmethod
    async def Upgrade(Self , Context:Simple , Writer:Asyncio.StreamWriter) -> None :
        if Writer.is_closing() is True : await Asyncio.sleep(0);
        else :
            Writer.write(SOCKET_UPGRADE % (
                Function.Hash(f'{Context.Signal.Request.Header.get("sec-websocket-key")}{SOCKET_GUID}').encode() ,
            ));
            await Writer.drain();
    
    @classmethod
    async def Session(Self , Context:Simple , Reader:Asyncio.StreamReader , Writer:Asyncio.StreamWriter) -> None :
        try :
            Begin = Function.Time(Int = True);
            while True :
                if (Function.Time(Int = True) - Begin) > int(Context.Config.Websocket.get('Connect')) : break;
                if int(Context.Config.Websocket.get('Timeout')) > 0 :
                    try : Header = await Asyncio.wait_for(Reader.readexactly(2) , timeout = int(Context.Config.Websocket.get('Timeout')));
                    except : break;
                else : Header = await Reader.readexactly(2);
                Fin = Header[0] & SOCKET_FIN;
                Opcode = Header[0] & SOCKET_OPCODE;
                Masked = Header[1] & SOCKET_FIN;
                Payload = Header[1] & SOCKET_PAYLOAD;
                if Payload == 126 : Payload = Struct.unpack(SOCKET_UNPACK_H , await Reader.readexactly(2))[0];
                if Payload == 127 : Payload = Struct.unpack(SOCKET_UNPACK_Q , await Reader.readexactly(8))[0];
                Mask = await Reader.readexactly(4) if Masked else SOCKET_BREAK_EMPTY;
                Load = await Reader.readexactly(Payload);
                if Masked : Load = bytes(Byte ^ Mask[Index % 4] for Index , Byte in enumerate(Load));
                if Opcode in (1 , 2) :
                    try : Context.Signal.Request.Body = Json.loads(Body);
                    except :
                        Body = Load.decode();
                        Parser = Parse.parse_qs(Body , keep_blank_values = True);
                        if not len(Parser) == 0 :
                            for Key , Value in Parser.items() : Context.Signal.Request.Body[Key.strip()] = Value[0].strip() if len(Value) == 1 else Value;
                        else : Context.Signal.Request.Body = Body;
                    finally :
                        if Self.Check(Context , 'Limiting') is True : raise ValueError(429);
                        if Context.Config.Websocket.get('Journal') is True : Context.Journal.put(dict(
                            Method = 'Websocket' ,
                            Type = 'Request' ,
                            Body = Context.Signal ,
                        ));
                        Asyncio.create_task(Self.Task(Copy.deepcopy(Context.Signal) , Context.Journal , Writer));
                else : break;
        except ValueError as Error :
            try :
                Context.Signal.Response = dict(Code = Error.args[0]);
                await Self.Send(Context.Signal , Context.Journal , Writer);
            except : Function.Trace(Context.Journal);
        except : Function.Trace(Context.Journal);
    
    @staticmethod
    def Check(Context:Simple , Method:str) -> bool :
        Config = getattr(Context.Config , Method);
        if Config.get('Status') is False or callable(Config.get('Callable')) is False : return False;
        return Config.get('Callable')(Simple(
            Network = Context.Signal.Network ,
            Header = Context.Signal.Request.Header ,
        ));
    
    @classmethod
    async def Task(Self , Context:Simple , Journal:Processing.Queue , Writer:Asyncio.StreamWriter) -> None :
        try :
            Context.Response = await Asyncio.to_thread(Self.Business , Context);
            if Context.Method == 'Http' : await Self.Response(Context , Journal , Writer);
            else : await Self.Send(Context , Journal , Writer);
        except :
            try :
                Context.Response = dict(Code = 503);
                if Context.Method == 'Http' : await Self.Response(Context , Journal , Writer);
                else : await Self.Send(Context , Journal , Writer);
            except : pass;
            finally : Function.Trace(Journal);
    
    @staticmethod
    def Business(Context:Simple) -> dict :
        Response = Context.Config.get('Callable')(Simple(
            Network = Context.Network ,
            Request = Context.Request ,
        ));
        Source = dict(
            Code = 200 ,
            Body = str() ,
        );
        if isinstance(Response , dict) is True and 'Code' in Response and 'Body' in Response : Source.update(Response);
        else : Source['Body'] = Response;
        return Source;