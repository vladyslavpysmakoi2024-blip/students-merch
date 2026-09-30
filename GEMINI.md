# Git & GitHub Safety Policy

- **NEVER execute modifying Git commands** (`git commit`, `git push`, `git pull`, `git checkout`, `git reset`, `git merge`, `git rebase`, `git branch -D`, etc.) autonomously.
- **NEVER call external APIs/tools** that create commits, pull requests, or push branches to GitHub autonomously.
- **Always ask the user for explicit confirmation** before running any modifying Git command, or propose the command as plain text in the chat for the user to review and run manually.
- Read-only inspection commands (`git status`, `git diff`) may be used to verify project state.
