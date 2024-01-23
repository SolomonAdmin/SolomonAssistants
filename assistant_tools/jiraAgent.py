import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers import get_secret_value

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_openai import OpenAI

JIRA_API_TOKEN = get_secret_value("JIRA_API_TOKEN")
OPENAI_API_KEY = get_secret_value("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["JIRA_API_TOKEN"] = JIRA_API_TOKEN
os.environ["JIRA_USERNAME"] = "ross.dickinson.ctr@skymantics.com"
os.environ["JIRA_INSTANCE_URL"] = "https://skymantics.atlassian.net"

def jira_run_agent_query(jira_query):
    """
    Initializes the agent and runs the given query.
    
    :param query: A string representing the instruction or query to be processed by the agent.
    :return: The result of the agent's execution.
    """
    llm = OpenAI(temperature=0)
    jira = JiraAPIWrapper()
    toolkit = JiraToolkit.from_jira_api_wrapper(jira)
    agent = initialize_agent(
        toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False
    )

    return agent.run(jira_query)

# # Example usage
# response  = jira_run_agent_query("Tell me about issue SIMON-2802.")
# print(response)

# os.environ["JIRA_API_TOKEN"] = "ATATT3xFfGF0fv8gfMqaK3bAMgX2fCmvin2PTdftjMFgLu7ffa5lMMqMOv1F_hDXTbMtuZIghMhS9teKtJLB2IqwsS3L74wz9v5VBSwfbqznS1cBH7_uQPLHwnCGS7tXVPXsGXW3ZBTvLImhWI--fDsrFeLf_PnLNrSB-zQ9atZICUOEwxmEWNY=42A7C9E1"
# os.environ["OPENAI_API_KEY"] = "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"