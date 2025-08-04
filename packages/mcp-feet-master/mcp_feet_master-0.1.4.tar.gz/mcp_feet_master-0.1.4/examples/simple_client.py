"""
Simple client example for MCP feet Master.

This example shows how to connect to the MCP feet Master server
and use its tools programmatically.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Main function to demonstrate MCP feet Master usage."""
    
    # Create server parameters
    # In a real deployment, you'd use: "mcp-feet-master"
    # For testing, we use the direct python module
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_feet_master.server"],
        env=os.environ.copy()
    )
    
    print("MCP feet Master Client Example")
    print("=" * 50)
    
    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("Successfully connected to MCP feet Master server\n")
                
                # List available tools
                tools = await session.list_tools()
                print("Available tools:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                print()
                
                # Example 1: Calculate feet for rabbits and chickens
                print("Example 1: Calculate animal feet")
                print("Question: A farm has 3 rabbits and 5 chickens, how many feet in total?")
                
                result = await session.call_tool("get_foot_num", {
                    "rabbits": 3,
                    "chickens": 5
                })
                
                if result.content:
                    import json
                    # Parse the result
                    result_text = result.content[0].text if result.content[0].text else "{}"
                    try:
                        result_data = json.loads(result_text)
                        print(f"Answer: {result_data.get('total_feet', 'N/A')} feet")
                        print(f"Calculation: {result_data.get('calculation', 'N/A')}")
                    except json.JSONDecodeError:
                        print(f"Result: {result_text}")
                print()
                
                # Example 2: Reverse calculation
                print("Example 2: Reverse calculate animal combinations")
                print("Question: If there are 20 feet in total, what are the possible animal combinations?")
                
                result = await session.call_tool("calculate_animals_from_feet", {
                    "total_feet": 20,
                    "animal_type": "mixed"
                })
                
                if result.content:
                    result_text = result.content[0].text if result.content[0].text else "{}"
                    try:
                        result_data = json.loads(result_text)
                        combinations = result_data.get('possible_combinations', [])
                        print(f"Found {len(combinations)} possible combinations:")
                        for i, combo in enumerate(combinations, 1):
                            print(f"   {i}. {combo['rabbits']} rabbits + {combo['chickens']} chickens")
                    except json.JSONDecodeError:
                        print(f"Result: {result_text}")
                print()
                
                # Example 3: Get examples resource
                print("Example 3: Get usage examples")
                try:
                    from pydantic import AnyUrl
                    resource = await session.read_resource(AnyUrl("feet://examples"))
                    if resource.contents:
                        print("Example content:")
                        print(resource.contents[0].text[:200] + "...")
                except Exception as e:
                    print(f"Unable to read resource: {e}")
                print()
                
                # Example 4: Use a prompt
                print("Example 4: Use prompt template")
                try:
                    prompt_result = await session.get_prompt("animal_feet_problem", {
                        "rabbits": 2,
                        "chickens": 4,
                        "include_explanation": True
                    })
                    if prompt_result.messages:
                        print("Generated prompt:")
                        print(prompt_result.messages[0].content.text[:200] + "...")
                except Exception as e:
                    print(f"Unable to get prompt: {e}")
                
                print("\nAll examples completed!")
                
    except Exception as e:
        print(f"Connection failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)