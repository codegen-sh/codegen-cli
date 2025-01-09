# Creating Codemods with AI

The `codegen create` command helps you bootstrap new codemods using AI. Simply describe what you want to do, and Codegen will generate a starter implementation.

## Basic Usage

```bash
codegen create my-codemod-name -d "Convert all React class components to functional components"
```

This will:

1. Generate a new codemod in `codegen-sh/codemods/my-codemod-name/`
2. Create a starter implementation based on your description
3. Add helpful comments and documentation

## Generated Structure

The command creates a new directory with:

```
codegen-sh/codemods/my-codemod-name/
├── run.py           # Main codemod implementation
└── system-prompt.md # AI context and helpful hints
```

## Example

Let's say you want to create a codemod to add error boundaries:

```bash
codegen create add-error-boundaries -d "Add React error boundaries around Suspense components"
```

This might generate something like:

```python
import codegen
from codegen import Codebase

@codegen.function('add-error-boundaries')
def run(codebase: Codebase):
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

After creating a codemod:

1. Review the generated code in `run.py`
2. Check the hints in `system-prompt.md`
3. Test it: `codegen run my-codemod-name`
4. Deploy it: `codegen deploy codegen-sh/codemods/my-codemod-name/run.py`
