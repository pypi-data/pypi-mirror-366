<p align="center">
    📦 <a href="https://pypi.org/project/Queus" style="text-decoration:none;">QUEUE</a>
</p>

<p align="center">
   <a href="https://telegram.me/Space_x_bots"><img src="https://img.shields.io/badge/Sᴘᴀᴄᴇ 𝕩 ʙᴏᴛꜱ-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
   <a href="https://telegram.me/clinton_abraham"><img src="https://img.shields.io/badge/Cʟɪɴᴛᴏɴ Aʙʀᴀʜᴀᴍ-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
   <a href="https://telegram.me/sources_codes"><img src="https://img.shields.io/badge/Sᴏᴜʀᴄᴇ ᴄᴏᴅᴇꜱ-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
</p>

## USAGE
<details>
    <summary>Installation</summary>

```bash
pip install queus
```
</details>

<details>
    <summary>Usage example</summary>

```python
import asyncio
from Queue.functions import Queue
from Queue.functions import Queues

async def runtask():
    print("Processing....")
    await asyncio.sleep(10)

async def main():
    await Queue.add("task01")
    await Queue.add("task02")
    await Queue.queue("task01", maximum=1)
    await runtask()

asyncio.run(main())
```
</details>
