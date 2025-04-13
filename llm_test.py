from llm import llm_call

def test_llm():
    """
    A simple test function for LLM.
    Currently, it just prints a message indicating the test is running.
    """
    print("Running LLM test...")
    # Here you can add actual LLM testing logic, such as sending a prompt and checking the response.

    system_prompt = "我是Kong Hang的助手"
    msg = llm_call("你是谁？", system_prompt)
    print(msg)
    assert msg.startswith(system_prompt)