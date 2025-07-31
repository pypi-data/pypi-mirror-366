from asyncio import Queue
import asyncio
from typing import Callable
try:
    import websockets
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install websockets')


class WBSer:
    def __init__(self):
        self.ws = None
        self.inq = Queue()
        self.outq = Queue()
        self.afuncs = []
        self.tasks = []
        self.is_start = False
    
    def add_atask(self, *afuncs:Callable[['WBSer'], None]):
        for afunc in afuncs:
            self.afuncs.append(afunc)
            if self.is_start: self.tasks.append(asyncio.create_task(afunc(self)))
    
    async def start(self, ws_url:str):
        self.ws = await websockets.connect(ws_url)
        self.tasks = [asyncio.create_task(func(self)) for func in self.afuncs]
        self.is_start = True
    
    async def close(self):
        try:
            await self.ws.close()
            [task.cancel() for task in self.tasks]
        except:
            pass
        self.tasks.clear()
        self.is_start=False