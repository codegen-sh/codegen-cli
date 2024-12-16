# Codegen CLI

A command-line interface for the Codegen API that helps you transform your code with AI.

## Installation

To install the latest release:

```
~$: pip install codegen-sh
```

To install for development run:

```
~$: pip install -e .
```

## Quick Start

1. Log in to authenticate with Codegen:

```
~$: codegen login
```

This will open your browser to get an authentication token. You can also pass a token directly with `--token`.

2. Initialize `codegen` from within your Git repository:

```
~$: codegen init
```

This creates the necessary folder structure and downloads documentation and examples.

3. Create a codemod:

```
~$: codegen create my-codemod-name --description "delete all my unused functions"
```

This will create a new codemod in the folder `codegen-sh/codemod/my-codemod-name/run.py`

When passed the `--description` argument, a Codegen expert AI will generate this first draft. Therefore, it's helpful to provide as much info as possible.

4. Run your codemod:

Execute this codemod and view output with `codegen run`:

```
~$: codegen run --apply-local
```

`--apply-local` will apply the changes to your current local filesystem.

## Available Commands

- `login` - Authenticate with Codegen
- `logout` - Clear stored authentication
- `init` - Initialize Codegen in your repository
- `create` - Create a new codemod
- `run` - Execute the active codemod
  - `--web` - Open results in web browser
  - `--apply-local` - Apply changes locally
- `expert` - Ask the Codegen AI expert questions
- `profile` - View current user and codemod info
- `set-active` - Select which codemod to run
- `docs-search` - Search documentation and examples

## Project Structure

After initialization, Codegen creates the following structure:

```
codegen-sh/
├── codemods/     # Your codemods live here
├── docs/         # API documentation
└── examples/     # Example codemods
```

## Working with AI

In Cursor composer or chat , type `@codegen-sh` to pull into context relevant docs.

## License

MIT License

Copyright (c) 2024 Codegen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
