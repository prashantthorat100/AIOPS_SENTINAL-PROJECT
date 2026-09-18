# Git & GitHub Workflow Guide — AIOps Sentinel Team

This is our shared guide for how we use GitHub as a team of 4. Read this once fully, then keep it open
as a reference while you work. Everyone should follow the same steps so we don't step on each other's code.

---

## 1. One-Time Setup (do this once, at the start)

1. **Accept the GitHub invite.** P1 (repo owner) has added you as a collaborator on the repo. Check your
   email/GitHub notifications and accept the invite.
2. **Clone the repo to your machine:**
   ```
   git clone https://github.com/prashantthorat100/AIOPS_SENTINAL-PROJECT.git
   cd AIOPS_SENTINAL-PROJECT
   ```
   This downloads the repo *and* automatically links your local folder to the shared repo (called `origin`),
   so `git push`/`git pull` will just work from here on.
3. **Configure your git identity** (if you haven't before), so your commits are attributed to you:
   ```
   git config --global user.name "Your Name"
   git config --global user.email "your_email@example.com"
   ```

---

## 2. Our Branching Strategy (Simple GitHub Flow)

- `main` is always the stable, working version of the project. **Nobody commits to `main` directly.**
- Every task gets its own short-lived branch, created off `main`.
- Branch naming convention: `<your-role>/<phase>-<short-task-name>`
  - Examples: `p1/phase2-kafka-topics`, `p2/phase3-anomaly-baseline`, `p3/phase6-opa-policies`, `p4/phase1-db-schema`
- Once your branch's work is reviewed and merged into `main`, delete the branch.

This keeps `main` deployable at all times and makes it obvious who is doing what and which phase it
belongs to (matches our `todos.md` phases).

---

## 3. The Day-to-Day Workflow (repeat this for every task)

**Step 1 — Update your local main before starting anything new:**
```
git checkout main
git pull origin main
```
Always do this first. It pulls in whatever teammates already merged, so you're never building on stale code.

**Step 2 — Create your branch:**
```
git checkout -b p1/phase3-feature-extraction
```
(Replace with your role/phase/task.) This is your own private copy — nothing you do here affects anyone
else until you merge it back.

**Step 3 — Do your work, then stage and commit:**
```
git add .
git commit -m "Add rate-of-change feature extraction"
```
Commit in small, meaningful chunks with clear messages — not one giant commit at the end.

**Step 4 — Push your branch to GitHub:**
```
git push origin p1/phase3-feature-extraction
```

**Step 5 — Open a Pull Request (PR):**
- Go to the repo on GitHub — you'll see a banner "Compare & pull request." Click it.
- Write a short description of what you did.
- Add a teammate as Reviewer (right sidebar).
- Click "Create pull request."

**Step 6 — Get reviewed and merge:**
- Your reviewer checks the "Files changed" tab and either approves or leaves comments.
- If changes are requested: edit locally → `git add .` → `git commit -m "address review"` → `git push`
  (this automatically updates the same PR — no need to open a new one).
- Once approved, click **"Merge pull request"** on GitHub.

**Step 7 — Clean up:**
```
git checkout main
git pull origin main
git branch -d p1/phase3-feature-extraction
```
Then go back to Step 1 for your next task.

---

## 4. Ground Rules

- **Never push directly to `main`.** Always go through a branch + PR, even for tiny changes.
- **Pull before you branch, every time** — this is the single biggest habit that prevents merge conflicts.
- **Review each other's PRs promptly** — don't let PRs sit for days blocking someone else's next task.
- **Keep commits and PRs scoped to one task** — easier to review, easier to revert if something breaks.
- If you hit a merge conflict or get stuck on a git command, ask in the group chat before force-pushing
  or deleting anything — conflicts are normal and fixable.

---

## 5. Quick Command Cheat Sheet

| What you want to do | Command |
|---|---|
| Get latest main | `git checkout main && git pull origin main` |
| Start a new task | `git checkout -b <role>/<phase>-<task>` |
| See what changed | `git status` |
| Stage all changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push your branch | `git push origin <branch-name>` |
| Switch branches | `git checkout <branch-name>` |
| See branch list | `git branch` |
| Delete a local branch | `git branch -d <branch-name>` |

---

*This guide accompanies the Client Brief and todos.md for the AIOps Sentinel capstone project.*
