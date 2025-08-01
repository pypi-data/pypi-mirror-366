# AI Filesystem

A virtual filesystem API for AI agents. Users can easily provide their agents with siloed filesystems to use as long term memory, scratchpads, or general purpose storage.

## How It Works

1. **API Server**: FastAPI backend that stores files in PostgreSQL
2. **User Isolation**: Each user can only see/modify their own files (enforced by database)
3. **Multiple Filesystems**: A user can have multiple filesystems and provide their agents with access to different, or the same filesystems.

## [Beta] Quick Start

### Creating an account on the Filesystem

1. Navigate [here](https://auth.fs.langchain.com) and sign up for an account on the Filesystem. 
2. Create an API key and save it someplace secure!

### Giving your agent access to the Filesystem

1. Set your API key as an environment variable for your agent: `AGENT_FS_API_KEY=<api_key>`
2. Specify the URL for the filesystem. If you're using our hosted solution, it is `AGENT_FS_URL=agent-file-system-production.up.railway.app`
3. Instantiate the filesystem client, and give your agent access to the tools

```python
from ai_filesystem import FilesystemClient

client = FilesystemClient(
  filesystem="nicks-agent-filesystem"
)
filesystem_tools = client.create_tools()  # list files, read file, create new file, and edit file
agent.bind_tools(filesystem_tools)
```

3. In your agent's system prompt, make sure to specify how you want the agent to use the filesystem. Common use cases include as long-term memory, to store learnings and mistakes, or to save work products.