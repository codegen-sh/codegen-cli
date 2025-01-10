# Webhooks in Codegen

Webhooks allow you to automatically run your Codegen functions in response to events like pull requests, pushes, or issue comments. This guide explains how to set up and deploy webhooks for your repository.

## Setting Up Webhooks

Here's a simple webhook that comments on pull requests:

```python
@codegen.webhook('my-pr-greeter')
def run(codebase, pr):
    print("New PR opened!")
    return {
        "success": True,
        "message": "👋 Thanks for opening this PR! I'll review the changes."
    }
```

To make this webhook live:

1. Deploy it to make it available for webhook triggers:
```bash
codegen deploy my-pr-greeter
```

2. Configure the webhook in your GitHub repository:
   - Go to Repository Settings > Webhooks
   - Add new webhook
   - Set Payload URL to: `https://api.codegen.com/v1/webhook`
   - Set Content type to: `application/json`
   - Select events you want to trigger the webhook (e.g., Pull requests, Issues)
   - Add your Codegen webhook secret from `~/.config/codegen-sh/webhook.json`

That's it! Your webhook will now run automatically when PRs are opened.

## Configuration

Create a `codegen.json` file in your repository root to configure webhook behavior:

```json
{
  "webhooks": {
    "my-webhook-function": {
      "events": ["pull_request.opened", "pull_request.synchronize"],
      "paths": ["src/**/*.ts", "src/**/*.tsx"],
      "branches": ["main", "develop"],
      "message": "Automatically updating code patterns"
    }
  }
}
```

### Configuration Options

- `events`: List of GitHub events that trigger the webhook
- `paths`: Optional glob patterns to filter which files trigger the webhook
- `branches`: Optional list of branches to run on
- `message`: Message to use in commit/PR comments
- `labels`: Optional labels to filter PRs/issues that trigger the webhook

## Testing Webhooks

Test your webhook locally before deploying:

```bash
# Test with a sample pull request event
codegen test-webhook my-webhook-function --event pull_request

# Test with a specific event payload
codegen test-webhook my-webhook-function --event-file ./test-payload.json
```

## Monitoring and Logs

Monitor webhook executions:

```bash
# View recent webhook executions
codegen logs my-webhook-function

# Stream logs in real-time
codegen logs my-webhook-function --follow
```

## Best Practices

1. **Security**:
   - Keep your webhook secret secure
   - Use branch protections for production branches
   - Limit webhook access to specific paths when possible

2. **Performance**:
   - Keep webhook functions focused and efficient
   - Use path filters to avoid unnecessary triggers
   - Consider rate limiting for busy repositories

3. **Reliability**:
   - Add error handling for webhook failures
   - Set up notifications for webhook errors
   - Monitor webhook execution times

4. **Maintenance**:
   - Regularly review webhook configurations
   - Keep webhook functions up to date
   - Document webhook behavior in your repository

## Example: Hello World Webhook

Let's create a simple webhook that prints "Hello World" whenever a PR is opened:

1. Create the function:
```bash
codegen create hello-world-webhook
```

2. In the generated function directory, your code should look like:
```python
def run(event):
    print("Hello World!")
    print(f"Event type: {event.type}")
    print(f"Repository: {event.repository}")
    return {
        "success": True,
        "message": "Hello from Codegen webhook!"
    }
```

3. Configure it in `codegen.json`:
```json
{
  "webhooks": {
    "hello-world-webhook": {
      "events": ["pull_request.opened"],
      "message": "Hello World webhook executed!"
    }
  }
}
```

4. Deploy the webhook:
```bash
codegen deploy hello-world-webhook
```

Now, whenever a PR is opened in your repository, the webhook will print "Hello World" and some basic event information. You can view the output in the webhook logs:
```bash
codegen logs hello-world-webhook
```

## Example: Auto-formatting PR Changes

Here's an example of a webhook that automatically formats new code in pull requests:

```json
{
  "webhooks": {
    "auto-format": {
      "events": ["pull_request.opened", "pull_request.synchronize"],
      "paths": ["**/*.{js,ts,jsx,tsx}"],
      "message": "Automatically formatting code",
      "labels": ["needs-formatting"]
    }
  }
}
```

## Troubleshooting

Common issues and solutions:

1. **Webhook not triggering**:
   - Verify webhook configuration in GitHub
   - Check event types are correctly specified
   - Ensure paths match your files
   - Verify branch names are correct

2. **Authentication failures**:
   - Check webhook secret is correctly configured
   - Verify Codegen CLI is authenticated
   - Ensure repository has correct permissions

3. **Execution failures**:
   - Check logs for error messages
   - Verify function dependencies are available
   - Test webhook locally first

For more help, see the [Codegen documentation](https://docs.codegen.com) or contact support. 