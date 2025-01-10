# Creating Functions with AI

The `codegen create` command helps you bootstrap new code transformation functions using AI. Simply describe what you want to do, and Codegen will generate a starter implementation.

## Basic Usage

```bash
codegen create my-function -d "Convert all React class components to functional components"
```

This will:

1. Create a new Python file with your function
2. Generate a starter implementation based on your description
3. Store the AI context in `.codegen-sh/prompts/`

## Command Options

```bash
# Create in current directory (default)
codegen create my-function -d "description"

# Create in specific directory
codegen create my-function src/transforms/ -d "description"

# Create with specific filename
codegen create my-function src/transforms/custom_name.py -d "description"
```

## Generated Files

The command creates:

```
your-chosen-path/
└── my_function.py      # Your function implementation

.codegen-sh/
└── prompts/
    └── my-function-system-prompt.md  # AI context and helpful hints
```

The system prompt (`.md` file) contains valuable context about how the function works and common patterns. When using AI assistants like Cursor:

1. Make sure to feed this file to your AI assistant for better help
2. The assistant will understand the function's purpose and implementation details
3. You'll get more accurate and contextual suggestions

For example in Cursor, you can:
- Drag and drop the `.md` file into the chat
- Use the file picker to select it
- Or reference it in your question

## Example

Let's say you want to create a function to add error boundaries:

```python
import codegen.cli.sdk.decorator
from app.codemod.compilation.models.context import CodemodContext
from app.codemod.compilation.models.pr_options import PROptions
from graph_sitter import PyCodebaseType

@codegen.cli.sdk.decorator.function('add-error-boundaries')
def run(codebase: PyCodebaseType, pr_options: PROptions):
    # Find all React files
    react_files = codebase.find_files("*.tsx", "*.jsx")

    for file in react_files:
        # Find Suspense components
        suspense_nodes = file.find_nodes(
            pattern="<Suspense>$CHILDREN</Suspense>"
        )

        # Wrap them in error boundaries
        for node in suspense_nodes:
            file.wrap(
                node,
                before="<ErrorBoundary>",
                after="</ErrorBoundary>"
            )
```

## AI Assistance

The AI will:

- Analyze your description to understand the intent
- Generate appropriate imports and boilerplate
- Add type hints and documentation
- Include example patterns and helper functions
- Provide comments explaining the approach

## Customizing the Output

You can refine the generated code by:

1. Editing the description (`-d` flag)
2. Modifying the generated code directly
3. Running `codegen create` again with a different description

## Best Practices

1. Be specific in your descriptions
2. Include key details like file types or patterns to match
3. Mention any special cases or edge conditions
4. Review and test the generated code
5. Add your own error handling and edge cases

## Next Steps

After creating a function:

1. Review the generated code
2. Check the system prompt in `.codegen-sh/prompts/my-function-system-prompt.md`:
   - Feed this file to your AI assistant for better help
   - It contains valuable context about the function's purpose and implementation
   - Use it when asking for help or making modifications
3. Test it: `codegen run my-function`
