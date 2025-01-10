# Invoking Functions Programmatically

You can invoke Codegen functions directly from Python code in two ways: using the high-level SDK or making HTTP requests directly.

## Using the SDK

The simplest way is to use the `Function` class from the SDK:

```python
import codegen

# Look up a function by its label
my_function = codegen.Function.lookup('my-function')

# Run it with optional parameters
result = my_function.run(param1="foo", param2="bar")

# Check the results
if result.success:
    print(f"Changes: \n{result.observation}")
    print(f"Web link: {result.web_link}")
else:
    print(f"Error: {result.error}")
```

## Using HTTP Requests

You can also invoke functions by making HTTP requests directly to the Codegen API:

```python
import requests

# Your auth token (from `~/.config/codegen-sh/auth.json`)
AUTH_TOKEN = "your_token_here"

# Your repository details
REPO = "your-org/your-repo"

def run_function(function_name: str, message: str | None = None):
    """Run a function by making HTTP requests directly."""
    response = requests.post(
        "https://api.codegen.com/v1/run",
        headers={
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "input": {
                "repo_full_name": REPO,
                "codemod_name": function_name,
                "message": message,
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        return {
            "success": result["success"],
            "web_link": result.get("web_link"),
            "observation": result.get("observation"),
            "error": result.get("error"),
        }
    else:
        raise Exception(f"Request failed: {response.text}")

# Use it
result = run_function("my-function", message="Updating error boundaries")
```

## Response Format

Both methods return a response with these fields:

```python
{
    "success": bool,        # Whether the run was successful
    "web_link": str,       # URL to view changes in web UI
    "observation": str,    # The diff/changes produced
    "error": str | None,   # Error message if any
    "logs": str | None,    # Logs from the function execution
}
```

## Best Practices

1. **Error Handling**: Always check the `success` field and handle errors gracefully
2. **Messages**: Include descriptive messages for better tracking
3. **Rate Limiting**: Consider adding retries and rate limiting for production use
4. **Auth Security**: Never hardcode auth tokens - use environment variables or secure storage
5. **Validation**: Validate function names and inputs before making requests

## Example: Batch Processing

Here's an example of running a function on multiple repositories:

```python
import codegen

def batch_run(function_name: str, repos: list[str]):
    """Run a function across multiple repositories."""
    function = codegen.Function.lookup(function_name)
    
    results = {}
    for repo in repos:
        try:
            result = function.run(
                repo=repo,
                message=f"Running {function_name} on {repo}"
            )
            results[repo] = {
                "success": result.success,
                "changes": bool(result.observation),
                "error": result.error,
            }
        except Exception as e:
            results[repo] = {
                "success": False,
                "error": str(e),
            }
    
    return results

# Use it
repos = ["org/repo1", "org/repo2", "org/repo3"]
results = batch_run("add-error-boundaries", repos)
```

## Security Considerations

When making programmatic calls:

1. Store auth tokens securely
2. Use HTTPS for all requests
3. Validate and sanitize all inputs
4. Monitor and log API usage
5. Implement proper error handling
6. Consider rate limiting
7. Use timeouts for requests 