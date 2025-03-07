
# Expandev Crew Implementation Guide

## Agents

### Role Definition
- Use clear and concise role names that reflect their function

Examples:
Senior Data Scientist
Research Analyst
Senior Python Developer
Data Analyst
Customer Service Representative
AI Technology Researcher
Market Researcher
About User
Space News Analyst
Blog Content Generator Agent
Market Research Analyst
Content Writer
Writer
Python Data Analyst
Data Fetcher
Data Processor
Summary Generator
Researcher
Senior Writer
Project Manager
Data Scientist
Senior Research Analyst
Tech Content Strategist
Python Data Analyst
OpenAI Expert
Anthropic Expert
Customized LLM Expert
Local AI Expert
Github Agent
Web Research Expert
Task Execution Evaluator
Task Execution Planner
Number Generator
Math Tutor
Friendly Neighbor
{topic} specialist
Information Agent
CEO
Very helpful assistant
{topic} Researcher
Scorer
Manager

### Goal Definition
- Use clear and concise goal definitions that express the activities it is able to execute

Examples:
Analyze and interpret complex datasets to provide actionable insights
Analyze and provide insights using Python
Analyze and remember complex data patterns
Analyze data and provide insights using Python
Analyze data trends in the market
Analyze research findings
Answer questions about space news accurately and comprehensively
Be super empathetic
Comply with necessary changes
Conduct foundational research
Conduct in-depth analysis
Conduct thorough research and analysis on AI and AI agents
Coordinate scoring processes
Craft compelling content on tech advancements
Craft engaging blog posts about the AI industry
Craft well-designed and thought-out code
Create engaging content
Draft the final report
Efficiently manage the crew and ensure high-quality task completion
Evaluate the performance of the agents in the crew
Express hot takes on {topic}
Fetch data online using Serper tool
Find and summarize information about specific topics
Find and summarize the latest AI news
Find related information from specific URL's
Gather current market data and trends
Gather information on market dynamics
Generate a blog title and content
Generate random numbers for various purposes
Generate summary from fetched data
Make everyone feel welcome
Make sure the writers in your company produce amazing content
Make the best research and analysis on content about AI and AI agents
Manage the crew and ensure the tasks are completed efficiently
Perform deep analysis of large datasets
Plan Step by Step Plan
Process fetched data
Process information using a local model
Provide information based on knowledge sources
Provide insights using GPT-4
Provide tailored responses
Provide up-to-date market analysis
Provide up-to-date market analysis of the AI industry
Research AI advancements
Score the title
Solve math problems accurately
Take action on Github using Github APIs
Uncover cutting-edge developments in AI and data science
Write and debug Python code
Write code to solve problems
Write detailed articles on AI
Write engaging content on market trends
Write engaging content on various topics
Write lessons of math for kids
Write the best content about AI and AI agents
Write the best content about {topic}
You know everything about the user
You research about math

### Backstory Definition

## Tasks Best Practices

### Task Design
- Create atomic, single-responsibility tasks
- Define clear input and output requirements
- Set reasonable max_iterations (3-5 recommended)
- Include validation criteria

### Task Dependencies
- Clearly specify task dependencies
- Use sequential tasks for complex workflows
- Implement proper error handling
- Consider task timeout settings

## Knowledge Management

### Knowledge Base
- Organize knowledge in structured formats
- Use appropriate file formats (txt, pdf, json)
- Implement version control for knowledge bases
- Keep context-relevant information only

### Memory Handling
- Choose appropriate memory types:
    - Short-term for task-specific info
    - Long-term for persistent knowledge
- Clear memory when no longer needed
- Monitor memory usage

## Crew Management

### Crew Composition
- Limit crew size (3-5 agents recommended)
- Ensure complementary agent skills
- Define clear hierarchy if needed
- Set appropriate task delegation rules

### Workflow Optimization
- Implement proper error handling
- Set reasonable timeouts
- Monitor resource usage
- Use async operations when possible

### Communication
- Define clear communication protocols
- Implement logging mechanisms
- Set up feedback loops
- Handle exceptions gracefully