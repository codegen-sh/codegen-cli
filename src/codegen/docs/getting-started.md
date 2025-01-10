# Getting Started with Codegen

Welcome to Codegen! This guide will help you get up and running with our AI-powered code transformation tool.

## Installation

Installing Codegen is simple:

```bash
pipx install codegen-sh
```

Don't have `pipx`? You can install it with:
```bash
python -m pip install --user pipx
pipx ensurepath
```

## Quick Start Guide

### 1. Authentication

First, let's authenticate with Codegen:

```bash
codegen login
```

This will open your browser where you can securely log in. Your authentication will be saved for future use.

### 2. Set Up Your Project

Navigate to your project's directory and initialize Codegen:

```bash
codegen init
```

This creates a `codegen-sh` directory in your project with everything you need to start using Codegen.

### 3. Making Your First Change

Let's say you want to update error handling in your codebase. Here's how:

1. Create a new function:
```bash
codegen create add-error-handling --description "Add try-catch blocks around async functions"
```

2. Run it:
```bash
codegen run add-error-handling
```

By default, this will show you the proposed changes without applying them. To apply the changes:
```bash
codegen run add-error-handling --apply-local
```

## Key Features

- **AI-Powered Transformations**: Describe what you want to change in plain English
- **Safe by Default**: Review changes before they're applied
- **Web Interface**: Use `--web` to view and manage changes in your browser
- **Version Control Aware**: Works seamlessly with Git
- **AI Assistant**: Get help anytime with `codegen expert`

## Common Commands

- `codegen run <function-name>` - Run a function
  - Add `--web` to view results in browser
  - Add `--apply-local` to apply changes to your files
- `codegen expert` - Chat with the AI expert about your code
- `codegen list` - View available functions
- `codegen docs-search` - Search documentation and examples

## Working with AI

Codegen comes with a built-in AI expert. Ask it anything about your code:

```bash
codegen expert "How can I update all my React components to use hooks?"
```

The AI will help you:
- Understand your codebase
- Create and modify functions
- Debug issues
- Find the right approach for your changes

## Deploying Your Functions

Once you've created and tested your functions locally, you can deploy them to make them available for others or for use in webhooks:

```bash
# Deploy a specific function by name
codegen deploy --label my-function

# Deploy all functions in a directory
codegen deploy --path ./my-functions

# Deploy all functions in current directory
codegen deploy
```

After deployment, you'll get:
- A confirmation message
- The deployment time
- A web link to view your deployment

This is especially useful when:
- Setting up webhooks for GitHub integration
- Sharing functions with your team
- Making functions available for automated runs
- Setting up CI/CD pipelines

## Examples

Here are some common use cases:

1. **Updating Dependencies**
```bash
codegen create update-deps --description "Update all package versions to latest stable"
```

2. **Code Style Changes**
```bash
codegen create convert-style --description "Convert CSS-in-JS to Tailwind classes"
```

3. **API Updates**
```bash
codegen create update-api --description "Update axios calls to use the new API endpoints"
```

## Best Practices

1. **Start Small**: Begin with simple, focused changes
2. **Review Changes**: Always check the proposed changes before applying
3. **Use Version Control**: Make sure your changes are committed before running Codegen
4. **Be Specific**: Give clear, detailed descriptions when creating functions
5. **Test First**: Use `--web` to review changes before applying them

## Getting Help

- Use `codegen expert` for AI assistance
- Run `codegen docs-search` to find documentation
- Visit [docs.codegen.com](https://docs.codegen.com) for detailed guides
- Add `--help` to any command for usage information

## Next Steps

- Try creating your first function with `codegen create`
- Explore example functions in the `codegen-sh/examples` directory
- Check out our [documentation](https://docs.codegen.com) for detailed guides
- Join our community to share and learn from others

Remember: Codegen is designed to be safe and helpful. Don't hesitate to experiment - you can always review changes before applying them! 