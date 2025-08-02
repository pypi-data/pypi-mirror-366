import asyncio
from ..exceptions import QueuedAlready
#======================================================================================

Queues = []

class Queue:

    @staticmethod
    async def add(uid, priority=-1, storage=Queues):
        if uid in storage:
            raise QueuedAlready("Task already in queue")
    
        if priority > -1:
            storage.insert(priority, uid)
        else:
            storage.append(uid)


#======================================================================================

    @staticmethod
    async def delete(uid, storage=Queues):
        storage.remove(uid) if uid in storage else 0

    @staticmethod
    async def position(uid, storage=Queues):
        return storage.index(uid) if uid in storage else 0

#======================================================================================

    @staticmethod
    async def queue(uid, wait=1, maximum=1, storage=Queues):
        while uid in storage:
            if storage.index(uid) > maximum:
                await asyncio.sleep(wait)
            else:
                break

#======================================================================================

    @staticmethod
    async def message(imog, text, button=None, maximum=1, storage=Queues):
        if maximum < len(storage):
            try: await imog.edit(text=text, reply_markup=button)
            except Exception: pass

#======================================================================================
