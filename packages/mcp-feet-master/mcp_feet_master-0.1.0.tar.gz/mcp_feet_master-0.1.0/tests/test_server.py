"""Tests for MCP feet Master server functionality."""

import pytest
from mcp_math_master.server import create_server


class TestGetFootNum:
    """Test the get_foot_num function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server = create_server()
        # Get the actual function from the server's tools
        tools = {}
        for tool_name, tool_func in self.server._tools.items():
            tools[tool_name] = tool_func
        self.get_foot_num = tools["get_foot_num"]

    def test_basic_calculation(self):
        """Test basic rabbit and chicken calculation."""
        result = self.get_foot_num(3, 5)
        
        assert result["total_feet"] == 22
        assert result["rabbit_feet"] == 12
        assert result["chicken_feet"] == 10
        assert result["rabbits"] == 3
        assert result["chickens"] == 5
        assert "3 隻兔子 × 4 腳 + 5 隻雞 × 2 腳 = 22 隻腳" in result["calculation"]
        assert result["formula"] == "3 × 4 + 5 × 2 = 22"

    def test_only_rabbits(self):
        """Test calculation with only rabbits."""
        result = self.get_foot_num(4, 0)
        
        assert result["total_feet"] == 16
        assert result["rabbit_feet"] == 16
        assert result["chicken_feet"] == 0

    def test_only_chickens(self):
        """Test calculation with only chickens."""
        result = self.get_foot_num(0, 6)
        
        assert result["total_feet"] == 12
        assert result["rabbit_feet"] == 0
        assert result["chicken_feet"] == 12

    def test_zero_animals(self):
        """Test calculation with zero animals."""
        result = self.get_foot_num(0, 0)
        
        assert result["total_feet"] == 0
        assert result["rabbit_feet"] == 0
        assert result["chicken_feet"] == 0

    def test_negative_rabbits(self):
        """Test that negative rabbit count raises ValueError."""
        with pytest.raises(ValueError, match="兔子數量不能為負數"):
            self.get_foot_num(-1, 5)

    def test_negative_chickens(self):
        """Test that negative chicken count raises ValueError."""
        with pytest.raises(ValueError, match="雞的數量不能為負數"):
            self.get_foot_num(3, -2)


class TestCalculateAnimalsFromFeet:
    """Test the calculate_animals_from_feet function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server = create_server()
        tools = {}
        for tool_name, tool_func in self.server._tools.items():
            tools[tool_name] = tool_func
        self.calculate_animals = tools["calculate_animals_from_feet"]

    def test_rabbits_only_valid(self):
        """Test calculation for rabbits only with valid foot count."""
        result = self.calculate_animals(16, "rabbits")
        
        assert result["possible"] is True
        assert result["rabbits"] == 4
        assert result["chickens"] == 0

    def test_rabbits_only_invalid(self):
        """Test calculation for rabbits only with invalid foot count."""
        result = self.calculate_animals(15, "rabbits")
        
        assert result["possible"] is False
        assert "無法由純兔子組成" in result["explanation"]

    def test_chickens_only_valid(self):
        """Test calculation for chickens only with valid foot count."""
        result = self.calculate_animals(12, "chickens")
        
        assert result["possible"] is True
        assert result["rabbits"] == 0
        assert result["chickens"] == 6

    def test_chickens_only_invalid(self):
        """Test calculation for chickens only with invalid foot count."""
        result = self.calculate_animals(13, "chickens")
        
        assert result["possible"] is False
        assert "無法由純雞組成" in result["explanation"]

    def test_mixed_animals(self):
        """Test calculation for mixed animals."""
        result = self.calculate_animals(20, "mixed")
        
        assert result["total_feet"] == 20
        assert len(result["possible_combinations"]) == 4
        
        # Check that all combinations are valid
        for combo in result["possible_combinations"]:
            calculated_feet = combo["rabbits"] * 4 + combo["chickens"] * 2
            assert calculated_feet == 20
            assert combo["verification"] == 20

    def test_negative_feet(self):
        """Test that negative total feet raises ValueError."""
        with pytest.raises(ValueError, match="總腳數不能為負數"):
            self.calculate_animals(-5, "mixed")


class TestServerCreation:
    """Test server creation and configuration."""

    def test_server_creation(self):
        """Test that server can be created successfully."""
        server = create_server()
        
        assert server is not None
        assert server.name == "MCP feet Master"

    def test_server_has_required_tools(self):
        """Test that server has all required tools."""
        server = create_server()
        
        # Check tools are registered
        assert "get_foot_num" in server._tools
        assert "calculate_animals_from_feet" in server._tools

    def test_server_has_resources(self):
        """Test that server has required resources."""
        server = create_server()
        
        # Check resources are registered
        assert any("feet://examples" in str(resource) for resource in server._resources.keys())

    def test_server_has_prompts(self):
        """Test that server has required prompts."""
        server = create_server()
        
        # Check prompts are registered
        assert "animal_feet_problem" in server._prompts


# Integration tests
class TestIntegration:
    """Integration tests for the complete server."""

    def test_typical_use_case(self):
        """Test a typical use case scenario."""
        server = create_server()
        tools = {}
        for tool_name, tool_func in server._tools.items():
            tools[tool_name] = tool_func
        
        # Calculate feet for 2 rabbits and 3 chickens
        result = tools["get_foot_num"](2, 3)
        total_feet = result["total_feet"]
        
        # Verify calculation
        assert total_feet == 14  # 2*4 + 3*2 = 8 + 6 = 14
        
        # Now reverse calculate to find possible combinations
        reverse_result = tools["calculate_animals_from_feet"](total_feet, "mixed")
        
        # Check that original combination is in the results
        original_combo_found = False
        for combo in reverse_result["possible_combinations"]:
            if combo["rabbits"] == 2 and combo["chickens"] == 3:
                original_combo_found = True
                break
        
        assert original_combo_found, "Original combination should be found in reverse calculation"

    def test_edge_cases(self):
        """Test various edge cases."""
        server = create_server()
        tools = {}
        for tool_name, tool_func in server._tools.items():
            tools[tool_name] = tool_func
        
        # Test with large numbers
        result = tools["get_foot_num"](100, 200)
        assert result["total_feet"] == 800  # 100*4 + 200*2
        
        # Test reverse calculation with odd number (should only have chicken solutions)
        odd_result = tools["calculate_animals_from_feet"](7, "mixed")
        for combo in odd_result["possible_combinations"]:
            # All valid combinations should have even number of chickens
            # (since 7 is odd, and rabbits contribute even feet)
            assert (combo["chickens"] % 2) == 1  # Odd chickens for odd total