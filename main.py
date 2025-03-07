import asyncio
from core.supervisor import Supervisor
from tasks.definition.objective_understanding import ObjectiveUnderstanding

async def main():
    supervisor = Supervisor()

    resposta = await supervisor.router(
        tipo="analista_de_negocios", 
        context={
            'demand_id': '21',
            'task': ObjectiveUnderstanding
        }
    )
    print(resposta)
    pass

if __name__ == '__main__':
    asyncio.run(main())