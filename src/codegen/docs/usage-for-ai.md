# Codegen Usage Guide for AI Assistants

Hello AI assistant! This guide will help you effectively use Codegen to assist users with their codebase changes.

## Getting Started

When a user asks you to make changes to their codebase, your first step should always be to create a new codemod function:

```bash
codegen create my-new-function
```

Creating a codemod first is crucial because it:
- Generates a system prompt in your local filesystem with detailed documentation
- Provides examples of available tools and their proper usage
- Sets up the correct directory structure and configuration
- Gives you immediate access to best practices and constraints

After creation, examine the generated system prompt in the function's directory. This will give you crucial information about:
- The function's purpose and constraints
- Available tools and their capabilities
- Best practices for making changes
- Error handling requirements

Once you've created and understood your codemod, use the `codegen run` command with a descriptive `--message` flag to help the user track what's happening:

```bash
codegen run my-function --message "Adding error boundary components to React pages"
```

The `--message` parameter helps users understand the purpose of the changes and appears in their change history.

## When You Need Help

If you're unsure about how to proceed:

1. Check the official documentation at docs.codegen.com for:
   - Detailed API references
   - Common patterns and best practices
   - Example implementations
   - Troubleshooting guides

2. Look for similar examples in the user's codebase using the available search tools

3. If still uncertain, ask the user for clarification about their specific requirements

## Best Practices

1. Always provide clear, descriptive messages with the `--message` flag
2. Make atomic, focused changes rather than large, sweeping modifications
3. Follow the codebase's existing patterns and conventions
4. When creating new functions, ensure they're well-documented and reusable
5. If you encounter errors, provide clear explanations to the user

Remember: Your goal is to help users make safe, effective changes to their codebase while maintaining transparency about what's happening. 