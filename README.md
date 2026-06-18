# Hashnode Agent — LangGraph + MCP Blog Manager

An interactive CLI agent for managing your Hashnode blog via natural language. Uses LangGraph ReAct architecture connected to a Hashnode MCP server, with Groq (LLaMA 3.1) as the LLM. Includes a first-run config wizard that writes credentials to `.env`.

## What It Can Do

- Create and publish blog articles
- Update existing articles
- Search articles by topic
- Fetch your latest publications
- Get Hashnode user profile info
- Test API connectivity

## Architecture

```
User input (CLI)
  → InteractiveHashnodeAgent
      → LangGraph ReAct Agent (Groq LLaMA 3.1 8B)
          └─ MCP Client → Hashnode MCP Server (stdio)
                            └─ Hashnode GraphQL API
```

## Setup

### 1. Install dependencies

```bash
pip install langchain-mcp-adapters langgraph langchain-groq python-dotenv
```

### 2. Configure credentials

On first run the agent will prompt you for:
- `GROQ_API_KEY` — from [console.groq.com](https://console.groq.com)
- `HASHNODE_PERSONAL_ACCESS_TOKEN` — from [hashnode.com/settings/developer](https://hashnode.com/settings/developer)
- `HASHNODE_USERNAME` — your Hashnode handle
- `HASHNODE_HOSTNAME` — your blog domain (e.g. `blog.yourname.hashnode.dev`)

Credentials are saved automatically to `Agent/.env`.

### 3. Run

```bash
python Agent/interactive_hashnode_agent.py
```

## Example Prompts

```
Create a blog post about LangGraph multi-agent systems
Search for articles about RAG
Get my latest articles
Show my Hashnode profile
```

Type `help` for all available commands, `quit` to exit.
