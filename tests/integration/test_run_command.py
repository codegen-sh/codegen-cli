from codegen.cli.commands.run.main import run


def test_run_command_success(cli_runner, mock_api_client):
    """Test successful execution of run command"""
    # Setup mock response
    mock_api_client.return_value.run_function.return_value = {"status": "success", "result": "Function executed successfully"}

    # Run the command
    result = cli_runner.invoke(run, ["my-function", "--arg1", "value1"])

    # Assertions
    assert result.exit_code == 0
    assert "Function executed successfully" in result.output
    mock_api_client.return_value.run_function.assert_called_once_with("my-function", {"arg1": "value1"})


def test_run_command_error(cli_runner, mock_api_client):
    """Test error handling in run command"""
    # Setup mock response to simulate an error
    mock_api_client.return_value.run_function.side_effect = Exception("API Error")

    # Run the command
    result = cli_runner.invoke(run, ["my-function"])

    # Assertions
    assert result.exit_code != 0
    assert "Error" in result.output


def test_run_command_with_config(isolated_cli_runner, mock_api_client):
    """Test run command with configuration file"""
    # Create a test config file
    with open("codegen.json", "w") as f:
        f.write('{"default_args": {"key": "value"}}')

    mock_api_client.return_value.run_function.return_value = {"status": "success", "result": "Success"}

    result = isolated_cli_runner.invoke(run, ["my-function"])

    assert result.exit_code == 0
    mock_api_client.return_value.run_function.assert_called_once_with("my-function", {"key": "value"})
