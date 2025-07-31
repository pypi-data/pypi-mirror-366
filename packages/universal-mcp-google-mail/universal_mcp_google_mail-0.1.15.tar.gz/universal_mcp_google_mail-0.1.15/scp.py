from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools import ToolManager
from universal_mcp_google_mail.app import GoogleMailApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="google-mail", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = GoogleMailApp(integration=integration)
tool_manager = ToolManager()
tool_manager.add_tool(app_instance.reply_to_message)
print(tool_manager.list_tools(format="mcp"))


    
  

