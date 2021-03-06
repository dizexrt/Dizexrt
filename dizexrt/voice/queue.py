import asyncio
import itertools

class MusicQueue(asyncio.Queue):

    def __init__(self):
        super().__init__()
        self.current = None
        self._loop_current = False
        self._loop_all = False
        self._skip_loop = True
    
    async def get(self):
        if self._loop_all and self.current is not None:
            await self.put(self.current)

        if not self._loop_current or self.current is None:
            self.current = await super().get()
        
        return self.current
    
    def get_loop(self):
        return self._loop_current
    
    def get_loop_all(self):
        return self._loop_all

    @property
    def items(self):
        queue = list(itertools.islice(self._queue,0,self.qsize()))
        if len(queue) == 0:return None
        return queue

    async def delete(self, *index:int):
        for _ in range(self.qsize()):
            _source = self.get_nowait()
            if _ in index:
                continue
            self.put_nowait(_source)

    async def cleanup(self):
        for _ in range(self.qsize()):
            self.get_nowait()

    async def put(self, *sources):
        for item in sources:
            self.put_nowait(item)
    
    def loop_current(self):
        self._loop_current = not self._loop_current
        if self._loop_current:self._loop_all = False
        return self._loop_current
    
    def loop_all(self):
        self._loop_all = not self._loop_all
        if self._loop_all:self._loop_current = False
        return self._loop_all

    def skip_loop(self):
        if self._loop_all:return
        self.current = None
