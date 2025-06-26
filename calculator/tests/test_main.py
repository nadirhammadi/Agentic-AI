import pytest
from unittest.mock import patch
from calculator.main import main
from pkg.calculator import Calculator
from pkg.render import render

# Mock the render function for testing purposes
@patch('main.render')
def test_main_success(mock_render):
    """Test successful execution of main function with valid input."""
    mock_render.return_value = "Expression: 2 + 2 = 4"
    with patch('sys.argv', ['main.py', '2 + 2']):
        main()
        mock_render.assert_called_once_with('2 + 2', 4)

@patch('main.render')
def test_main_failure(mock_render):
    """Test error handling when an invalid expression is provided."""
    mock_render.side_effect = Exception("Invalid Expression")
    with patch('sys.argv', ['main.py', '2 ++ 2']):
        with pytest.raises(Exception) as excinfo:
            main()
        assert str(excinfo.value) == "Error: Invalid Expression"

@patch('sys.argv', ['main.py'])
def test_main_no_args():
    """Test the behaviour when no arguments are passed."""
    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("Calculator App")
        mock_print.assert_any_call('Usage: python main.py "<expression>"')
        mock_print.assert_any_call('Example: python main.py "3 + 5"')


def test_calculator_evaluate():
    """Test Calculator.evaluate method with various expressions."""
    calculator = Calculator()
    assert calculator.evaluate("2 + 2") == 4
    assert calculator.evaluate("10 - 5") == 5
    assert calculator.evaluate("4 * 2") == 8
    assert calculator.evaluate("10 / 2") == 5.0
    assert calculator.evaluate("10 // 2") == 5
    assert calculator.evaluate("10 % 3") == 1
    assert calculator.evaluate("2 ** 3") == 8
    with pytest.raises(Exception) as excinfo:
      calculator.evaluate("2 +")
    assert "Invalid Expression" in str(excinfo.value)


def test_render_function():
    """Test render function with different inputs."""
    assert render("2 + 2", 4) == "Expression: 2 + 2 = 4"
    assert render("10 - 5", 5) == "Expression: 10 - 5 = 5"
    assert render("Invalid Expression", "Error") == "Expression: Invalid Expression = Error" #Handles error gracefully



def test_edge_cases_calculator():
    """Test Calculator with edge cases."""
    calculator = Calculator()
    assert calculator.evaluate("0 + 0") == 0  # Zero values
    assert calculator.evaluate("10 - 10") == 0  # Subtraction resulting in zero
    assert calculator.evaluate("0 * 5") == 0  # Multiplication with zero
    with pytest.raises(ZeroDivisionError): # Division by zero
        calculator.evaluate("5 / 0")
    assert calculator.evaluate("10 // 0") == "Division by zero is not allowed" # Integer division by zero
    with pytest.raises(Exception) as excinfo: # Handle invalid expression gracefully
        calculator.evaluate("2 + + 2")
    assert "Invalid Expression" in str(excinfo.value)
    with pytest.raises(Exception) as excinfo: # Handle invalid expression gracefully
        calculator.evaluate("abc")
    assert "Invalid Expression" in str(excinfo.value)