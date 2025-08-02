"""MCP feet Master Server Implementation."""

import sys
from mcp.server.fastmcp import FastMCP


def create_server() -> FastMCP:
    """Create and configure the MCP feet Master server."""
    
    # Create FastMCP server instance
    mcp = FastMCP("MCP feet Master")

    @mcp.tool()
    def get_foot_num(rabbits: int, chickens: int) -> dict:
        """
        Calculate the total number of feet for rabbits and chickens.
        
        Rabbits have 4 feet, chickens have 2 feet.
        
        Args:
            rabbits: Number of rabbits
            chickens: Number of chickens
            
        Returns:
            Dictionary containing calculation results, including:
            - total_feet: Total number of feet
            - rabbit_feet: Total feet from rabbits
            - chicken_feet: Total feet from chickens
            - calculation: Calculation process description
        """
        # Input validation
        if rabbits < 0:
            raise ValueError("Number of rabbits cannot be negative")
        if chickens < 0:
            raise ValueError("Number of chickens cannot be negative")
        
        # Calculate
        rabbit_feet = rabbits * 4
        chicken_feet = chickens * 2
        total_feet = rabbit_feet + chicken_feet
        
        return {
            "total_feet": total_feet,
            "rabbit_feet": rabbit_feet,
            "chicken_feet": chicken_feet,
            "rabbits": rabbits,
            "chickens": chickens,
            "calculation": f"{rabbits} rabbits x 4 feet + {chickens} chickens x 2 feet = {total_feet} feet",
            "formula": f"{rabbits} x 4 + {chickens} x 2 = {total_feet}"
        }

    @mcp.tool()
    def calculate_animals_from_feet(total_feet: int, animal_type: str = "mixed") -> dict:
        """
        Calculate animal count from total feet (bonus feature).
        
        Args:
            total_feet: Total number of feet
            animal_type: Animal type ("rabbits", "chickens", "mixed")
            
        Returns:
            Possible animal combinations
        """
        if total_feet < 0:
            raise ValueError("Total feet cannot be negative")
        
        if animal_type == "rabbits":
            if total_feet % 4 == 0:
                return {
                    "possible": True,
                    "rabbits": total_feet // 4,
                    "chickens": 0,
                    "explanation": f"{total_feet} feet can be {total_feet // 4} rabbits"
                }
            else:
                return {
                    "possible": False,
                    "explanation": f"{total_feet} feet cannot be made with only rabbits (rabbits have 4 feet)"
                }
        
        elif animal_type == "chickens":
            if total_feet % 2 == 0:
                return {
                    "possible": True,
                    "rabbits": 0,
                    "chickens": total_feet // 2,
                    "explanation": f"{total_feet} feet can be {total_feet // 2} chickens"
                }
            else:
                return {
                    "possible": False,
                    "explanation": f"{total_feet} feet cannot be made with only chickens (chickens have 2 feet)"
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
        """Provide calculation examples."""
        return """
# MCP feet Master Usage Examples

## Basic Calculations
- 3 rabbits + 5 chickens = 3x4 + 5x2 = 12 + 10 = 22 feet
- 2 rabbits + 0 chickens = 2x4 + 0x2 = 8 + 0 = 8 feet
- 0 rabbits + 6 chickens = 0x4 + 6x2 = 0 + 12 = 12 feet

## Reverse Calculations
- 20 feet possible combinations:
  - 5 rabbits + 0 chickens
  - 3 rabbits + 4 chickens
  - 1 rabbit + 8 chickens
  - 0 rabbits + 10 chickens

## Usage
1. Use get_foot_num(rabbits, chickens) to calculate total feet
2. Use calculate_animals_from_feet(total_feet, animal_type) to calculate animals from feet
        """

    @mcp.prompt("animal_feet_problem")
    def create_animal_feet_prompt(
        rabbits: int, 
        chickens: int,
        include_explanation: bool = True
    ) -> str:
        """
        Generate animal feet problem prompt template.
        
        Args:
            rabbits: Number of rabbits
            chickens: Number of chickens
            include_explanation: Whether to include explanation
        """
        
        base_prompt = f"""
Please solve the following math problem:

A farm has {rabbits} rabbits and {chickens} chickens.
How many feet are there in total?

"""
        
        if include_explanation:
            base_prompt += """
Please provide:
1. Calculation process
2. Final answer
3. Verify your calculation

Remember:
- Each rabbit has 4 feet
- Each chicken has 2 feet
"""
        
        return base_prompt

    return mcp


def main() -> None:
    """Main entry point for running the server."""
    try:
        server = create_server()
        print("MCP feet Master Server starting...")
        print("Available tools:")
        print("   - get_foot_num(rabbits, chickens): Calculate total feet")
        print("   - calculate_animals_from_feet(total_feet, animal_type): Calculate animals from feet")
        print("Available resources:")
        print("   - feet://examples: View examples")
        print("Available prompts:")
        print("   - animal_feet_problem: Generate math problems")
        print()
        print("Server ready to accept connections!")
        
        # Run server
        server.run()
        
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()