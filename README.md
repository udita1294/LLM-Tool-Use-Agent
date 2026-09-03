#  Groq Tool-Calling AI Agent

A lightweight AI agent built with **Python, Groq, Tavily, and LLM tool calling**.

The agent can intelligently decide whether to answer a user's question directly or use an external tool. Currently, it supports:

*  **Web Search** using Tavily
*  **Mathematical Calculations** using a custom Python tool
*  **LLM-powered tool selection** using Groq
*  **Multi-step tool-calling workflow**

---

##  Overview

Traditional LLM applications usually generate an answer directly from the model.

This project demonstrates a more agentic approach:

```text
                    User Query
                        │
                        ▼
                ┌───────────────┐
                │   Groq LLM    │
                │   GPT-OSS     │
                └───────┬───────┘
                        │
                 Decide what to do
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       No Tool Needed         Tool Required
             │                     │
             │              ┌──────┴──────┐
             │              │             │
             │              ▼             ▼
             │         Web Search    Calculator
             │          (Tavily)      (Python)
             │              │             │
             │              └──────┬──────┘
             │                     │
             │               Tool Result
             │                     │
             └──────────────┬──────┘
                            ▼
                    Final LLM Response
```

The LLM determines which tool should be used based on the user's query.

For example:

```text
User:
What is 25 * 48?

LLM → calculate tool
     → 1200
     → LLM generates final response
```

While:

```text
User:
What are the latest developments in artificial intelligence?

LLM → web_search tool
     → Tavily search results
     → LLM summarizes the results
```

---

#  Features

### 1. LLM Tool Calling

The project uses Groq's chat completion API with function/tool calling.

The model receives descriptions of the available tools and decides when a tool is necessary.

```python
response = groq.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

---

### 2. Web Search

The agent can search the internet using **Tavily**.

```python
def web_search(query: str) -> str:
    response = tavily.search(
        query=query,
        search_depth="basic"
    )
```

The search results are then returned to the LLM so it can generate a final answer.

---

### 3. Mathematical Calculator

A custom calculator tool handles basic mathematical expressions.

Examples:

```text
2 + 2
100 / 5
(10 + 5) * 2
25 * 48
```

The calculator also validates the input before evaluating the expression.

---

### 4. Automatic Tool Selection

The user does not need to explicitly tell the agent which tool to use.

For example:

```text
Calculate 150 * 24
```

automatically triggers:

```text
calculate()
```

while:

```text
Who is the current CEO of NVIDIA?
```

can trigger:

```text
web_search()
```

---

### 5. Two-Step Agent Workflow

The project follows a simple but important agentic loop:

**Step 1 — LLM decides**

```text
User Query
    ↓
LLM
    ↓
Tool Call
```

**Step 2 — Execute tool and return result**

```text
Tool
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

This demonstrates the fundamental architecture behind many modern LLM agents.

---

#  Tech Stack

| Technology    | Purpose                         |
| ------------- | ------------------------------- |
| Python        | Core programming language       |
| Groq          | LLM inference and tool calling  |
| GPT-OSS-120B  | Language model                  |
| Tavily        | Web search                      |
| python-dotenv | Environment variable management |

---

#  Project Structure

```text
groq-tool-calling-agent/
│
├── main.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

#  How Tool Calling Works

The available tools are described to the LLM using a structured schema.

For example:

```python
{
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Perform basic mathematical calculations.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string"
                }
            },
            "required": ["expression"]
        }
    }
}
```

The model can then return a tool call such as:

```text
calculate
{
    "expression": "25 * 48"
}
```

The Python application executes the actual function:

```python
tool_function = available_tools.get(tool_name)

tool_result = tool_function(**tool_arguments)
```

The result is then added to the conversation:

```python
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": tool_result
})
```

Finally, the LLM receives the tool result and generates the user-facing response.

---

#  Agent Execution Flow

```text
                  ┌──────────────┐
                  │    User      │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   Groq LLM   │
                  └──────┬───────┘
                         │
                  Tool required?
                    /          \
                  No            Yes
                  │              │
                  │        Select tool
                  │          /       \
                  │         /         \
                  │        ▼           ▼
                  │   Web Search   Calculator
                  │        │           │
                  │        └─────┬─────┘
                  │              │
                  │        Tool Result
                  │              │
                  └───────┬──────┘
                          ▼
                   ┌──────────────┐
                   │   Groq LLM   │
                   └──────┬───────┘
                          │
                          ▼
                   Final Response
```

---

#  Security Considerations

The calculator validates mathematical expressions before evaluation.

Only the following characters are allowed:

```text
0123456789
+
-
*
/
(
)
.
%
space
```

This prevents arbitrary Python code from being passed to `eval()`.

API keys are loaded through environment variables rather than being hardcoded into the source code.

---

#  What This Project Demonstrates

This project demonstrates practical understanding of:

* Large Language Models
* LLM APIs
* Function calling
* Tool calling
* AI agents
* Agent execution loops
* Prompt design
* Structured tool schemas
* External API integration
* Web search integration
* Environment variable management
* Python backend development
