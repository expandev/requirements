from langgraph.graph import Graph
from core.proxies.agent_proxy import AgentProxy
from agents.definition.atena import AtenaSystem
from typing import Dict

class Supervisor:
    def __init__(self):
        self.agentes: Dict[str, AgentProxy] = {
            'analista_de_negocios': AtenaSystem()
        }
        self._workflow = self.build_workflow()
	
    async def router(self, tipo, context, *args, **kwargs):
        if tipo in self.agentes:
            # prepare_agent
            prepared_agent = self.prepare_agent(self.agentes[tipo], context)
            # call_agent
            resposta = await self.call_agent(prepared_agent, context)
            pass
        else:
            raise ValueError("Tipo de agente não suportado.")
        
        return resposta

    def prepare_agent(self, agente: AgentProxy, context) -> AgentProxy:
        # Lazy loading
        initialized_agent = agente.inicialize(demand_id=context['demand_id'], task=context['task'])
        return initialized_agent
	
    async def call_agent(self, agent: AgentProxy, context):
        # await agente.exec()
        result = agent.start_conversation(context)
        return result
    
    def build_workflow(self):
        workflow = Graph()
        
        workflow.add_node("router", self.router )
        workflow.add_node("collect_requirements", self.agentes['analista_de_negocios'].start_conversation)
        #workflow.add_node("especification_requirements", self.self.agentes['especificacao'])
        #workflow.add_node("analyze_requirements", self.self.agentes['analise'])
        
        workflow.add_edge("router", "collect_requirements")
        #workflow.add_edge("router", "especification_requirements")
        #workflow.add_edge("router", "analyze_requirements")
        
        workflow.set_entry_point("router")
        #workflow.get_graph().draw_mermaid_png()
        return workflow.compile()
    