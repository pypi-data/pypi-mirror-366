import asyncio
import subprocess
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

nest_asyncio.apply()  # Needed to run interactive python


async def main():
    # Start the server process via stdio using the new package command
    server_params = StdioServerParameters(
        command="mcp-calculator-demo",
        args=[],
        env=None
    )

    # Connect to the server via stdio
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Test all calculator tools
            print("\n=== Testing Calculator Tools ===")
            
            # Test addition
            result = await session.call_tool("add", arguments={"a": 6, "b": 3})
            print(f"6 + 3 = {result.content[0].text}")
            
            # Test subtraction
            result = await session.call_tool("subtract", arguments={"a": 10, "b": 4})
            print(f"10 - 4 = {result.content[0].text}")
            
            # Test multiplication
            result = await session.call_tool("multiply", arguments={"a": 5, "b": 7})
            print(f"5 * 7 = {result.content[0].text}")
            
            # Test division
            result = await session.call_tool("divide", arguments={"a": 15.0, "b": 3.0})
            print(f"15 / 3 = {result.content[0].text}")

            await asyncio.sleep(100)


if __name__ == "__main__":
    asyncio.run(main())