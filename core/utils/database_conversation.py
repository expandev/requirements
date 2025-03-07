import psycopg2
from psycopg2 import Error
import json
import os
from dotenv import load_dotenv, find_dotenv

# Configure logging
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class DatabaseConversation:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv(find_dotenv())

        # Get the database settings from the .env file
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_port = os.getenv('DB_PORT', '5432')

        # Build the options string from the environment variable
        db_options_str = os.getenv('DB_OPTIONS', '')
        db_options = ""

        # Format the options to the format expected by psycopg2
        if db_options_str:
            # Check if the options already have the -c prefix
            if "-c" in db_options_str:
                # If they already have the -c prefix, use it directly
                db_options = db_options_str
            else:
                # Convert space-separated options to the -c format
                options_list = db_options_str.split()
                formatted_options = []

                for option in options_list:
                    formatted_options.append(f"-c {option}")

                db_options = " ".join(formatted_options)

        try:
            # Define the connection credentials
            connection_params = {
                'host': db_host,
                'dbname': db_name,
                'user': db_user,
                'password': db_password,
                'port': db_port
            }

            # Add options only if valid options exist
            if db_options:
                connection_params['options'] = db_options

            # Log the settings for debugging (without showing the password)
            debug_params = connection_params.copy()
            debug_params['password'] = '******'
            logger.info(f"Connecting with parameters: {debug_params}")

            # Establish the connection
            self.connection = psycopg2.connect(**connection_params)

            logger.info(f"Connection established to the database: {db_name} on {db_host}")

        except Error as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            raise  # Propagate the error to be handled at a higher level

    # Helper method to check if the connection is active
    def check_connection(self):
        if not self.connection or self.connection.closed:
            raise ConnectionError("Database connection is not established")
        return True

    def startConversation(self, demand_id, user, task_name, task_config, agent_name, agent_config):
        """
        Starts a new conversation using the procedure sp_start_conversation
        
        Args:
            demand_id: Demand ID
            user: User name
            task_name: Task name
            task_config: Task configuration as a dict
            agent_name: Agent name
            agent_config: Agent configuration as a dict
            
        Returns:
            tuple: (demand_config, knowledge_area, iteration_id) if successful, (None, None, None) otherwise
        """
        try:
            # Check the connection
            self.check_connection()
            
            # Convert dictionaries to JSON strings
            task_config_json = json.dumps(task_config, ensure_ascii=False)
            agent_config_json = json.dumps(agent_config, ensure_ascii=False)
            
            logger.info(f"Starting conversation for demand {demand_id}...")
            
            # Simpler approach: create a temporary PL/pgSQL function and execute it
            cursor = self.connection.cursor()
            
            cursor.execute("CALL sp_start_conversation(%s, %s, %s, %s, %s, %s, %s, %s, %s) ", (
                demand_id,
                user,
                task_name,
                task_config_json,
                agent_name,
                agent_config_json,
                None, 
                None,
                None
                )
            )
        
            # Get the output parameter values
            demand_config, knowledge_area, iteration_id = cursor.fetchone() 

            return demand_config, knowledge_area, iteration_id
            
        except Error as e:
            logger.error(f"Error starting conversation: {e}")
            self.connection.rollback()
            return None, None, None

    def endConversation(self, iteration_id, result, input_token=0, output_token=0):
        """
        Ends a conversation using the procedure sp_end_conversation
        
        Args:
            iteration_id: Iteration ID
            result: Conversation result as text
            input_token: Total input tokens used
            output_token: Total output tokens used
            
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        try:
            # Check the connection
            self.check_connection()
            
            # Ensure that result is in UTF-8 if it's a string
            if isinstance(result, str):
                result = result.encode('utf-8').decode('utf-8')
            
            cursor = self.connection.cursor()
            
            # Call the procedure sp_end_conversation directly with the token parameters
            cursor.execute("CALL dbo.sp_end_conversation(%s, %s, %s, %s);", 
                          (iteration_id, result, input_token, output_token))
            cursor.close()
            
            self.connection.commit()

            return True
            
        except Error as e:
            logger.error(f"Error ending conversation: {e}")
            self.connection.rollback()
            return False