"""MCP feet Master Server Implementation."""

import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP


def create_server() -> FastMCP:
    """Create and configure the MCP feet Master server."""
    
    # 創建 FastMCP 伺服器實例
    mcp = FastMCP("MCP feet Master")

    @mcp.tool()
    def get_foot_num(rabbits: int, chickens: int) -> dict:
        """
        計算兔子和雞的總腳數。
        
        兔子有4隻腳，雞有2隻腳。
        
        Args:
            rabbits: 兔子的數量
            chickens: 雞的數量
            
        Returns:
            包含計算結果的字典，包括：
            - total_feet: 總腳數
            - rabbit_feet: 兔子的總腳數
            - chicken_feet: 雞的總腳數
            - calculation: 計算過程說明
        """
        # 輸入驗證
        if rabbits < 0:
            raise ValueError("兔子數量不能為負數")
        if chickens < 0:
            raise ValueError("雞的數量不能為負數")
        
        # 計算
        rabbit_feet = rabbits * 4
        chicken_feet = chickens * 2
        total_feet = rabbit_feet + chicken_feet
        
        return {
            "total_feet": total_feet,
            "rabbit_feet": rabbit_feet,
            "chicken_feet": chicken_feet,
            "rabbits": rabbits,
            "chickens": chickens,
            "calculation": f"{rabbits} 隻兔子 × 4 腳 + {chickens} 隻雞 × 2 腳 = {total_feet} 隻腳",
            "formula": f"{rabbits} × 4 + {chickens} × 2 = {total_feet}"
        }

    @mcp.tool()
    def calculate_animals_from_feet(total_feet: int, animal_type: str = "mixed") -> dict:
        """
        根據總腳數反推動物數量（額外功能）。
        
        Args:
            total_feet: 總腳數
            animal_type: 動物類型 ("rabbits", "chickens", "mixed")
            
        Returns:
            可能的動物組合
        """
        if total_feet < 0:
            raise ValueError("總腳數不能為負數")
        
        if animal_type == "rabbits":
            if total_feet % 4 == 0:
                return {
                    "possible": True,
                    "rabbits": total_feet // 4,
                    "chickens": 0,
                    "explanation": f"{total_feet} 隻腳可以是 {total_feet // 4} 隻兔子"
                }
            else:
                return {
                    "possible": False,
                    "explanation": f"{total_feet} 隻腳無法由純兔子組成（兔子有4隻腳）"
                }
        
        elif animal_type == "chickens":
            if total_feet % 2 == 0:
                return {
                    "possible": True,
                    "rabbits": 0,
                    "chickens": total_feet // 2,
                    "explanation": f"{total_feet} 隻腳可以是 {total_feet // 2} 隻雞"
                }
            else:
                return {
                    "possible": False,
                    "explanation": f"{total_feet} 隻腳無法由純雞組成（雞有2隻腳）"
                }
        
        else:  # mixed
            combinations = []
            for rabbits in range(total_feet // 4 + 1):
                remaining_feet = total_feet - (rabbits * 4)
                if remaining_feet % 2 == 0:
                    chickens = remaining_feet // 2
                    combinations.append({
                        "rabbits": rabbits,
                        "chickens": chickens,
                        "verification": rabbits * 4 + chickens * 2
                    })
            
            return {
                "total_feet": total_feet,
                "possible_combinations": combinations,
                "count": len(combinations)
            }

    @mcp.resource("feet://examples")
    def get_examples() -> str:
        """提供計算範例。"""
        return """
# MCP feet Master 使用範例

## 基本計算
- 3隻兔子 + 5隻雞 = 3×4 + 5×2 = 12 + 10 = 22隻腳
- 2隻兔子 + 0隻雞 = 2×4 + 0×2 = 8 + 0 = 8隻腳
- 0隻兔子 + 6隻雞 = 0×4 + 6×2 = 0 + 12 = 12隻腳

## 反推計算
- 20隻腳可能的組合：
  - 5隻兔子 + 0隻雞
  - 3隻兔子 + 4隻雞
  - 1隻兔子 + 8隻雞
  - 0隻兔子 + 10隻雞

## 使用方法
1. 使用 get_foot_num(rabbits, chickens) 計算總腳數
2. 使用 calculate_animals_from_feet(total_feet, animal_type) 反推動物數量
"""

    @mcp.prompt("animal_feet_problem")
    def create_animal_feet_prompt(
        rabbits: int, 
        chickens: int,
        include_explanation: bool = True
    ) -> str:
        """
        生成動物腳數問題的提示模板。
        
        Args:
            rabbits: 兔子數量
            chickens: 雞的數量
            include_explanation: 是否包含解釋
        """
        
        base_prompt = f"""
請解決以下數學問題：

農場裡有 {rabbits} 隻兔子和 {chickens} 隻雞。
請計算總共有多少隻腳？

"""
        
        if include_explanation:
            base_prompt += """
請提供：
1. 計算過程
2. 最終答案
3. 驗證你的計算

記住：
- 每隻兔子有 4 隻腳
- 每隻雞有 2 隻腳
"""
        
        return base_prompt

    return mcp


def main() -> None:
    """Main entry point for running the server."""
    try:
        server = create_server()
        print("🐰🐔 MCP feet Master Server 啟動中...")
        print("📊 可用工具:")
        print("   - get_foot_num(rabbits, chickens): 計算總腳數")
        print("   - calculate_animals_from_feet(total_feet, animal_type): 反推動物數量")
        print("📚 可用資源:")
        print("   - feet://examples: 查看使用範例")
        print("📝 可用提示:")
        print("   - animal_feet_problem: 生成數學問題")
        print()
        print("✅ 伺服器已準備好接受連接!")
        
        # 運行伺服器
        server.run()
        
    except KeyboardInterrupt:
        print("\n👋 伺服器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 伺服器啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()