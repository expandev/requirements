from abc import ABC, abstractmethod
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator
import json
import logging
import os
import warnings
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union, Type
from pydantic import BaseModel, Field, field_validator, model_validator
from core.enums.system import SystemState
from langchain_core.messages import AIMessage, BaseMessage
from core.enums.models import Models, MODEL_TO_PROVIDER, LLM_CONTEXT_WINDOW_SIZES, DEFAULT_CONTEXT_WINDOW_SIZE, CONTEXT_WINDOW_USAGE_RATIO    
from core.proxies.task_proxy import TaskProxy

"""
AgentModel Module (AgentDefinition) - Defines and manages agent profiles in the Atena system.

This module provides the structure to define agents and their attributes,
including roles, objectives, and operational contexts.
"""
class AgentModel(BaseModel):
    """
    Defines the profile and characteristics of an agent.
    """
    # Basic fields
    name: Optional[str] = Field(
        default=None,
        description="Agent's identifier name"
    )
    
    # Section 4: Agent Configuration
    # 4.1 Role
    role: str = Field(
        default=None,
        description="Agent's role/title"
    )
    
    field_of_work: str = Field(
        default=None,
        description="Agent's field of work"
    )
    
    expertise_level: str = Field(
        default=None,
        description="Agent's expertise level"
    )
    
    professional_background: str = Field(
        default=None,
        description="Agent's professional background"
    )
    
    # 4.2 Skills
    technical_skills: List[str] = Field(
        default_factory=list,
        description="List of the agent's technical skills"
    )
    
    resources: List[str] = Field(
        default_factory=list,
        description="List of resources available to the agent"
    )
    
    # 4.3 Behavior
    communication_approach: str = Field(
        default="",
        description="Agent's communication approach"
    )
    
    response_style: str = Field(
        default="",
        description="Agent's response style"
    )
    
    proactivity_level: str = Field(
        default="",
        description="Agent's proactivity level"
    )
    
    autonomy: str = Field(
        default="",
        description="Agent's autonomy level"
    )

    state: SystemState = Field(
        default=None,
        description="Agent's current state"
    )

    user: str = Field(
        default=None,
        description="Agent's user"
    )

    agent: Any = Field(
        default=None,
        description="Agent's profile"
    )

    task: TaskProxy = Field(
        default=None,
        description="Agent's task"
    )

    database: Any = Field(
        default=None,
        description="Agent's database"
    )

    @field_validator('role', 'field_of_work', 'expertise_level', 'professional_background')
    @classmethod
    def validate_not_empty(cls, v: str, field: str) -> str:
        """Validates that mandatory fields are not empty."""
        if not v or not v.strip():
            raise ValueError(f'{field.name} cannot be empty')
        return v.strip()

    def format(self) -> str:
        """Formats the agent definition into a structured string."""
        template = """
            ### AGENT PROFILE ###
            NAME: {name}

            ROLE CONFIGURATION:
            - Role Title: {role}
            - Field of Work: {field_of_work}
            - Expertise Level: {expertise_level}
            - Professional Background: {professional_background}

            TECHNICAL SKILLS:
            {skills}

            RESOURCES:
            {resources}

            BEHAVIOR CONFIGURATION:
            - Communication Approach: {communication_approach}
            - Response Style: {response_style}
            - Proactivity Level: {proactivity_level}
            - Autonomy: {autonomy}
        """
        
        return template.format(
            name=self.name or 'Unnamed Agent',
            role=self.role,
            field_of_work=self.field_of_work,
            expertise_level=self.expertise_level,
            professional_background=self.professional_background,
            skills="\n".join(f"- {s}" for s in self.technical_skills),
            resources="\n".join(f"- {r}" for r in self.resources),
            communication_approach=self.communication_approach,
            response_style=self.response_style,
            proactivity_level=self.proactivity_level,
            autonomy=self.autonomy
        )

    @property
    def display_name(self) -> str:
        """Returns the agent's display name."""
        return self.name or 'Unnamed Agent'

    def set_name(self, name: str) -> None:
        """Sets the agent's name."""
        self.name = name.strip()

    def clone(self) -> 'AgentModel':
        """Creates a copy of the agent."""
        return AgentModel(
            name=self.name,
            role=self.role,
            field_of_work=self.field_of_work,
            expertise_level=self.expertise_level,
            professional_background=self.professional_background,
            technical_skills=self.technical_skills.copy(),
            resources=self.resources.copy(),
            communication_approach=self.communication_approach,
            response_style=self.response_style,
            proactivity_level=self.proactivity_level,
            autonomy=self.autonomy
        )

    def is_complete(self) -> bool:
        """Checks if the agent has all mandatory fields filled."""
        return bool(
            self.role and 
            self.field_of_work and 
            self.expertise_level and 
            self.professional_background
        )

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"Agent({self.display_name})"

    def __repr__(self) -> str:
        """Detailed representation of the agent."""
        return f"AgentModel(name='{self.name}', role='{self.role}')"

    def dict_representation(self) -> dict:
        """Creates a dictionary representation of the agent."""
        return {
            "name": self.display_name,
            "role": self.role,
            "field_of_work": self.field_of_work,
            "expertise_level": self.expertise_level,
            "professional_background": self.professional_background,
            "technical_skills": self.technical_skills,
            "resources": self.resources,
            "communication_approach": self.communication_approach,
            "response_style": self.response_style,
            "proactivity_level": self.proactivity_level,
            "autonomy": self.autonomy
        }
    
    def execute_task(self, input_data):
        """Executes a task based on the input data"""
        """TODO - Revisar e adicionar a definição de tipos"""
        #prompt = self.prompt_strategy.generate_prompt(input_data)
        #response = self.llm.call_model(prompt)
        #self._validate(response)
        #return "Hello World!"
        return self._agent.execute_task(input_data)
        pass
        
    def _validate(self, output):
        """Validates the agent's output and corrects errors if necessary."""
        """TODO - Revisar e adicionar a definição de tipos"""
        # Lógica de autocorreção
        #if not self._check_quality(output):
        #    self._correct_errors(output)
        pass
	
    def _check_quality(output):
        """Checks the quality of the agent's output."""
        """TODO - Revisar e adicionar a definição de tipos"""
        #return all([
            #self._check_completeness(agent_output),
            #self._check_ambiguity(agent_output),
            #self._check_consistency(agent_output)
        #])
        pass
