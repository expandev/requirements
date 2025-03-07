"""
Module for reading and processing configurations in Markdown format.

This module implements classes to manage agent and task configurations
defined in structured Markdown files, providing a clean interface to
access these data in other parts of the system.
"""

import re
import os
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

default_knowledge_base_path = 'knowledge_base/definition'

class MarkdownParserUtils:
    """
    Utility class for parsing Markdown files.
    
    Provides static methods to extract and process data from structured Markdown
    files, including sections, values, and selected options.
    """
    
    @staticmethod
    def find_section(content: str, section_name: str) -> str:
        """
        Finds a specific section in the Markdown content.
        
        Args:
            content: Complete Markdown content for parsing.
            section_name: Name of the section to locate.
            
        Returns:
            str: Content of the found section or an empty string if not found.
        """
        try:
            # First try to find as a section title with **
            pattern = f"\\*\\*{re.escape(section_name)}\\*\\*.*?(?=\\*\\*|$)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(0)
                
            # If not found, try as a header
            pattern = f"### {re.escape(section_name)}.*?(?=###|$)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(0)
                
            return ""
        except Exception as e:
            logger.error(f"Error searching for section {section_name}: {str(e)}")
            return ""

    @staticmethod
    def extract_between_backticks(text: str) -> str:
        """
        Extracts content between backticks (```).
        
        Args:
            text: Text that potentially contains content between backticks.
            
        Returns:
            str: Content between backticks or an empty string if not found.
        """
        try:
            if not text:
                return ""
                
            match = re.search(r'```(.*?)```', text, re.DOTALL)
            if match:
                return match.group(1).strip()
            return ""
        except Exception as e:
            logger.error(f"Error extracting content between backticks: {str(e)}")
            return ""

    @staticmethod
    def extract_selected_checkbox_value(section: str) -> str:
        """
        Extracts the value of a selected checkbox [X] in a section.
        
        Args:
            section: Section content potentially containing a checked checkbox.
            
        Returns:
            str: Value of the selected checkbox or an empty string if not found.
        """
        try:
            if not section:
                return ""
                
            # Look for line with [X] or [x]
            for line in section.split('\n'):
                if '[X]' in line or '[x]' in line:
                    # Extract the text after the checkbox
                    match = re.search(r'- \[[Xx]\] ([^:\n]+)', line)
                    if match:
                        return match.group(1).strip()
            return ""
        except Exception as e:
            logger.error(f"Error extracting checkbox value: {str(e)}")
            return ""

    @staticmethod
    def section_exists(content: str, section_name: str) -> bool:
        """
        Checks if a section exists in the content.
        
        Args:
            content: Complete Markdown content.
            section_name: Name of the section to check.
            
        Returns:
            bool: True if the section exists, False otherwise.
        """
        try:
            return bool(re.search(f"\\*\\*{re.escape(section_name)}\\*\\*|### {re.escape(section_name)}", content))
        except Exception:
            return False
            
    @staticmethod
    def find_section_between_headers(content: str, start_header: str, end_header: str) -> str:
        """
        Finds content between two markdown headers.
        
        Args:
            content: Complete Markdown content.
            start_header: Starting header.
            end_header: Ending header.
            
        Returns:
            str: Content between the headers or an empty string if not found.
        """
        try:
            # Escape special characters in headers
            start_header = re.escape(start_header)
            end_header = re.escape(end_header)
            
            # Pattern that captures all content between the headers
            pattern = f"({start_header}.*?)(?={end_header}|$)"
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                return match.group(1)
            return ""
        except Exception as e:
            logger.error(f"Error searching for section between headers: {str(e)}")
            return ""

    @staticmethod
    def get_selected_option(content: str, section_name: str) -> str:
        """
        Extracts the option marked with [X] from a section, including its description.
        
        Args:
            content: Complete Markdown content.
            section_name: Name of the section containing the options.
            
        Returns:
            str: Selected option with description or an empty string if not found.
        """
        try:
            section = MarkdownParserUtils.find_section(content, section_name)
            if not section:
                return ""
            
            # Look for line with [X] or [x]
            for line in section.split('\n'):
                if '[X]' in line or '[x]' in line:
                    # First try to extract with the complete description
                    match = re.search(r'- \[[Xx]\] ([^:]+):\s*(.+)', line)
                    if match:
                        option = match.group(1).strip()
                        description = match.group(2).strip()
                        return f"{option}: {description}"
                    
                    # If no description found, return just the option
                    match = re.search(r'- \[[Xx]\] ([^:]+)', line)
                    if match:
                        return match.group(1).strip()
            return ""
        except Exception as e:
            logger.error(f"Error extracting selected option from {section_name}: {str(e)}")
            return ""
    
    @staticmethod
    def safe_extract_value(section_name: str, content: str) -> str:
        """
        Extracts the value from a section with error handling and support for multiple formats.
        
        First tries to extract value between backticks, then tries to find
        a selected checkbox.
        
        Args:
            section_name: Name of the section.
            content: Complete Markdown content.
            
        Returns:
            str: Extracted value or an empty string if not found.
        """
        try:
            section_content = MarkdownParserUtils.find_section(content, section_name)
            if not section_content:
                return ""
                
            # First try to extract from backticks
            value = MarkdownParserUtils.extract_between_backticks(section_content)
            if value:
                return value
            
            # If not found, try to extract from checkbox
            value = MarkdownParserUtils.extract_selected_checkbox_value(section_content)
            return value
        except Exception as e:
            logger.error(f"Error extracting {section_name}: {str(e)}")
            return ""


class KnowledgeBaseLoader:
    """
    Class responsible for loading knowledge base files in Markdown format.
    
    Manages the location, loading, and processing of Markdown files
    used as a knowledge base for tasks.
    """
    
    def __init__(self, knowledge_base_path: str = default_knowledge_base_path):
        """
        Initializes the loader with the base path for the files.
        
        Args:
            knowledge_base_path: Path to the directory of knowledge files.
        """
        self.knowledge_base_path = knowledge_base_path
    
    def load_md_files(self, knowledge_base_files: List[str]) -> Dict[str, str]:
        """
        Loads the specified Markdown files from the knowledge base.
        
        Args:
            knowledge_base_files: List of knowledge base file names.
            
        Returns:
            Dict: Dictionary with the contents of the loaded markdown files.
        """
        md_contents = {}
        
        for file_name in knowledge_base_files:
            if not file_name or file_name.strip() == '':
                continue
                
            # Remove numbers and spaces from the beginning of the file name
            clean_name = file_name.strip()
            # Remove numbering from the start (e.g., "1.file.md" -> "file.md")
            clean_name = re.sub(r'^\d+\.', '', clean_name)
            
            # Get only the base name of the file without the extension
            base_name = os.path.splitext(os.path.basename(clean_name))[0]
            
            # Check if the file has an extension
            has_extension = '.' in clean_name
            
            # List of paths to try
            paths_to_try = [
                os.path.join(self.knowledge_base_path, clean_name)
            ]
            
            # Add extension attempts if not present
            if not has_extension:
                paths_to_try.extend([
                    os.path.join(self.knowledge_base_path, f"{clean_name}.md"),
                    os.path.join(self.knowledge_base_path, f"{clean_name}.markdown")
                ])
            
            # Try each possible path
            md_loaded = False
            for file_path in paths_to_try:
                try:
                    with open(file_path, 'r', encoding='utf8') as file:
                        content = file.read()
                        md_contents[base_name] = content
                        logger.info(f"Markdown file loaded successfully: {file_path}")
                        md_loaded = True
                        break  # Exit loop if loaded successfully
                except FileNotFoundError:
                    continue  # Try the next path
                except Exception as e:
                    logger.error(f"Error loading Markdown file {file_path}: {str(e)}")
                    break  # Do not try further if there is an error
            
            if not md_loaded:
                logger.warning(f"Could not load file: {file_name}")
                
        return md_contents


class LLMConfig:
    """
    Class to store language model configuration for a task.
    
    Maintains data about the model, temperature, and other LLM settings
    without knowing the source of these data.
    """
    
    def __init__(self):
        """Initializes with default values."""
        self.model = ""
        self.temperature = 0.5
        self.max_tokens = None


class TaskConfig:
    """
    Class to store configuration for a task.
    
    Maintains all data related to a specific task, including
    its objective, description, language, expected outputs, and LLM settings.
    """
    
    def __init__(self, kb_loader: KnowledgeBaseLoader):
        """
        Initializes the task configuration.
        
        Args:
            kb_loader: Instance of the knowledge base loader.
        """
        self.name = ""
        self.main_objective = ""
        self.description = ""
        self.language = ""
        self.expected_output = ""
        self.output_json = None
        self.knowledge_base = []  # List of knowledge base files.
        self.knowledge_contents = {}  # Contents of the loaded files.
        self.tools = []
        self.out_of_scope = []  # List of out-of-scope items.
        self.llm_config = LLMConfig()
        self.kb_loader = kb_loader
        
    def load_from_markdown(self, task_section: str, task_num: int):
        """
        Loads task configuration from a markdown section.
        
        Args:
            task_section: Markdown content of the task section.
            task_num: Task number for reference.
        """
        try:
            # Set default name for the task
            self.name = f"Task {task_num}"
            
            # Extract main objective
            main_objective = MarkdownParserUtils.extract_between_backticks(
                MarkdownParserUtils.find_section(task_section, "Main Objective")
            )
            if main_objective:
                self.main_objective = main_objective
                logger.info(f"Task {task_num} objective loaded: {main_objective[:30]}...")
            
            # Extract outcomes and description
            outcomes = self._get_task_outcomes(task_section)
            if outcomes:
                self.description = outcomes
            
            # Basic task settings
            language_text = MarkdownParserUtils.extract_between_backticks(
                MarkdownParserUtils.find_section(task_section, "Language")
            )
            if language_text:
                self.language = language_text
            
            output_text = MarkdownParserUtils.extract_between_backticks(
                MarkdownParserUtils.find_section(task_section, "Expected Output")
            )
            if output_text:
                self.expected_output = output_text
            
            json_text = MarkdownParserUtils.extract_between_backticks(
                MarkdownParserUtils.find_section(task_section, "Output Json")
            )
            if json_text:
                self.output_json = json_text
            
            # Out of Scope
            out_of_scope_section = MarkdownParserUtils.find_section(task_section, "Out of Scope")
            if out_of_scope_section:
                out_of_scope_text = MarkdownParserUtils.extract_between_backticks(out_of_scope_section)
                if out_of_scope_text:
                    self.out_of_scope = [
                        item.strip()
                        for item in out_of_scope_text.split('\n')
                        if item.strip() and not item.startswith('#')
                    ]
                    logger.info(f"Out-of-scope items for Task {task_num}: {len(self.out_of_scope)}")
            
            # Knowledge Base
            kb_section = MarkdownParserUtils.find_section(task_section, "Knowledge Base")
            if kb_section:
                kb_text = MarkdownParserUtils.extract_between_backticks(kb_section)
                if kb_text:
                    self.knowledge_base = [
                        kb.strip()
                        for kb in kb_text.split('\n')
                        if kb.strip() and not kb.startswith('#')
                    ]
                    logger.info(f"Knowledge Base for Task {task_num}: {', '.join(self.knowledge_base) if self.knowledge_base else 'None'}")
            
            # Tools
            tools_section = MarkdownParserUtils.find_section(task_section, "Tools")
            if tools_section:
                tools = MarkdownParserUtils.extract_between_backticks(tools_section)
                if tools:
                    self.tools = [
                        tool.strip()
                        for tool in tools.split('\n')
                        if tool.strip() and not tool.startswith('#')
                    ]
                    logger.info(f"Tools for Task {task_num}: {', '.join(self.tools) if self.tools else 'None'}")
            
            # LLM configs
            llm_section = MarkdownParserUtils.find_section_between_headers(
                task_section, 
                f"#### 3.{task_num}.1", 
                f"#### 3.{task_num}.2" if MarkdownParserUtils.section_exists(task_section, f"#### 3.{task_num}.2") else "## Section 4:"
            )
            
            if llm_section:
                # LLM Model - supports traditional format and checkbox
                model_section = MarkdownParserUtils.find_section(llm_section, "LLM Model")
                
                # Try to find the model (first in backticks, then in checkbox)
                model = MarkdownParserUtils.safe_extract_value("LLM Model", llm_section)
                if model:
                    self.llm_config.model = model.strip()
                    logger.info(f"LLM model loaded for Task {task_num}: {self.llm_config.model}")
                
                # Temperature
                temp_section = MarkdownParserUtils.find_section(llm_section, "LLM Temperature")
                if temp_section:
                    if "[X] 0.1" in temp_section or "[x] 0.1" in temp_section:
                        self.llm_config.temperature = 0.1
                    elif "[X] 0.9" in temp_section or "[x] 0.9" in temp_section:
                        self.llm_config.temperature = 0.9
                    else:
                        self.llm_config.temperature = 0.5
                
                # Max tokens
                max_tokens_text = MarkdownParserUtils.extract_between_backticks(
                    MarkdownParserUtils.find_section(llm_section, "LLM Max Tokens")
                )
                
                if max_tokens_text and max_tokens_text.strip() and not max_tokens_text.startswith('[') and max_tokens_text.isdigit():
                    self.llm_config.max_tokens = int(max_tokens_text)
            
            # Load Markdown files if there is a knowledge base
            if self.knowledge_base:
                self.knowledge_contents = self.kb_loader.load_md_files(self.knowledge_base)
                logger.info(f"Markdown files loaded for Task {task_num}: {list(self.knowledge_contents.keys())}")
                
        except Exception as e:
            logger.error(f"Error loading configuration for Task {task_num}: {str(e)}")
            logger.exception("Error details:")
    
    def _get_task_outcomes(self, content: str) -> str:
        """
        Extracts the outcomes of a specific task.
        
        Args:
            content: Markdown content of the task section.
            
        Returns:
            str: Formatted outcomes or an empty string if not found.
        """
        try:
            outcomes_section = MarkdownParserUtils.find_section(content, "Expected Outcomes")
            if not outcomes_section:
                return ""

            outcomes_text = MarkdownParserUtils.extract_between_backticks(outcomes_section)
            if not outcomes_text:
                return ""

            outcomes = []
            current_outcome = []
            outcome_number = 1
            
            lines = outcomes_text.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Check if it's a new outcome
                if line.startswith(f"{outcome_number}.") and "outcome:" in line:
                    # If we already have content, save the previous outcome
                    if current_outcome:
                        outcomes.append('\n'.join(current_outcome))
                        current_outcome = []
                    
                    # Start the new outcome
                    current_outcome.append(line)
                    outcome_number += 1
                elif current_outcome:  # If an outcome is being processed
                    current_outcome.append(line)
                
                i += 1
                
            # Add the last outcome
            if current_outcome:
                outcomes.append('\n'.join(current_outcome))
                
            return '\n\n'.join(outcomes)
            
        except Exception as e:
            logger.error(f"Error extracting task outcomes: {str(e)}")
            return ""
    
    def get_formatted_description(self) -> str:
        """
        Returns the formatted description with the knowledge base contents.
        
        Returns:
            str: Formatted description with replaced contents.
        """
        formatted_description = self.description
        
        # Replace references to the Markdown files with their contents
        for var_name, var_content in self.knowledge_contents.items():
            placeholder = "{" + var_name + "}"
            if placeholder in formatted_description:
                # The content is already a string, but ensure it is a string
                var_content_str = str(var_content)
                formatted_description = formatted_description.replace(placeholder, var_content_str)
                
        return formatted_description


class AgentConfig:
    """
    Class to store agent configuration.
    
    Maintains all data related to the agent, including basic information,
    communication settings, skills, etc.
    """
    
    def __init__(self):
        """Initializes with empty values."""
        # Agent info
        self.agent_name = ""
        self.form_name = ""
        self.creation_date = ""
        self.responsible = ""
        self.version = ""
        self.interaction_type = ""
        
        # Agent configuration
        self.role = ""
        self.field_of_work = ""
        self.expertise_level = ""
        self.professional_background = ""
        self.technical_skills = []
        self.resources = []
        
        # Communication settings
        self.communication_approach = ""
        self.response_style = ""
        self.proactivity_level = ""
        self.autonomy = ""
        
        # Problems
        self.problems = []
    
    def load_from_markdown(self, content: str):
        """
        Loads agent configuration from Markdown content.
        
        Args:
            content: Complete Markdown content.
        """
        try:
            # Load basic information
            self._load_agent_info(content)
            
            # Load problems
            self._load_problems(content)
            
            # Load configurations
            self._load_agent_config(content)
            
            logger.info(f"Agent configuration loaded successfully: {self.agent_name}")
            
        except Exception as e:
            logger.error(f"Error loading agent configuration: {str(e)}")
            logger.exception("Error details:")
    
    def _load_agent_info(self, content: str):
        """
        Loads basic agent information.
        
        Args:
            content: Complete Markdown content.
        """
        try:
            # Section 1 info
            section1 = MarkdownParserUtils.find_section_between_headers(content, "## Section 1:", "## Section 2:")
            if section1:
                # Extract basic fields
                self.agent_name = MarkdownParserUtils.safe_extract_value("Agent Name", section1)
                self.creation_date = MarkdownParserUtils.safe_extract_value("Creation Date", section1)
                self.responsible = MarkdownParserUtils.safe_extract_value("Responsible", section1)
                self.version = MarkdownParserUtils.safe_extract_value("Version", section1)
            
            # Extract interaction type with complete description
            interaction_section = MarkdownParserUtils.find_section(content, "Interaction Type")
            if interaction_section:
                for line in interaction_section.split('\n'):
                    if '[X]' in line or '[x]' in line:
                        match = re.search(r'- \[[Xx]\] ([^:]+):\s*(.+)', line)
                        if match:
                            type_name = match.group(1).strip()
                            type_desc = match.group(2).strip()
                            self.interaction_type = f"{type_name}: {type_desc}"
                            break

            logger.info(f"Agent name loaded: {self.agent_name}")
        except Exception as e:
            logger.error(f"Error loading agent information: {str(e)}")
            logger.exception("Error details:")
    
    def _load_problems(self, content: str):
        """
        Loads the list of problems.
        
        Args:
            content: Complete Markdown content.
        """
        try:
            problems_section = MarkdownParserUtils.find_section(content, "Problems to be Solved")
            if problems_section:
                problems_text = MarkdownParserUtils.extract_between_backticks(problems_section)
                if problems_text:
                    self.problems = [
                        prob.strip()
                        for prob in problems_text.split('\n')
                        if prob.strip() and not prob.startswith('#')
                    ]
                    logger.info(f"Loaded {len(self.problems)} problems")
        except Exception as e:
            logger.error(f"Error loading problems: {str(e)}")
    
    def _load_agent_config(self, content: str):
        """
        Loads agent configurations.
        
        Args:
            content: Complete Markdown content.
        """
        try:
            # Load configurations from Section 4
            section4 = MarkdownParserUtils.find_section_between_headers(content, "## Section 4:", "## Section 5:")
            if not section4:
                section4 = MarkdownParserUtils.find_section_between_headers(content, "## Section 4:", "$")  # If Section 5 is not present
            
            if section4:
                # Role info
                role_section = MarkdownParserUtils.find_section(section4, "Role Title")
                if role_section:
                    self.role = MarkdownParserUtils.extract_between_backticks(role_section)
                
                field_section = MarkdownParserUtils.find_section(section4, "Field of Work")
                if field_section:
                    self.field_of_work = MarkdownParserUtils.extract_between_backticks(field_section)
                
                background_section = MarkdownParserUtils.find_section(section4, "Professional Background")
                if background_section:
                    self.professional_background = MarkdownParserUtils.extract_between_backticks(background_section)
                
                # Expertise level with description
                expertise_section = MarkdownParserUtils.find_section(section4, "Expertise Level")
                if expertise_section:
                    for line in expertise_section.split('\n'):
                        if '[X]' in line or '[x]' in line:
                            match = re.search(r'- \[[Xx]\] ([^:]+):\s*(.+)', line)
                            if match:
                                level = match.group(1).strip()
                                desc = match.group(2).strip()
                                self.expertise_level = f"{level}: {desc}"
                                break
                
                # Skills and resources
                skills_section = MarkdownParserUtils.find_section(section4, "Required Technical Skills")
                if skills_section:
                    skills = MarkdownParserUtils.extract_between_backticks(skills_section)
                    if skills:
                        self.technical_skills = [
                            skill.strip()
                            for skill in skills.split('\n')
                            if skill.strip() and not skill.startswith('#')
                        ]
                
                resources_section = MarkdownParserUtils.find_section(section4, "Resources")
                if resources_section:
                    resources = MarkdownParserUtils.extract_between_backticks(resources_section)
                    if resources:
                        self.resources = [
                            resource.strip()
                            for resource in resources.split('\n')
                            if resource.strip() and not resource.startswith('#')
                        ]
                
                # Communication settings with complete descriptions
                self.communication_approach = MarkdownParserUtils.get_selected_option(section4, "Communication Approach")
                self.response_style = MarkdownParserUtils.get_selected_option(section4, "Response Style")
                self.proactivity_level = MarkdownParserUtils.get_selected_option(section4, "Proactivity Level")
                self.autonomy = MarkdownParserUtils.get_selected_option(section4, "Autonomy")
                
                logger.info(f"Agent config loaded: {self.role}")
            
        except Exception as e:
            logger.error(f"Error loading agent configurations: {str(e)}")
            logger.exception("Error details:")


class ExpandevConfigProvider:
    """
    Main class responsible for managing the configuration.
    
    Manages access to all agent and task configurations,
    including initial loading, automatic updates, and access via properties.
    """
    
    def __init__(self, md_file_path: str, knowledge_base_path: str = default_knowledge_base_path):
        """
        Initializes the configuration provider.
        
        Args:
            md_file_path: Path to the configuration markdown file.
            knowledge_base_path: Path to the folder containing knowledge base files.
        """
        self.md_file_path = Path(md_file_path)
        self.knowledge_base_path = knowledge_base_path
        self.last_modified = 0
        
        # Initialize components
        self.kb_loader = KnowledgeBaseLoader(knowledge_base_path)
        self.agent_config = AgentConfig()
        self.tasks: Dict[str, TaskConfig] = {}
        
        # Load initial configuration
        self._load_config()
        
        # Setup file observer
        self._setup_watcher()
        
    # Properties to maintain compatibility with existing code
    @property
    def agent_name(self) -> str:
        """Agent name"""
        return self.agent_config.agent_name
        
    @property
    def role(self) -> str:
        """Agent role/function"""
        return self.agent_config.role
        
    @property
    def form_name(self) -> str:
        """Form name"""
        return self.agent_config.form_name
        
    @property
    def creation_date(self) -> str:
        """Creation date"""
        return self.agent_config.creation_date
        
    @property
    def responsible(self) -> str:
        """Responsible person"""
        return self.agent_config.responsible
        
    @property
    def version(self) -> str:
        """Version"""
        return self.agent_config.version
        
    @property
    def interaction_type(self) -> str:
        """Interaction type"""
        return self.agent_config.interaction_type
        
    @property
    def field_of_work(self) -> str:
        """Field of work"""
        return self.agent_config.field_of_work
        
    @property
    def expertise_level(self) -> str:
        """Expertise level"""
        return self.agent_config.expertise_level
        
    @property
    def professional_background(self) -> str:
        """Professional background"""
        return self.agent_config.professional_background
        
    @property
    def technical_skills(self) -> List[str]:
        """Technical skills"""
        return self.agent_config.technical_skills
        
    @property
    def resources(self) -> List[str]:
        """Available resources"""
        return self.agent_config.resources
        
    @property
    def communication_approach(self) -> str:
        """Communication approach"""
        return self.agent_config.communication_approach
        
    @property
    def response_style(self) -> str:
        """Response style"""
        return self.agent_config.response_style
        
    @property
    def proactivity_level(self) -> str:
        """Proactivity level"""
        return self.agent_config.proactivity_level
        
    @property
    def autonomy(self) -> str:
        """Autonomy level"""
        return self.agent_config.autonomy
        
    @property
    def problems(self) -> List[str]:
        """Problems to be solved"""
        return self.agent_config.problems

    def _load_config(self) -> None:
        """
        Loads and parses the MD file.
        
        Reads the configuration Markdown file, extracts all data,
        and configures the AgentConfig and TaskConfig instances.
        """
        try:
            current_mtime = self.md_file_path.stat().st_mtime
            if current_mtime <= self.last_modified:
                return

            logger.info(f"Loading configuration from file: {self.md_file_path}")
            
            with open(self.md_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            self.last_modified = current_mtime
            
            # Load agent information
            self.agent_config.load_from_markdown(content)
            
            # Load task configurations
            self._load_tasks_config(content)
            
            logger.info("Configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            logger.exception("Error details:")

    def _load_tasks_config(self, content: str) -> None:
        """
        Loads task configurations.
        
        Args:
            content: Complete Markdown content.
        """
        try:
            # Find the Tasks section (Section 3)
            tasks_section = MarkdownParserUtils.find_section_between_headers(content, "## Section 3:", "## Section 4:")
            if not tasks_section:
                return

            for task_num in range(1, 10):  # Support up to Task9
                task_prefix = f"Task{task_num}"
                
                # Find the specific task section
                task_section = MarkdownParserUtils.find_section_between_headers(
                    tasks_section, 
                    f"### 3.{task_num}", 
                    f"### 3.{task_num + 1}" if task_num < 9 else "## Section 4:"
                )
                
                if not task_section:
                    continue
                
                # Create a new task and load it
                task_config = TaskConfig(self.kb_loader)
                task_config.load_from_markdown(task_section, task_num)
                
                self.tasks[task_prefix] = task_config
                logger.info(f"{task_prefix} configuration loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading tasks configuration: {str(e)}")
            logger.exception("Error details:")

    def _setup_watcher(self) -> None:
        """
        Sets up the file observer.
        
        Uses watchdog to monitor changes in the configuration file
        and automatically reload when it is modified.
        """
        class MDHandler(FileSystemEventHandler):
            def __init__(self, config_provider):
                self.config_provider = config_provider

            def on_modified(self, event):
                if event.src_path == str(self.config_provider.md_file_path):
                    logger.info("File modified, reloading configuration...")
                    self.config_provider._load_config()

        self.observer = Observer()
        self.observer.schedule(
            MDHandler(self),
            str(self.md_file_path.parent),
            recursive=False
        )
        self.observer.start()
        logger.info("Observer started successfully")

    def force_reload(self) -> None:
        """Forces reloading of the configuration."""
        logger.info("Forcing configuration reload...")
        self._load_config()


# Example usage
if __name__ == "__main__":
    # Initialize the configuration provider
    config_provider = ExpandevConfigProvider("config/agent_definition.md")
    
    # Access agent configurations
    agent = config_provider.agent_config
    print(f"Agent name: {agent.agent_name}")
    print(f"Role: {agent.role}")
    
    # Access task configurations
    for task_key, task in config_provider.tasks.items():
        print(f"\nTask: {task_key}")
        print(f"Objective: {task.main_objective}")
        print(f"Model: {task.llm_config.model}")
        print(f"Temperature: {task.llm_config.temperature}")