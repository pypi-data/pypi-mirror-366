from . import Common;
from .Http import Http;
from .Journal import Journal;
from .Resource import Resource;
from .Websocket import Websocket;

def Lunch(Source:dict = dict()) -> None :
    try :
        Context = Common.Simple(
            Config = Common.Function.Configure(Source) ,
            Journal = Common.Processing.Queue() ,
        );
        Common.Function.Proctitle('Main');
        Process:list[Common.Processing.Process] = list();
        if Context.Config.Http.get('Status') is True : Process.append(Common.Processing.Process(target = Http.Lunch , args = (Context , )));
        if Context.Config.Websocket.get('Status') is True : Process.append(Common.Processing.Process(target = Websocket.Lunch , args = (Context , )));
        if len(Process) == 0 : Common.Function.Log('Http Or Websocket Must Have One Enabled');
        else :
            if Context.Config.Resource.get('Status') is True : Process.append(Common.Processing.Process(target = Resource.Lunch , args = (Context , )));
            Process.append(Common.Processing.Process(target = Journal.Lunch , args = (Context , )));
        for X in Process : X.start();
        for X in Process : X.join();
    except : Common.Function.Trace();