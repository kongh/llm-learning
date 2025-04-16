from basic_workflow import chain, parallel, route
from orchestrator_workers_workflow import FlexibleOrchestrator
from evaluator_optimizer_workflow import loop
import pytest

def test_chain():
    """
    # Example 1: Chain workflow for structured data extraction and formatting
    # Each step progressively transforms raw text into a formatted table
    """
    data_processing_steps = [
        """Extract only the numerical values and their associated metrics from the text.
        Format each as 'value: metric' on a new line.
        Example format:
        92: customer satisfaction
        45%: revenue growth""",
        
        """Convert all numerical values to percentages where possible.
        If not a percentage or points, convert to decimal (e.g., 92 points -> 92%).
        Keep one number per line.
        Example format:
        92%: customer satisfaction
        45%: revenue growth""",
        
        """Sort all lines in descending order by numerical value.
        Keep the format 'value: metric' on each line.
        Example:
        92%: customer satisfaction
        87%: employee satisfaction""",
        
        """Format the sorted data as a markdown table with columns:
        | Metric | Value |
        |:--|--:|
        | Customer Satisfaction | 92% |"""
    ]

    report = """
    Q3 Performance Summary:
    Our customer satisfaction score rose to 92 points this quarter.
    Revenue grew by 45% compared to last year.
    Market share is now at 23% in our primary market.
    Customer churn decreased to 5% from 8%.
    New user acquisition cost is $43 per user.
    Product adoption rate increased to 78%.
    Employee satisfaction is at 87 points.
    Operating margin improved to 34%.
    """

    print("\nInput text:")
    print(report)
    formatted_result = chain(report, data_processing_steps)

    print(formatted_result)
    assert formatted_result != ''

def test_parallel():
    """
    # Example 2: Parallelization workflow for stakeholder impact analysis
    # Process impact analysis for multiple stakeholder groups concurrently
    """
    stakeholders = [
        """Customers:
        - Price sensitive
        - Want better tech
        - Environmental concerns""",
        
        """Employees:
        - Job security worries
        - Need new skills
        - Want clear direction""",
        
        """Investors:
        - Expect growth
        - Want cost control
        - Risk concerns""",
        
        """Suppliers:
        - Capacity constraints
        - Price pressures
        - Tech transitions"""
    ]

    impact_results = parallel(
        stakeholders,
        """Analyze how market changes will impact this stakeholder group.
        Provide specific impacts and recommended actions.
        Format with clear sections and priorities. You must answer in Chinese."""
    )

    for result in impact_results:
        print(result)

def test_route():
    """
    # Example 3: Route workflow for customer support ticket handling
    # Route support tickets to appropriate teams based on content analysis
    """
    support_routes = {
        "billing": """You are a billing support specialist. Follow these guidelines:
        1. Always start with "Billing Support Response:"
        2. First acknowledge the specific billing issue
        3. Explain any charges or discrepancies clearly
        4. List concrete next steps with timeline
        5. End with payment options if relevant
        
        Keep responses professional but friendly.
        
        Input: """,
        
        "technical": """You are a technical support engineer. Follow these guidelines:
        1. Always start with "Technical Support Response:"
        2. List exact steps to resolve the issue
        3. Include system requirements if relevant
        4. Provide workarounds for common problems
        5. End with escalation path if needed
        
        Use clear, numbered steps and technical details.
        
        Input: """,
        
        "account": """You are an account security specialist. Follow these guidelines:
        1. Always start with "Account Support Response:"
        2. Prioritize account security and verification
        3. Provide clear steps for account recovery/changes
        4. Include security tips and warnings
        5. Set clear expectations for resolution time
        
        Maintain a serious, security-focused tone.
        
        Input: """,
        
        "product": """You are a product specialist. Follow these guidelines:
        1. Always start with "Product Support Response:"
        2. Focus on feature education and best practices
        3. Include specific examples of usage
        4. Link to relevant documentation sections
        5. Suggest related features that might help
        
        Be educational and encouraging in tone.
        
        Input: """
    }

    # Test with different support tickets
    tickets = [
        """Subject: Can't access my account
        Message: Hi, I've been trying to log in for the past hour but keep getting an 'invalid password' error. 
        I'm sure I'm using the right password. Can you help me regain access? This is urgent as I need to 
        submit a report by end of day.
        - John""",
        
        """Subject: Unexpected charge on my card
        Message: Hello, I just noticed a charge of $49.99 on my credit card from your company, but I thought
        I was on the $29.99 plan. Can you explain this charge and adjust it if it's a mistake?
        Thanks,
        Sarah""",
        
        """Subject: How to export data?
        Message: I need to export all my project data to Excel. I've looked through the docs but can't
        figure out how to do a bulk export. Is this possible? If so, could you walk me through the steps?
        Best regards,
        Mike"""
    ]

    print("Processing support tickets...\n")
    for i, ticket in enumerate(tickets, 1):
        print(f"\nTicket {i}:")
        print("-" * 40)
        print(ticket)
        print("\nResponse:")
        print("-" * 40)
        response = route(ticket, support_routes)
        print(response)

def test_orchestrator_workers():
    """
    # Example 4: Orchestrator and Workers workflow for task decomposition and execution
    # Break down tasks and run them in parallel using worker LLMs
    """
    ORCHESTRATOR_PROMPT = """
    Analyze this task and break it down into 2-3 distinct approaches:

    Task: {task}

    Return your response in this format:

    <analysis>
    Explain your understanding of the task and which variations would be valuable.
    Focus on how each approach serves different aspects of the task.
    </analysis>

    <tasks>
        <task>
        <type>formal</type>
        <description>Write a precise, technical version that emphasizes specifications</description>
        </task>
        <task>
        <type>conversational</type>
        <description>Write an engaging, friendly version that connects with readers</description>
        </task>
    </tasks>
    """

    WORKER_PROMPT = """
    Generate content based on:
    Task: {original_task}
    Style: {task_type}
    Guidelines: {task_description}

    Return your response in this format:

    <response>
    Your content here, maintaining the specified style and fully addressing requirements.
    </response>
    """

    orchestrator = FlexibleOrchestrator(
        orchestrator_prompt=ORCHESTRATOR_PROMPT,
        worker_prompt=WORKER_PROMPT,
    )

    results = orchestrator.process(
        task="Write a product description for a new eco-friendly water bottle",
        context={
            "target_audience": "environmentally conscious millennials",
            "key_features": ["plastic-free", "insulated", "lifetime warranty"]
        }
    )
    print(results)


def test_evalutor_optimizer():
    evaluator_prompt = """
    Evaluate this following code implementation for:
    1. code correctness
    2. time complexity
    3. style and best practices

    You should be evaluating only and not attemping to solve the task.
    Only output "PASS" if all criteria are met and you have no further suggestions for improvements.
    Output your evaluation concisely in the following format.

    <evaluation>PASS, NEEDS_IMPROVEMENT, or FAIL</evaluation>
    <feedback>
    What needs improvement and why.
    </feedback>
    """

    generator_prompt = """
    Your goal is to complete the task based on <user input>. If there are feedback 
    from your previous generations, you should reflect on them to improve your solution

    Output your answer concisely in the following format: 

    <thoughts>
    [Your understanding of the task and feedback and how you plan to improve]
    </thoughts>

    <response>
    [Your code implementation here]
    </response>
    """

    task = """
    <user input>
    Implement a Stack with:
    1. push(x)
    2. pop()
    3. getMin()
    All operations should be O(1).
    </user input>
    """

    loop(task, evaluator_prompt, generator_prompt)