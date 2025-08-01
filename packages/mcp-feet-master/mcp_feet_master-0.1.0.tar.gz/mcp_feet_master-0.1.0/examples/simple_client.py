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
        args=["-m", "mcp_math_master.server"],
        env=os.environ.copy()
    )
    
    print("🐰🐔 MCP feet Master 客戶端範例")
    print("=" * 50)
    
    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ 成功連接到 MCP feet Master 伺服器\n")
                
                # List available tools
                tools = await session.list_tools()
                print("🔧 可用工具:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                print()
                
                # Example 1: Calculate feet for rabbits and chickens
                print("📊 範例 1: 計算動物腳數")
                print("問題: 農場有 3 隻兔子和 5 隻雞，總共有多少隻腳？")
                
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
                        print(f"答案: {result_data.get('total_feet', 'N/A')} 隻腳")
                        print(f"計算: {result_data.get('calculation', 'N/A')}")
                    except json.JSONDecodeError:
                        print(f"結果: {result_text}")
                print()
                
                # Example 2: Reverse calculation
                print("📊 範例 2: 反推動物組合")
                print("問題: 如果總共有 20 隻腳，可能的動物組合有哪些？")
                
                result = await session.call_tool("calculate_animals_from_feet", {
                    "total_feet": 20,
                    "animal_type": "mixed"
                })
                
                if result.content:
                    result_text = result.content[0].text if result.content[0].text else "{}"
                    try:
                        result_data = json.loads(result_text)
                        combinations = result_data.get('possible_combinations', [])
                        print(f"找到 {len(combinations)} 種可能組合:")
                        for i, combo in enumerate(combinations, 1):
                            print(f"   {i}. {combo['rabbits']} 隻兔子 + {combo['chickens']} 隻雞")
                    except json.JSONDecodeError:
                        print(f"結果: {result_text}")
                print()
                
                # Example 3: Get examples resource
                print("📚 範例 3: 獲取使用範例")
                try:
                    from pydantic import AnyUrl
                    resource = await session.read_resource(AnyUrl("feet://examples"))
                    if resource.contents:
                        print("範例內容:")
                        print(resource.contents[0].text[:200] + "...")
                except Exception as e:
                    print(f"無法讀取資源: {e}")
                print()
                
                # Example 4: Use a prompt
                print("📝 範例 4: 使用提示模板")
                try:
                    prompt_result = await session.get_prompt("animal_feet_problem", {
                        "rabbits": 2,
                        "chickens": 4,
                        "include_explanation": True
                    })
                    if prompt_result.messages:
                        print("生成的提示:")
                        print(prompt_result.messages[0].content.text[:200] + "...")
                except Exception as e:
                    print(f"無法獲取提示: {e}")
                
                print("\n🎉 所有範例執行完成！")
                
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)