import asyncio    
import mcp.types  
import textwrap
from fastmcp import Client  
from fastmcp.client.transports import StreamableHttpTransport   
from fastmcp.client.messages import MessageHandler  
    
class ReportMessageHandler(MessageHandler):    
    def __init__(self, client):    
        self.client = client    
        
    async def on_resource_list_changed(    
        self, notification: mcp.types.ResourceListChangedNotification    
    ) -> None:    
        """Automatically refresh resources when reports are generated."""    
        print("New report available - updating resource list")    
        resources = await self.client.list_resources()    
        for resource in resources:    
             if str(resource.uri).endswith(".md") or str(resource.uri).startswith("report://"):  
                print(f"New report: {resource.name} at {resource.uri}")  
                
                content = await self.client.read_resource(resource.uri)  
                
                if hasattr(content[0], 'text'):  
                    print(f"Report content from {resource.uri}:")  
                    print(content[0].text)  
                
async def main():    
    async def progress_handler(  
        progress: float,   
        total: float | None,   
        message: str | None  
    ) -> None:  
        if total is not None:  
            percentage = (progress / total) * 100  
            print(f"Progress: {percentage:.1f}% - {message or ''}")  
        else:  
            print(f"Progress: {progress} - {message or ''}")  

    transport = StreamableHttpTransport(   
        url="http://localhost:9001/mcp",
        sse_read_timeout=None
    )   
  
    client = Client(  
        transport=transport,   
        progress_handler=progress_handler,   
        timeout=None,   
        init_timeout=0  
    )  
      
    message_handler = ReportMessageHandler(client)  
  
    async with client:  
        client._session_kwargs["message_handler"] = message_handler  
          
        await client.ping()  
        print("Server is reachable")  
  
        tools = await client.list_tools()    
        print(f"Available tools: {[tool.name for tool in tools]}")    

        import sys
        if len(sys.argv) > 1:
            topic = " ".join(sys.argv[1:])
            print(f"Using topic from command line: {topic}")
        else:
            topic = input("Enter research topic: ")
        
        result = await client.call_tool(
            "do_scientific_research", 
            {"topic": topic}, 
            progress_handler=progress_handler
        )  

        if result.data.get('status') == 'failed':
            return

        resources = await client.list_resources()  
        print(f"\nAvailable resources: {len(resources)}")
        
        for resource in resources:  
            content = await client.read_resource(resource.uri)  
            
            report_text = str(content[0])
            
            # danke copilot
            lines = report_text.split('\n')
            for line in lines:
                # Add visual formatting for headers
                if line.startswith('# '):
                    print(f"\n{line[2:].upper()}")
                    print("=" * 60)
                elif line.startswith('## '):
                    print(f"\n{line[3:]}")
                    print("-" * 40)
                elif line.startswith('### '):
                    print(f"\n{line[4:]}")
                elif line.strip():
                    # Wrap long lines for better readability
                    wrapped_lines = textwrap.fill(line.strip(), width=75)
                    print(wrapped_lines)
                else:
                    print()
            
            print("\n" + "="*80)
        
if __name__ == "__main__":    
    asyncio.run(main())
