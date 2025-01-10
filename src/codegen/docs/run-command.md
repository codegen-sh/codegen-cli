# Running Functions

The `codegen run` command executes code transformation functions on your codebase. It can run functions from any Python file or directory in your project.

## Basic Usage

```bash
# Run a function by its label
codegen run my-function

# Run with a message (for PR description)
codegen run my-function --message "Updating error boundaries"

# Apply changes locally
codegen run my-function --apply-local
```

## Command Options

- `--message`: Add a message to describe the changes (used in PR description)
- `--web`: Open results in web browser
- `--apply-local`: Apply changes to your local filesystem

## Example

Let's say you have a function to add error boundaries:

```python
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

You can run it with:

```bash
# Preview changes
codegen run add-error-boundaries

# Apply changes locally
codegen run add-error-boundaries --apply-local

# Create a PR with changes
codegen run add-error-boundaries --message "Adding error boundaries around Suspense"
```

## How It Works

1. The command finds the function by its label
2. Executes it on Codegen's pre-parsed version of your codebase
3. Shows you a preview of the changes
4. Applies them locally or creates a PR based on your options

## Best Practices

1. Always preview changes before applying them
2. Use descriptive messages when creating PRs
3. Test changes on a small subset first
4. Keep functions focused and composable
5. Add error handling for edge cases

## Troubleshooting

If you get errors applying changes:

1. Check for uncommitted changes:
   ```bash
   git status
   ```

2. Either commit your changes:
   ```bash
   git add .
   git commit -m "Save current changes"
   ```

3. Or stash them:
   ```bash
   git stash
   ```

Then try running the command again.
