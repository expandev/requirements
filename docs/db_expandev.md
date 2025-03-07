# Expandev Database (PostgreSQL)

**Server**: postgresql-codenapp-dev.postgres.database.azure.com  
**Tool**: pgAdmin  

## Tables and Configurations
### CREW
Team of agents

| Column          | Type          | Constraint  | Description                                         |
|-----------------|---------------|-------------|-----------------------------------------------------|
| `id`            | `smallint`    | `pk`        | Unique identifier of the crew.                      |
| `name`          | `varchar(100)`| `not null`  | Name of the crew.                                   |
| `default_config`| `json`        | `not null`  | Default configuration of the model and temperature for each task. Json Keys: `task`, `model`, and `temperature`.|

### DEMAND
Demands/features

| Column           | Type    | Constraint | Description                                                
|------------------|---------|------------|------------------------------------------------------------|
| `id`             | `int`   | `pk`       | Unique identifier of the demand.                           |
| `config`         | `json`  | `not null` | Details of the demand. Json keys: `name` and `description`.|
| `knowledge_area` | `json`  | `null`     | Knowledge area of the demand. Json keys: `area`.           |

### EMBEDDING
Storage of embeddings

| Column       | Type        | Constraint | Description                                               |
|------------- |------------ |------------|-----------------------------------------------------------|
| `id`         | `int`       | `pk`       | Unique identifier of the embedding.                       |
| `vector`     | `vector`    | `not null` | 384-dimensional vector.                                   |
| `metadata`   | `json`      |            | Contains the original text associated with the embedding. |
| `created_at` | `timestamp` |            | Date and time of record creation. Automatically filled.   |

### EVALUATION
Evaluation of the result of an iteration.

| Column        | Type         | Constraint      | Description                                       |
|---------------|--------------|-----------------| --------------------------------------------------|
| `id`          | `int`        | `pk`            | Unique identifier of the evaluation.              |
| `iteration_id`| `int`        | `not null`, `fk`| Reference to Iteration evaluated (foreign key to `ITERATION`). |
| `by_agent`    | `boolean`    | `not null`      | Responsible for the evaluation: 0-Human / 1-Agent |
| `llm_id`      | `smallint`   | `fk`            | Reference to LLM used in the evaluation. Filled if by_agent=1. (foreign key to `LLM`). |
| `temperature` | `numeric(5,2)|                 | Agent's temperature used in the evaluation. Filled if by_agent=1.  |
| `max_iter`    | `smallint`   |                 | Maximum number of iterations configured in the agent. Filled if by_agent=1.|
| `label`       | `json`       |                 | Evaluation result                                 |
| `input_token` | `int`        |                 | Number of tokens consumed when triggering the task. Filled if by_agent=1. |
| `output_token`| `int`        |                 | Number of tokens consumed by the result. Filled if by_agent=1. |
| `executed_at` | `timestamp`  | `not null`      | Date and time of evaluation. Automatically filled.|
| `executed_by` | `varchar(50)`|                 | User responsible for the evaluation. Filled if by_agent=0.|

### ITERATION
Execution logs for each task in the workflow.

| Column        | Type          | Constraint      | Description                                     |
|---------------|---------------|-----------------|-------------------------------------------------|
| `id`          | `int`         | `pk`            | Unique identifier of the iteration.             |
| `workflow_id` | `int`         | `not null`, `fk`| Workflow ID of the executed workflow (foreign key to `WORKFLOW`).|
| `task_name`   | `varchar(100)`| `not null`      | Name of the task executed.                      |
| `task_config` | `json`        | `not null`      | Configuration used in the task execution. Json keys: `model`, `temperature`, `description`, and `expected_output`.|
| `agent_name`  | `varchar(100)`|                 | Name of the agent responsible for the execution.|
| `agent_config`| `json`        |                 | Configuration used by the agent during the task execution. Json keys: `model`, `temperature`, `goal`, `backstory`, `verbose`, `max_iter`. |
| `input_token` | `int`         |                 | Number of tokens consumed when triggering the task.|
| `output_token`| `int`         |                 | Number of tokens consumed by the result.        |
| `executed_at` | `timestamp`   | `not null`      | Date and time of task execution.                |
| `result`      | `text`        |                 | Result generated from the task execution.       |

### LLM
AI models.

| Column            | Type           | Constraint      | Description                                |
|-------------------|--------------- |-----------------|--------------------------------------------|
| `id`              | `smallint`     | `pk`            | Unique identifier of the AI model.         |
| `manufacturer_id` | `smallint`     | `not null`, `fk`| Manufacturer ID (foreign key to `MANUFACTURER`).|
| `model`           | `varchar(100)` | `not null`      | Identifying string of the model in the manufacturer's API.|
| `alias`           | `varchar(100)` | `not null`      | Model's alias.                             |
| `current_cost`    | `numeric(7,4)` | `not null`      | Cost per n tokens.                         |

### MANUFACTURER 
LLM manufacturers.

| Column            | Type            | Constraint        | Description                           |
|--------------     |-----------------|-------------------|---------------------------------------|
| `id`              | `int`           | `pk`              | Unique identifier of the manufacturer.|
| `name`            | `varchar(100)`  | `not null`        | Manufacturer's name.                  |

### WORKFLOW
Workflows of a crew for a specific demand. 

| Column            | Type            | Constraint        | Description                              |
|------------------ |-----------------|-------------------|------------------------------------------|
| `id`              | `int`           | `pk`              | Unique identifier of the workflow.       |
| `demand_id`       | `int`           | `not null`, `fk`  | Demand ID (foreign key to `DEMAND`).     |
| `crew_id`         | `int`           | `not null`, `fk`  | Crew ID (foreign key to `CREW`).         |
| `config`          | `json`          |                   | Specific configuration for one or more tasks. If `null`, the default configuration (defined in the crew) is used. Json Keys: `task`, `model`, and `temperature`.|
| `created_at`      | `timestamp`     | `not null`        | Date and time of workflow creation in the database.          |
| `executed_at`     | `timestamp`     |                   | Date and time of workflow execution. If `null`, not executed yet.|
| `created_by`      | `varchar(50)`   | `null`            | User responsible for creating the workflow in the database.  |