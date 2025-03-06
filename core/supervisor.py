from langgraph.graph import Graph
from core.proxies import AgentProxy
from agents.requirement_agent import RequirementAgent

class Supervisor:
    def __init__(self):
        self.agentes = {
            'coleta': RequirementAgent()
        }
        self._workflow = self.build_workflow()
	
    async def router(self, tipo, context, *args, **kwargs):
        if tipo in self.agentes:
            # prepare_agent
            # call_agent
            resposta = await self.call_agent(self.agentes[tipo], context)
            pass
        else:
            raise ValueError("Tipo de agente não suportado.")
        
        return resposta

    def prepare_agent(self, agente, context):
        # Lazy loading
        pass
	
    async def call_agent(self, agent: AgentProxy, context):
        # await agente.exec()
        result = agent.execute_task(context)
        return result
    
    def build_workflow(self):
        workflow = Graph()
        
        workflow.add_node("router", self.router )
        workflow.add_node("collect_requirements", self.agentes['coleta'].execute_task)
        #workflow.add_node("especification_requirements", self.self.agentes['especificacao'])
        #workflow.add_node("analyze_requirements", self.self.agentes['analise'])
        
        workflow.add_edge("router", "collect_requirements")
        #workflow.add_edge("router", "especification_requirements")
        #workflow.add_edge("router", "analyze_requirements")
        
        workflow.set_entry_point("router")
        return workflow.compile()
    