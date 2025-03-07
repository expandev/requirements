from typing import Optional
import logging
from enum import Enum
from crews.atena_system import AtenaSystem
from langchain_core.messages import SystemMessage, HumanMessage

# Basic logging configuration
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """Possible conversation states."""
    ACTIVE = "active"
    ENDED = "ended"
    ERROR = "error"

class AtenaConversation:
    """Manages the conversation with the agent."""
    
    # Special system commands
    EXIT_COMMANDS = {'exit', 'quit'}
    SPECIAL_COMMANDS = {
        'save': 'save_history',
        'tokens': 'show_tokens',
    }

    def __init__(self, demand_id: int):
        """
        Start the conversation with Atena.
        
        Args:
            demand_id: ID of the demand to be processed
        """
        self.system = AtenaSystem(demand_id)
        self.state = ConversationState.ACTIVE

    def display_welcome_message(self) -> None:
        """Displays the welcome message."""
        welcome_text = [
            "\nYou will be interacting with Atena, a requirements analyst specialized in software.",
            "\n-----------------------------------------------------------------------------------------------",
            f"\nI am analyzing the following demand:\n{self.system.demand}",
            f"\nKnowledge area: {self.system.knowledge_area}",
            f"\nIteration ID: {self.system.iteration_id}",
            "\nAvailable commands:",
            "- 'save': saves the conversation history",
            "- 'tokens': displays the total number of tokens used",
            "- 'exit': ends the conversation",
            "\nAtena: Hello! My name is Atena, and I am a requirements analyst specialized in understanding your needs for software development."
        ]
        print('\n'.join(welcome_text))

    def display_message_history(self) -> None:
        """Shows the message history on the terminal."""
        print("\n=== Message History ===")
        for msg in self.system.messages[1:]:  # Skips the first message (system prompt)
            role = "You" if isinstance(msg, HumanMessage) else "Atena"
            print(f"\n{role}: {msg.content}")
        print("\n===========================")

    def display_token_usage(self) -> None:
        """Displays information about token usage."""
        print("\n=== Token Usage ===")
        print(f"Total tokens used in the conversation: {self.system.total_conversation_tokens}")
        print("==================\n")

    def handle_special_commands(self, command: str) -> bool:
        """
        Processes special system commands.
        
        Args:
            command: Command to be processed
            
        Returns:
            bool: True if the conversation should continue, False to end
        """
        if command in self.EXIT_COMMANDS:
            print("Saving history and ending the conversation...")
            self.display_message_history()
            self.system.save_history()
            print("Conversation ended. Goodbye!")
            self.state = ConversationState.ENDED
            return False
            
        if command == 'save':
            self.display_message_history()
            self.system.save_history()
            return True

        if command == 'tokens':
            self.display_token_usage()
            return True
            
        return None

    def handle_user_input(self, user_input: str) -> bool:
        """
        Processes user input.
        
        Args:
            user_input: Text entered by the user
            
        Returns:
            bool: True if the conversation should continue, False to end
        """
        try:
            user_input = user_input.strip()
            
            # Check for empty input
            if not user_input:
                print("\nAtena: Please type a message before sending.")
                return True
                
            # Process special commands
            special_command_result = self.handle_special_commands(user_input.lower())
            if special_command_result is not None:
                return special_command_result
                
            # Process normal message
            response = self.system.process_message(user_input)
            print("\nAtena:", response)
            return True
            
        except (EOFError, KeyboardInterrupt):
            logger.info("Operation interrupted by the user")
            self.display_message_history()
            self.system.save_history()
            self.state = ConversationState.ENDED
            return False
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            print(f"\nAtena: Sorry, an error occurred while processing your message.")
            self.state = ConversationState.ERROR
            return True

    def run(self) -> None:
        """Runs the main conversation loop."""
        try:
            self.display_welcome_message()
            
            while self.state == ConversationState.ACTIVE:
                user_input = input("\nYou: ")
                if not self.handle_user_input(user_input):
                    break
                    
        except Exception as e:
            logger.error(f"Fatal error during execution: {str(e)}")
            print("\nCritical error. Shutting down the system.")
        finally:
            # Ensure history is saved even in case of an error
            if self.state == ConversationState.ERROR:
                try:
                    self.system.save_history()
                except:
                    pass
            logger.info("Conversation ended")

def main():
    """Main function that starts the system."""
    try:
        # Ask the user for the demand ID
        demand_id = int(input("Enter the demand ID: "))
        
        conversation = AtenaConversation(demand_id)
        conversation.run()
    except ValueError:
        print("Error: The demand ID must be an integer.")
    except Exception as e:
        logger.error(f"Fatal error when starting the system: {str(e)}")
        print(f"\nFatal error when starting the system: {str(e)}")

if __name__ == "__main__":
    main()