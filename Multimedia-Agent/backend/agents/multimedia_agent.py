"""
Multimedia Agent

LangGraph-compatible Multimedia Agent responsible for
selecting and executing multimedia tools.
"""

from langchain_core.messages import (
    SystemMessage,
    ToolMessage,
)

from backend.config import get_llm
from backend.prompts.system_prompt import SYSTEM_PROMPT
from backend.tools.multimedia_tools import (
    MULTIMEDIA_TOOLS,
)


class MultimediaAgent:
    """
    Multimedia Agent

    Responsibilities
    ----------------
    - Decide which multimedia tool(s) should be used.
    - Execute tool calls.
    - Return responses compatible with LangGraph.
    """

    def __init__(self):

        self.llm = get_llm()

        self.tools = MULTIMEDIA_TOOLS

        self.tools_by_name = {
            tool.name: tool
            for tool in self.tools
        }

        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )

    # ---------------------------------------------------
    # Agent Node
    # ---------------------------------------------------

    def agent_node(self, state: dict) -> dict:
        """
        LangGraph Agent Node

        Input
        -----
        {
            "messages": [...]
        }

        Output
        ------
        {
            "messages": [AIMessage]
        }
        """

        messages = state["messages"]

        system_message = SystemMessage(
            content=SYSTEM_PROMPT
        )

        response = self.llm_with_tools.invoke(
            [system_message] + messages
        )

        return {
            "messages": [response]
        }

    # ---------------------------------------------------
    # Tool Node
    # ---------------------------------------------------

    def tool_node(self, state: dict) -> dict:
        """
        Execute every tool requested by the LLM.

        Input
        -----
        {
            "messages": [...]
        }

        Output
        ------
        {
            "messages": [
                ToolMessage(...)
            ]
        }
        """

        messages = state["messages"]

        last_message = messages[-1]

        tool_outputs = []

        if not hasattr(last_message, "tool_calls"):
            return {
                "messages": []
            }

        for tool_call in last_message.tool_calls:

            tool_name = tool_call["name"]

            tool_args = tool_call["args"]

            tool_id = tool_call["id"]

            tool_function = self.tools_by_name.get(
                tool_name
            )

            if tool_function is None:

                tool_outputs.append(

                    ToolMessage(
                        content=f"Tool '{tool_name}' not found.",
                        tool_call_id=tool_id,
                        name=tool_name,
                    )

                )

                continue

            try:

                result = tool_function.invoke(
                    tool_args
                )

            except Exception as e:

                result = f"Tool execution failed: {str(e)}"

            tool_outputs.append(

                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id,
                    name=tool_name,
                )

            )

        return {
            "messages": tool_outputs
        }


# ---------------------------------------------------
# Testing
# ---------------------------------------------------

if __name__ == "__main__":

    from langchain_core.messages import HumanMessage

    agent = MultimediaAgent()

    state = {
        "messages": [
            HumanMessage(
                content="Generate a summary of Artificial Intelligence."
            )
        ]
    }

    response = agent.agent_node(state)

    print("\nAgent Response\n")
    print(response)