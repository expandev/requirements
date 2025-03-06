import asyncio
from core.supervisor import Supervisor

async def main():
    supervisor = Supervisor()
    resposta = await supervisor.router("coleta", [])
    print(resposta)
    pass

if __name__ == '__main__':
    asyncio.run(main())