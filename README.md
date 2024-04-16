![goose checker logo](https://raw.githubusercontent.com/AdamPaslawski/goose-checker/main/assets/goose_checker.svg)

# goose-checker
Military Grade Silly Goose Detection

# Quick Start
Navigate to a git repository on your machine
```
export OPENAI_API_KEY=your-api-key-goes-here
goose-checker
```


# Setup

## 1. Installation

via pipx

`pipx install goose-checker`

via pip

`pip install goose-checker`

See your options in the command line.

`goose-checker --help`

## 2. Setting Your API Key

### a. Azure Model Users
If you are using Azure as your provider your API key must be set as
`AZURE_OPENAI_API_API_KEY=your-key-here`

#### b. OpenAI Model Users
If you are using OpenAI as your provider your API key must be set as
`OPENAI_API_KEY=your key here`

### 3. Setting Convenient Environment Variables (optional)
Having to specify settings over and over an be annoying, we provide sensible defaults but we can make this easier by using environment variables

Example:
```
export GOOSE_CHECKER_PROVIDER=azure
export GOOSE_CHECKER_MODEL_NAME=gpt-4
export AZURE_OPENAI_API_VERSION=2023-07-01-preview
export AZURE_OPENAI_BASE_URL=some_azure_base_url
```

You can set these in `~/.bashrc` for convenience


# Usage

## Basic Usage
```
pipx run goose-checker
```
or if you installed with pip

```
goose-checker
```

## Providing Arguments
```
pipx run goose-checker --model gpt-4
```
or if you installed with pip

```
goose-checker --model gpt-4
```