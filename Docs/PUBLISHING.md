# Publishing to PyPI — One-Time Setup Guide

## How it works

**GitHub Release → GitHub Actions → PyPI**

Automatic. No manual uploads. No API tokens in environment variables.
Uses PyPI's Trusted Publisher (OIDC) — the modern, secure way.

---

## Step 1 — Create a PyPI account

Go to **https://pypi.org/account/register**

---

## Step 2 — Configure Trusted Publisher on PyPI

1. Log in to PyPI
2. Go to **https://pypi.org/manage/account/publishing/**
3. Click **"Add a new pending publisher"**
4. Fill in:

   | Field | Value |
   |---|---|
   | PyPI Project Name | `promptiq` |
   | GitHub Owner | `youssefLabs` |
   | GitHub Repository | `promptvc` |
   | Workflow filename | `publish.yml` |
   | Environment name | `pypi` |

5. Click **Add**

This tells PyPI: "trust GitHub Actions in this repo to publish this package."

---

## Step 3 — Create an Environment on GitHub

1. Go to your repo: **https://github.com/youssefLabs/promptvc**
2. Click **Settings** → **Environments** → **New environment**
3. Name it exactly: `pypi`
4. Leave it empty (no secrets needed — that's the point)
5. Click **Configure environment**

---

## Step 4 — Push the code

```bash
git clone https://github.com/youssefLabs/promptvc
cd promptvc

# Copy all new files (replace existing ones)
cp -r /path/to/promptiq-final/. .

# Commit and push
git add .
git commit -m "feat: PromptIQ v1.0.0 — full rewrite"
git push origin main
```

---

## Step 5 — Create a GitHub Release

1. Go to **https://github.com/youssefLabs/promptvc/releases/new**
2. Click **"Choose a tag"** → type `v1.0.0` → click **"Create new tag"**
3. Title: `v1.0.0 — PromptIQ`
4. Paste the release notes from `RELEASE_NOTES.md`
5. Click **Publish Release**

**That's it.** The GitHub Action will automatically:
- Run tests on Python 3.10, 3.11, 3.12
- Build the wheel and source distribution
- Verify the package
- Upload to PyPI

In 2–3 minutes: `pip install promptiq` works worldwide. ✅

---

## Updating (every future release)

1. Update `version` in `pyproject.toml`
2. `git push`
3. Create a new GitHub Release with the new version tag
4. Done — PyPI updates automatically

---

## Verifying the release

After publishing:
- **https://pypi.org/project/promptiq/** — your package page
- **https://github.com/youssefLabs/promptvc/actions** — workflow run details

---

## Troubleshooting

**"Version already exists"** — PyPI versions are immutable. Bump the version in `pyproject.toml` and create a new release.

**"Trusted publisher not configured"** — Double-check Step 2. The environment name must match exactly (`pypi`).

**"Tests failed"** — Check the Actions tab. Fix the failing test, push, and create a new release with a bumped version.
