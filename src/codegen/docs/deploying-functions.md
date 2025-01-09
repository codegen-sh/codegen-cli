# Deploying Functions

Deploy code-transformation functions to Codegen Cloud and run them in ~2 seconds on pre-parsed codebases. Functions can be:

- Called as APIs from your code
- Triggered automatically on pull requests
- Run from the CLI for quick transformations
- Shared with your team for reuse

Functions are deployed remotely and execute on Codegen's distributed infrastructure, which maintains a pre-parsed, indexed version of your codebase for instant access.

## Prerequisites

Before you can deploy functions, you need to:

1. Sign up for Codegen Cloud: `codegen auth`
2. Initialize your repository: `codegen init`

Codegen Cloud provides several benefits:

- Serverless infrastructure: Run functions instantly on pre-parsed codebases with zero setup
- Flexible triggers: Invoke via API, webhooks, or automatically on pull requests
- Zero maintenance: No servers to manage, instant deployments, automatic scaling

## Types of Functions

There are two types of functions you can create:

1. Regular functions (using `@codegen.function`)
2. PR check functions (using `@codegen.webhook`)

## Regular Functions

Regular functions are used for code transformations. They can take typed parameters and return a diff of the changes:

```python
import codegen
from codegen import Codebase
from pydantic import BaseModel

class MyParams(BaseModel):
    flag_name: str
    description: str | None = None

@codegen.function('remove-feature-flag')
def run(codebase: Codebase, params: MyParams):
    # Your code transformation logic here
    for file in codebase.files:
        if file.name.endswith('.py'):
            file.edit(f'# Removing flag: {params.flag_name}')
```

## PR Check Functions

PR check functions are special functions that run on pull requests. They can notify specific users and perform checks:

```python
@codegen.webhook('check-suspense-queries', users=['@john', '@jane'])
def run(codebase, pr: PullRequest):
    # Your PR check logic here
    if has_issues(codebase):
        codebase.slack.send_message('@john', pr=pr)
```

## Deploying Functions

To deploy a function:

1. Create a Python file with your function(s)
2. Run `codegen deploy path/to/your/file.py`

The deploy command will:

- Find all functions decorated with `@codegen.function` or `@codegen.pr_check`
- Bundle each function with its dependencies
- Deploy them to Codegen Cloud
- Provide a URL to view and manage the deployment

When you run a deployed function, it executes on Codegen Cloud, which:

- Uses the pre-parsed version of your codebase for faster execution
- Handles large codebases efficiently through distributed processing
- Provides a web interface to view changes before applying them
- Manages authentication and access control for your team

### Function Dependencies

When you deploy a function, Codegen automatically bundles:

- All imports from your module
- Local utility functions used by your main function
- Any nested function dependencies

For example:

```python
import codegen

def check_syntax(code: str) -> bool:
    return True

def validate_file(file):
    return check_syntax(file.content)

@codegen.function('lint-python')
def run(codebase):
    for file in codebase.files:
        validate_file(file)
```

When deployed, this will include both `check_syntax` and `validate_file` functions.

## Using Deployed Functions

Once deployed, you can use your functions in two ways:

1. From Python:

```python
import codegen

# Look up a deployed function
remove_ff = codegen.Function.lookup('remove-feature-flag')

# Run it with parameters
result = remove_ff.run(flag_name='MY_FLAG', description='Removing old flag')
```

2. From the CLI:

```bash
codegen run remove-feature-flag --flag-name MY_FLAG
```

## Best Practices

1. Use descriptive names for your functions that indicate their purpose
2. For PR checks, include relevant team members in the `users` list
3. Break down complex logic into helper functions for better organization
4. Use Pydantic models for type-safe parameters
5. Include docstrings and comments to explain what your function does
