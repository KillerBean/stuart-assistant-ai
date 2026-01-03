import asyncio
from stuart_ai.core.assistant import Assistant

async def main():
    assistant = Assistant()
    await assistant.listen_continuously()

if __name__ == "__main__":
    asyncio.run(main())