# Running Codemods

The `codegen run` command executes codemods on your codebase. It offers several modes of operation to help you review and apply changes safely.

## Basic Usage

```bash
codegen run my-codemod-name [options]
```

## Run Options

### 1. Preview Mode (Default)

```bash
codegen run my-codemod-name
```

- Shows a diff preview in your terminal
- No changes are made to your filesystem
- Provides a web link to review changes in detail
- Best for reviewing changes before applying them

### 2. Apply Mode

```bash
codegen run my-codemod-name --apply-local
```

- Applies changes directly to your local filesystem
- Creates a git diff you can review
- Requires a clean git state (no uncommitted changes)
- Best for when you're ready to make changes

### 3. Web Mode

```bash
codegen run my-codemod-name --web
```

- Opens the web interface automatically
- Shows side-by-side diff view
- Provides file tree navigation
- Best for reviewing complex changes

### 4. PR Mode

```bash
codegen run my-codemod-name --pr
```

- Creates a pull request with the changes
- Adds description and context
- Assigns reviewers if specified
- Best for team workflows

## Example Workflow

1. Preview changes first:

```bash
codegen run add-error-boundaries
```

2. Review in web interface:

```bash
codegen run add-error-boundaries --web
```

3. Apply when ready:

```bash
codegen run add-error-boundaries --apply-local
```

## Passing Parameters

For codemods that accept parameters:

```bash
codegen run remove-feature-flag --flag-name MY_FLAG --description "Removing old flag"
```

## Output

The command shows:

- Number of files changed
- Preview of the changes (diff)
- Logs from the codemod execution
- Web link for detailed review
- Error messages if any issues occur

## Best Practices

1. Always preview changes first (default mode)
2. Use `--web` for complex changes that need careful review
3. Ensure clean git state before using `--apply-local`
4. Review logs and error messages carefully
5. Use `--pr` for changes that need team review

## Troubleshooting

If `--apply-local` fails:

1. Check for uncommitted changes: `git status`
2. Commit or stash changes: `git stash`
3. Try again
4. Restore changes if needed: `git stash pop`
