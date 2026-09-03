import os
import json
import math

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# ============================================================
# 1. Load API Keys
# ============================================================

load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ============================================================
# 2. Define Tools
# ============================================================

def web_search(query: str) -> str:
    """Search the web using Tavily and return the search result.
    """
    response = tavily.search(query=query,search_depth="basic")
    results = response.get("results", [])
    if not results:
        return "No useful search results were found."

    # Combine the relevant search results into a string
    formatted_results = []
    for result in results:
        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", "")

        formatted_results.append(
            f"Title: {title}\n"
            f"Content: {content}\n"
            f"URL: {url}"
        )
    return "\n\n".join(formatted_results)


def calculate(expression: str) -> str:
    """Calculate a basic mathematical expression.
    """
    try:
        # Allow only basic mathematical characters
        allowed_characters = set("0123456789+-*/().% ")

        if not all(char in allowed_characters for char in expression):
            return "Invalid mathematical expression."

        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Could not calculate the expression: {str(e)}"

# ============================================================
# 3. Tools Object
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the internet for current or factual information. "
                "Use this tool when the user asks about something that "
                "requires web search or up-to-date information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": ("The search query to use when searching the web.")
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Perform basic mathematical calculations such as "
                "addition, subtraction, multiplication, division, "
                "percentages, and expressions using parentheses."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression such as "
                            "'2 * 2', '100 / 5', or '(10 + 5) * 2'."
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# ============================================================
# 4. Tool Mapping
# ============================================================

available_tools = {
    "web_search": web_search,
    "calculate": calculate
}

# ============================================================
# 5. Agent Function
# ============================================================

def run_agent(user_query: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "You have access to two tools: web_search and calculate. "
                "Use web_search when the user needs information from the "
                "internet or current information. "
                "Use calculate for mathematical calculations. "
                "If no tool is required, answer the user directly."
            )
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    # --------------------------------------------------------
    # First LLM call
    # --------------------------------------------------------

    response = groq.chat.completions.create(model="openai/gpt-oss-120b",messages=messages,tools=tools,tool_choice="auto")

    assistant_message = response.choices[0].message

    # Add the assistant's response to conversation
    messages.append(assistant_message)

    # --------------------------------------------------------
    # Check whether the LLM wants to call a tool
    # --------------------------------------------------------

    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_arguments = json.loads(
                tool_call.function.arguments
            )
            # Get the actual Python function
            tool_function = available_tools.get(tool_name)
            if tool_function is None:
                tool_result = f"Unknown tool: {tool_name}"
            else:
                # Execute the Python function
                tool_result = tool_function(**tool_arguments)

            # ------------------------------------------------
            # Add tool result back to conversation
            # ------------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                }
            )

        # ----------------------------------------------------
        # Second LLM call
        # ----------------------------------------------------

        final_response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        return final_response.choices[0].message.content

    # --------------------------------------------------------
    # No tool required
    # --------------------------------------------------------
    return assistant_message.content

# ============================================================
# 6. Main
# ============================================================

if __name__ == "__main__":
    user_query = input("Ask question ❓ : ")

    answer = run_agent(user_query)

    print("\nAssistant 💻 :")
    print(answer)