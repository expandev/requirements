from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import json
import logging
import os
import warnings
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union, Type
from pydantic import BaseModel, Field, field_validator, model_validator
from langchain_core.messages import AIMessage, BaseMessage
from core.enums.models import Models, MODEL_TO_PROVIDER, LLM_CONTEXT_WINDOW_SIZES, DEFAULT_CONTEXT_WINDOW_SIZE, CONTEXT_WINDOW_USAGE_RATIO
from core.enums.system import SystemState

"""
TaskProxy Module - Defines and manages task definitions in the Atena system.
"""
class TaskProxy(BaseModel):
    """
    Defines a task to be performed by an agent.
    """
    
    # Mandatory fields
    problems_to_solve: List[str] = Field(
        description="List of problems that the task should solve"
    )
    
    main_objective: str = Field(
        description="Main objective of the task"
    )
    
    expected_outcomes: str = Field(
        description="Expected outcomes and their rules"
    )
    
    language: str = Field(
        description="Language for execution"
    )
    
    expected_output: str = Field(
        description="Expected output format"
    )
    
    # Optional fields
    out_of_scope: List[str] = Field(
        default_factory=list,
        description="Items out of scope"
    )
    
    output_json: Optional[Type[BaseModel]] = Field(
        default=None,
        description="Model for structured output"
    )

    # Validators
    @field_validator('main_objective', 'expected_outcomes', 'language', 'expected_output')
    @classmethod
    def validate_non_empty(cls, v: str, field: str) -> str:
        """Validates that the field is not empty."""
        if not v or not v.strip():
            raise ValueError(f'{field.name} cannot be empty')
        return v.strip()

    def _format_json_schema(self) -> str:
        """Formats the JSON schema for display."""
        return (
            self.output_json.model_json_schema(indent=2)
            if self.output_json
            else "No JSON schema defined"
        )

    def format(self) -> str:
        """Formats the task definition into a structured string."""
        template = """
            ### TASK DEFINITION ###

            PROBLEMS TO SOLVE:
            {problems}

            MAIN OBJECTIVE:
            {main_objective}

            EXPECTED OUTCOMES:
            {expected_outcomes}

            LANGUAGE: {language}
            EXPECTED OUTPUT: {expected_output}

            {optional_fields}
        """
        # Formats optional fields if they exist
        optional_fields = []
        
        if self.out_of_scope:
            optional_fields.append("OUT OF SCOPE:\n" + 
                "\n".join(f"- {item}" for item in self.out_of_scope))
            
        if self.output_json:
            optional_fields.append("OUTPUT JSON SCHEMA:\n" + self._format_json_schema())
            
        return template.format(
            problems="\n".join(f"- {p}" for p in self.problems_to_solve),
            main_objective=self.main_objective,
            expected_outcomes=self.expected_outcomes,
            language=self.language,
            expected_output=self.expected_output,
            optional_fields="\n\n".join(optional_fields) if optional_fields else ""
        )

    def is_complete(self) -> bool:
        """Checks if the task has all mandatory fields filled."""
        return bool(
            self.problems_to_solve and
            self.main_objective and
            self.expected_outcomes and
            self.language and
            self.expected_output
        )
