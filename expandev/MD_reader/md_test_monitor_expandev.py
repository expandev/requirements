import time
from datetime import datetime
import logging
import sys
import os
import textwrap
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_expandev_monitor():
    print("Starting Expandev MD file monitor...")
    
    try:
        from expandev.MD_reader.md_config_expandev import ExpandevConfigProvider, MarkdownParserUtils
        
        # Path to the agent configuration file
        md_file_path = 'docs/Agent_Construction/Expandev_Atena_Agent_Construction_Form.md'
        
        # Check if the file exists
        if not os.path.exists(md_file_path):
            logger.error(f"File not found: {md_file_path}")
            print(f"⚠️ File not found: {md_file_path}")
            print("Please check the path and try again.")
            sys.exit(1)
        
        config = ExpandevConfigProvider(md_file_path)
        
        def print_current_config():
            print("\n" + "="*80)
            print("🤖 EXPANDEV AGENT: DETAILED CONFIGURATIONS 🤖".center(80))
            print("="*80)
            
            # Agent Identification
            print("\n[📋 AGENT IDENTIFICATION]")
            print(f"• Name: {config.agent_name}")
            print(f"• Creation Date: {config.creation_date}")
            print(f"• Responsible: {config.responsible}")
            print(f"• Version: {config.version}")
            print(f"• Interaction Type: {config.interaction_type}")
            
            # Problems to Solve
            print("\n[🎯 PROBLEMS TO SOLVE]")
            if config.problems:
                for i, problem in enumerate(config.problems, 1):
                    print(f"• Problem {i}: {problem}")
            else:
                print("• No problem defined")
            
            # Agent Configurations
            print("\n[⚙️ AGENT CONFIGURATIONS]")
            print(f"• Role: {config.role}")
            print(f"• Field of Work: {config.field_of_work}")
            print(f"• Expertise Level: {config.expertise_level}")
            
            # Professional Background
            print("\n[👔 PROFESSIONAL BACKGROUND]")
            if config.professional_background:
                wrapped_text = textwrap.fill(config.professional_background, width=78, 
                                             initial_indent="  ", subsequent_indent="  ")
                print(wrapped_text)
            else:
                print("  No professional background defined")
            
            # Technical Skills
            print("\n[🛠️ TECHNICAL SKILLS]")
            if config.technical_skills:
                for skill in config.technical_skills:
                    if skill:  # Check if not empty
                        print(f"• {skill}")
            else:
                print("• No technical skill defined")
            
            # Resources
            print("\n[📚 RESOURCES]")
            if config.resources:
                for resource in config.resources:
                    if resource:  # Check if not empty
                        print(f"• {resource}")
            else:
                print("• No resource defined")
            
            # Communication Settings
            print("\n[💬 COMMUNICATION SETTINGS]")
            print(f"• Approach: {config.communication_approach}")
            print(f"• Response Style: {config.response_style}")
            print(f"• Proactivity Level: {config.proactivity_level}")
            print(f"• Autonomy: {config.autonomy}")
            
            # Tasks Configuration
            print("\n[📝 CONFIGURED TASKS]")
            if config.tasks:
                for task_key, task in config.tasks.items():
                    print(f"\n{task_key.upper()}:")
                    print(f"  • Name: {task.name or task_key}")
                    
                    # Option to view full Knowledge Base content
                    print(f"  • Task ID: {task_key}")  # Useful for selecting which task to examine
                    
                    # Main Objective (limited to avoid too long text)
                    if task.main_objective:
                        if len(task.main_objective) > 100:
                            print(f"  • Main Objective: {task.main_objective[:100]}...")
                        else:
                            print(f"  • Main Objective: {task.main_objective}")
                    else:
                        print("  • Main Objective: Not defined")
                    
                    print(f"  • Language: {task.language or 'Not defined'}")
                    
                    # Out of Scope
                    print("\n  • Out of Scope:")
                    if hasattr(task, 'out_of_scope') and task.out_of_scope and any(item.strip() for item in task.out_of_scope):
                        for item in task.out_of_scope:
                            if item.strip():
                                print(f"    - {item}")
                    else:
                        print("    - No out of scope item defined")
                    
                    # Knowledge Base
                    print("\n  • Knowledge Base:")
                    if hasattr(task, 'knowledge_base') and task.knowledge_base and any(kb.strip() for kb in task.knowledge_base):
                        for kb in task.knowledge_base:
                            if kb.strip():
                                print(f"    - {kb}")
                    else:
                        print("    - No knowledge file configured")
                    
                    # Knowledge Contents (summary)
                    print("\n  • Knowledge Contents:")
                    if hasattr(task, 'knowledge_contents') and task.knowledge_contents:
                        for key, value in task.knowledge_contents.items():
                            print(f"    - {key}: ", end="")
                            if isinstance(value, dict):
                                print(f"Dictionary with {len(value)} keys")
                            elif isinstance(value, list):
                                print(f"List with {len(value)} items")
                            else:
                                value_str = str(value)
                                print(f"{len(value_str)} characters")
                                
                            # New: Show more details of the Markdown content
                            if isinstance(value, str) and len(value) > 0:
                                # Extract the document title (first non-empty line)
                                lines = value.split('\n')
                                title = next((line for line in lines if line.strip()), "No title")
                                
                                # Show title and first characters
                                print(f"      Title: {title}")
                                print(f"      First 200 characters: {value[:200].replace(chr(10), ' ')}...")
                                
                                # Show document structure (headers)
                                headers = [line for line in lines if line.strip().startswith('#')][:5]
                                if headers:
                                    print(f"      Document structure (up to 5 headers):")
                                    for header in headers:
                                        print(f"        {header}")
                                        
                                # Also show end of the document
                                if len(value) > 400:
                                    print(f"      Last 200 characters: ...{value[-200:].replace(chr(10), ' ')}")
                    else:
                        print("    - No Markdown content loaded")
                    
                    # Description/Outcomes (summary)
                    print(f"\n  • Description/Outcomes:")
                    if task.description:
                        print(f"    - {len(task.description)} characters")
                        # Show only some placeholders
                        placeholders = set(re.findall(r'\{([^}]+)\}', task.description))
                        if placeholders:
                            print(f"    - Placeholders: {', '.join(placeholders)}")
                    else:
                        print("    - No description defined")
                        
                    # Formatted Description
                    print(f"\n  • Formatted Description:")
                    if hasattr(task, 'get_formatted_description'):
                        formatted = task.get_formatted_description()
                        print(f"    - {len(formatted)} characters")
                        if len(formatted) > 0:
                            print(f"    - First 50 characters: {formatted[:50]}...")
                    else:
                        print("    - Formatting function not available")

                    print(f"\n  • Expected Output: {task.expected_output or 'Not defined'}")
                    print(f"  • Output JSON: {task.output_json or 'Not configured'}")

                    # Tools
                    print("\n  • Tools:")
                    if task.tools and any(tool.strip() for tool in task.tools):
                        for tool in task.tools:
                            if tool.strip():
                                print(f"    - {tool}")
                    else:
                        print("    - No tool configured")
                    
                    # LLM Configuration
                    print(f"\n  • LLM Configurations:")
                    print(f"    - Model: {task.llm_config.model or 'Not defined'}")
                    print(f"    - Temperature: {task.llm_config.temperature}")
                    print(f"    - Max Tokens: {task.llm_config.max_tokens or 'Default'}")
                    
                    # Display original LLM Model section from the MD file
                    print(f"\n  • LLM Model Section in MD:")
                    try:
                        # Read the MD file again to display the original section
                        with open(md_file_path, 'r', encoding='utf-8') as file:
                            md_content = file.read()
                            
                        # Find the LLM section for the task
                        llm_section = ""
                        task_section = MarkdownParserUtils.find_section_between_headers(
                            md_content, 
                            f"### 3.{task_key[-1]}", 
                            f"### 3.{int(task_key[-1])+1}" if int(task_key[-1]) < 9 else "## Section 4:"
                        )
                        
                        if task_section:
                            llm_attrs_section = MarkdownParserUtils.find_section_between_headers(
                                task_section, 
                                f"#### 3.{task_key[-1]}.1", 
                                f"#### 3.{task_key[-1]}.2" if MarkdownParserUtils.section_exists(task_section, f"#### 3.{task_key[-1]}.2") else "## Section 4:"
                            )
                            
                            if llm_attrs_section:
                                model_section = MarkdownParserUtils.find_section(llm_attrs_section, "LLM Model")
                                if model_section:
                                    # Clean the section for display
                                    clean_section = model_section.replace("**LLM Model**", "").strip()
                                    # Display the lines of the section
                                    for line in clean_section.split('\n'):
                                        line = line.strip()
                                        if line and not line.startswith('- Description:') and not line.startswith('- Required:'):
                                            print(f"    {line}")
                    except Exception as e:
                        print(f"    Error displaying original section: {str(e)}")
            else:
                print("• No task configured")

            print("\n" + "="*80)
            print(f"Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80 + "\n")

        print("\nMonitor started!")
        print("1. Modify the MD file")
        print("2. Save changes")
        print("3. Press Enter to force an update")
        print("4. Type 'kb Task1' to see the full Knowledge Base content of a task")
        print("   Example: kb Task1")
        print("5. Type 'llm Task1' to see details of the task's LLM configuration")
        print("   Example: llm Task1")
        print("6. Press Ctrl+C to exit\n")

        # Print the initial configuration
        try:
            print_current_config()
        except Exception as e:
            logger.error(f"Error showing initial configuration: {str(e)}")
            logger.exception("Error details:")
            print(f"\n⚠️ Error showing configuration: {str(e)}")

        def show_knowledge_base_content(task_id):
            """Displays the full Knowledge Base content for a specific task"""
            if task_id not in config.tasks:
                print(f"⚠️ Task {task_id} not found!")
                return
                
            task = config.tasks[task_id]
            
            print("\n" + "="*80)
            print(f"📚 FULL KNOWLEDGE BASE CONTENT OF {task_id.upper()} 📚".center(80))
            print("="*80)
            
            if not task.knowledge_contents:
                print("\nNo content in the Knowledge Base for this task.")
                return
                
            for kb_name, kb_content in task.knowledge_contents.items():
                print(f"\n\n{'='*40}")
                print(f"📄 FILE: {kb_name}")
                print(f"{'='*40}\n")
                
                # Display full content
                if isinstance(kb_content, str):
                    print(kb_content)
                else:
                    print(json.dumps(kb_content, indent=2, ensure_ascii=False))
                    
            print("\n" + "="*80)
            
        def show_llm_details(task_id):
            """Displays details of the LLM configuration for a specific task"""
            if task_id not in config.tasks:
                print(f"⚠️ Task {task_id} not found!")
                return
                
            task = config.tasks[task_id]
            
            print("\n" + "="*80)
            print(f"🤖 DETAILS OF LLM CONFIGURATION OF {task_id.upper()} 🤖".center(80))
            print("="*80)
            
            # Display loaded configurations
            print("\n[📊 LOADED CONFIGURATIONS]")
            print(f"• Model: {task.llm_config.model or 'Not defined'}")
            print(f"• Temperature: {task.llm_config.temperature}")
            print(f"• Max Tokens: {task.llm_config.max_tokens or 'Default'}")
            
            # Try to display the original LLM Model section from the MD file
            print("\n[📝 ORIGINAL CONTENT IN MD FILE]")
            try:
                # Read the MD file again to display the original section
                with open(md_file_path, 'r', encoding='utf-8') as file:
                    md_content = file.read()
                    
                # Find the LLM section for the task
                task_num = task_id[-1]  # Extract the task number (e.g., "1" from "Task1")
                
                task_section = MarkdownParserUtils.find_section_between_headers(
                    md_content, 
                    f"### 3.{task_num}", 
                    f"### 3.{int(task_num)+1}" if int(task_num) < 9 else "## Section 4:"
                )
                
                if task_section:
                    # Find the LLM attributes section
                    llm_attrs_section = MarkdownParserUtils.find_section_between_headers(
                        task_section, 
                        f"#### 3.{task_num}.1", 
                        f"#### 3.{task_num}.2" if MarkdownParserUtils.section_exists(task_section, f"#### 3.{task_num}.2") else "## Section 4:"
                    )
                    
                    if llm_attrs_section:
                        # Model
                        model_section = MarkdownParserUtils.find_section(llm_attrs_section, "LLM Model")
                        if model_section:
                            print("\n• LLM Model:")
                            # Clean the section for display
                            for line in model_section.split('\n'):
                                line = line.strip()
                                if line and "LLM Model" not in line and not line.startswith('- Description:') and not line.startswith('- Required:'):
                                    print(f"  {line}")
                                    
                        # Temperature
                        temp_section = MarkdownParserUtils.find_section(llm_attrs_section, "LLM Temperature")
                        if temp_section:
                            print("\n• LLM Temperature:")
                            for line in temp_section.split('\n'):
                                line = line.strip()
                                if line and "LLM Temperature" not in line and not line.startswith('- Description:') and not line.startswith('- Type:') and not line.startswith('- Required:'):
                                    print(f"  {line}")
                                    
                        # Max Tokens
                        max_tokens_section = MarkdownParserUtils.find_section(llm_attrs_section, "LLM Max Tokens")
                        if max_tokens_section:
                            print("\n• LLM Max Tokens:")
                            # Try to extract the value between backticks
                            tokens_value = MarkdownParserUtils.extract_between_backticks(max_tokens_section)
                            if tokens_value:
                                print(f"  ```{tokens_value}```")
                            else:
                                # Display the cleaned content
                                for line in max_tokens_section.split('\n'):
                                    line = line.strip()
                                    if line and "LLM Max Tokens" not in line and not line.startswith('- Description:') and not line.startswith('- Type:') and not line.startswith('- Required:'):
                                        print(f"  {line}")
                    else:
                        print("  LLM attributes section not found.")
                else:
                    print("  Task section not found.")
            except Exception as e:
                print(f"  Error reading MD file: {str(e)}")
                
            print("\n[📋 PARSING ANALYSIS]")
            try:
                # Analysis of what was detected by the parser
                with open(md_file_path, 'r', encoding='utf-8') as file:
                    md_content = file.read()
                
                task_num = task_id[-1]
                task_section = MarkdownParserUtils.find_section_between_headers(
                    md_content, 
                    f"### 3.{task_num}", 
                    f"### 3.{int(task_num)+1}" if int(task_num) < 9 else "## Section 4:"
                )
                
                if task_section:
                    llm_section = MarkdownParserUtils.find_section_between_headers(
                        task_section, 
                        f"#### 3.{task_num}.1", 
                        f"#### 3.{task_num}.2" if MarkdownParserUtils.section_exists(task_section, f"#### 3.{task_num}.2") else "## Section 4:"
                    )
                    
                    if llm_section:
                        model_section = MarkdownParserUtils.find_section(llm_section, "LLM Model")
                        
                        if model_section:
                            print("\n• Analysis of LLM Model section:")
                            
                            # Check for backticks format
                            backticks_value = MarkdownParserUtils.extract_between_backticks(model_section)
                            if backticks_value:
                                print(f"  ✅ Found value between backticks: '{backticks_value}'")
                            else:
                                print(f"  ❌ No value found between backticks")
                            
                            # Check for checkbox format
                            checkbox_value = MarkdownParserUtils.extract_selected_checkbox_value(model_section)
                            if checkbox_value:
                                print(f"  ✅ Found value in checkbox: '{checkbox_value}'")
                            else:
                                print(f"  ❌ No value found in checkbox")
                                
                                # Detailed analysis of lines with checkbox
                                checkbox_lines = []
                                for line in model_section.split('\n'):
                                    if '- [' in line:
                                        checkbox_lines.append(line.strip())
                                
                                if checkbox_lines:
                                    print("\n  Checkboxes found (but none selected):")
                                    for line in checkbox_lines:
                                        print(f"    {line}")
                                        # Check for uppercase or lowercase X
                                        if '[X]' in line or '[x]' in line:
                                            print(f"    ⚠️ This checkbox appears marked, but was not recognized: '{line}'")
                                            match = re.search(r'- \[[Xx]\] ([^:\n]+)', line)
                                            if match:
                                                print(f"    🔍 Value that would be extracted: '{match.group(1).strip()}'")
                                else:
                                    print("  No checkbox found in the section")
                            
                            # Final value extracted by safe_extract_value
                            safe_value = MarkdownParserUtils.safe_extract_value("LLM Model", llm_section)
                            print(f"\n• Final extracted value: '{safe_value or 'None'}'")
                            
                            # Correction suggestion
                            print("\n• Suggested correct format:")
                            print("  For backticks format:")
                            print("  ```")
                            print("  anthropic/claude-3-5-haiku-20241022")
                            print("  ```")
                            print("\n  For checkbox format:")
                            print("  - [ ] gpt-4-turbo-preview")
                            print("  - [X] anthropic/claude-3-5-haiku-20241022")
                            print("  - [ ] anthropic/claude-3-sonnet-20240229")
                    else:
                        print("  LLM attributes section not found.")
                else:
                    print("  Task section not found.")
            except Exception as e:
                print(f"  Error during analysis: {str(e)}")
                
            print("\n" + "="*80)
        
        while True:
            try:
                # Wait for user input
                user_input = input("Command (Enter=Update, kb Task1=View Knowledge Base, llm Task1=View LLM, Ctrl+C=Exit): ")
                
                # Check if the user wants to view the knowledge base
                if user_input.lower().startswith("kb "):
                    task_id = user_input[3:].strip()
                    show_knowledge_base_content(task_id)
                # Check if the user wants to view LLM details
                elif user_input.lower().startswith("llm "):
                    task_id = user_input[4:].strip()
                    show_llm_details(task_id)
                else:
                    # Default behavior: update
                    config.force_reload()
                    print_current_config()
                
                time.sleep(1)  # Small pause to avoid excessive CPU usage
                
            except KeyboardInterrupt:
                print("\nMonitor terminated by user.")
                break
            except Exception as e:
                logger.error(f"Error during execution: {str(e)}")
                logger.exception("Error details:")
                print(f"\n⚠️ Error during execution: {str(e)}")
                print("Check the logs for more details.")
        
    except ImportError as e:
        logger.error(f"Error importing ExpandevConfigProvider: {str(e)}")
        logger.error("Check if the module is in the PYTHONPATH")
        print(f"\n⚠️ Error importing ExpandevConfigProvider: {str(e)}")
        print("Ensure the module 'utils.md_config_expandev' is available in the PYTHONPATH")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running the monitor: {str(e)}")
        logger.exception("Error details:")
        print(f"\n⚠️ Error running the monitor: {str(e)}")
        print("Check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    test_expandev_monitor()