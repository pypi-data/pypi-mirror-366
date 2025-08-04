import asyncio
from .function02 import Queues
from ..exceptions import QueuedAlready
#================================================================================================

class Queue:

    def __init__(self, **kwargs):
        self.waiting = kwargs.get("wait", 1)
        self.maximum = kwargs.get("maximum", 1)
        self.storage = kwargs.get("storage", Queues)

#================================================================================================

    async def total(self):
        return len(self.storage)

    async def add(self, uid, priority=-1):
        if uid in self.storage: raise QueuedAlready()
        self.storage.append(uid) if priority == -1 else self.storage.insert(priority, uid)

#================================================================================================

    async def message(self, imog, text, button=None):
        if len(self.storage) >= self.maximum:
            try: await imog.edit(text=text, reply_markup=button)
            except Exception: pass

#================================================================================================
    
    async def remove(self, uid):
        self.storage.remove(uid) if uid in self.storage else 0

    async def position(self, uid):
        return self.storage.index(uid) - self.maximum + 1 if uid in self.storage else 0

#================================================================================================

    async def queue(self, uid):
        while uid in self.storage:
            if self.storage.index(uid) >= self.maximum: await asyncio.sleep(self.waiting)
            else: break

#================================================================================================
