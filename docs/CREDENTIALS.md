# Shared Credentials

**For team use only. Do not share outside this project.**

## Setup Instructions

Copy and paste these commands into your terminal to configure your environment:

```bash
# OpenAI API Key
export OPENAI_API_KEY="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"

# LangSmith Tracing
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="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"
export LANGCHAIN_PROJECT="MentorAI-Eval"
```

## Persistent Setup (Optional)

To avoid re-exporting every session, add the commands above to your shell profile:

- **macOS/Linux (zsh):** `~/.zshrc`
- **macOS/Linux (bash):** `~/.bashrc`

Then restart your terminal or run `source ~/.zshrc`.

## Verifying Setup

After configuring, run:

```bash
python run_eval.py --persona nell --turns 3
```

Check that traces appear at [smith.langchain.com](https://smith.langchain.com) in the **MentorAI-Eval** project.
