# First push to GitHub

1. **Create a new repository** on GitHub (e.g. `IdleHunter`). Do not initialize with README if you already have one locally.

2. **Replace placeholder** in README (if forking):
   - This repo: `https://github.com/muratbulat/IdleHunter.git`. For a fork, replace `muratbulat` with your GitHub username.

3. **Ensure secrets are not committed:**
   - `.env` is in `.gitignore` — never add it.
   - Check: `git status` should not list `.env`.

4. **Initialize and push (if not already a git repo):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: IdleHunter v0.1.0"
   git branch -M main
   git remote add origin https://github.com/muratbulat/IdleHunter.git
   git push -u origin main
   ```

5. **If the repo already exists remotely:**
   ```bash
   git remote add origin https://github.com/muratbulat/IdleHunter.git
   git push -u origin main
   ```

6. **Later updates:** Commit, then `git push`.
