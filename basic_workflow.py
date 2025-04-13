from typing import List, Dict
from llm import llm_call, extract_xml
from concurrent.futures import ThreadPoolExecutor
import re

def chain(input: str, prompts: List[str]) -> str:
    """
    Chain multiple LLM calls sequentially, passing results between steps.
    Args:
        input (str): The input to the first prompt.
        prompts (List[str]): A list of prompts to chain together.
    Returns:
        str: The output of the last LLM in the chain.
    """
    result = input
    for i, prompt in enumerate(prompts):
        print(f"Step {i + 1}:")
        result = llm_call(f'{prompt}\nInput: {result}')
        print(f"Output: {result}\n")
    return result

def parallel(inputs: List[str], prompt: str, n_workers: int = 3) -> List[str]:
    """
    Run multiple LLM calls in parallel, processing each input independently.
    Args:
        inputs (List[str]): A list of inputs to process.
        prompt (str): The prompt to use for each LLM call.
    Returns:
        List[str]: A list of outputs from each LLM call.
    """
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(llm_call, f"{prompt}\nInput: {x}") for x in inputs]
        return [f.result() for f in futures]

def route(input: str, routes: Dict[str, str]) -> str:
    """
    Route the input to the appropriate LLM based on a dictionary of routes.
    Args:
        input (str): The input to route.
        routes (Dict[str, str]): A dictionary mapping keywords to LLM names.
    Returns:
        str: The output of the selected LLM.
    """

    # First determine appropriate route using LLM with chain-of-thought
    print(f"\nAvailable routes: {list(routes.keys())}")
    selector_prompt = f"""
    Analyze the input and select the most appropriate support team from these options: {list(routes.keys())}
    First explain your reasoning, then provide your selection in this XML format:

    <reasoning>
    Brief explanation of why this ticket should be routed to a specific team.
    Consider key terms, user intent, and urgency level.
    </reasoning>

    <selection>
    The chosen team name
    </selection>

    Input: {input}""".strip()
    
    route_response = llm_call(selector_prompt)
    reasoning = extract_xml(route_response, 'reasoning')
    route_key = extract_xml(route_response, 'selection').strip().lower()
    
    print("Routing Analysis:")
    print(reasoning)
    print(f"\nSelected route: {route_key}")
    
    # Process input with selected specialized prompt
    selected_prompt = routes[route_key]
    return llm_call(f"{selected_prompt}\nInput: {input}")