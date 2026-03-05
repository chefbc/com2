# GitHub Pages Deployment Reference

This document describes how the documentation site is deployed to GitHub Pages, including the workflow, branch previews, and configuration requirements.

## Overview

The site is built with MkDocs Material and deployed via GitHub Actions. The workflow supports:

- **Production**: Main site at the root URL when merging to `main`
- **Previews**: Branch-specific preview URLs for review before merging

## URL Structure

| Event | URL |
|-------|-----|
| Merge to `main` | `https://chefbc.github.io/com2/` |
| Push to `feature/add-x` | `https://chefbc.github.io/com2/preview/feature-add-x/` |
| PR from `feature/add-x` (same repo) | Same preview URL |

Branch names with slashes (e.g. `feature/add-x`) are sanitized to hyphens in the URL (`feature-add-x`).

## Deployment Flow

### When you push to a branch (e.g. `feature/add-x`)

1. **Trigger**: Workflow runs on `push`
2. **Branch detection**: Uses `github.ref_name` (e.g. `feature/add-x`)
3. **Config**: Sets `destination_dir` to `preview/feature-add-x`
4. **Build**: MkDocs builds with `site_url` set for the preview path
5. **Checks**: Link checker (if enabled) and Lighthouse run
6. **Deploy**: Content is pushed to `gh-pages` branch under `preview/feature-add-x/`
7. **Preview URL**: Available at `https://chefbc.github.io/com2/preview/feature-add-x/`

### When you open a PR (e.g. `feature/add-x` → `main`)

Same flow as above, but:

- Branch is detected from `github.head_ref` (the PR source branch)
- Deploy runs only for same-repo PRs (skipped for forks due to token permissions)

### When you merge to main

1. **Trigger**: Merge creates a `push` event to `main`
2. **Branch detection**: Uses `github.ref_name` = `main`
3. **Config**: Sets `destination_dir` to empty (root deployment)
4. **Build**: MkDocs builds with `site_url` set for the production URL
5. **Checks**: Link checker and Lighthouse run
6. **Deploy**: Content is pushed to the root of the `gh-pages` branch
7. **Production site**: `https://chefbc.github.io/com2/`

## The gh-pages Branch

The `gh-pages` branch is the **branch GitHub Pages serves from**. It holds the built site output, not the source code.

### Source vs. deployment

- **Source branches** (`main`, `feature/add-x`, etc.): Markdown, `mkdocs.yml`, themes, plugins
- **`gh-pages` branch**: Built HTML, CSS, JS, and assets that GitHub Pages serves

### Layout on gh-pages

```
gh-pages/
├── index.html              ← main site (from main branch)
├── assets/
├── preview/
│   ├── test/               ← preview from test branch
│   │   ├── index.html
│   │   └── ...
│   └── feature-add-x/      ← preview from feature/add-x branch
│       ├── index.html
│       └── ...
```

With `keep_files: true`, deploying `main` to the root does not delete preview folders, and deploying a branch to `preview/...` does not remove the main site or other previews.

## Required GitHub Pages Configuration

**Critical**: The workflow pushes to the `gh-pages` branch. GitHub Pages must be configured to serve from that branch.

In **Settings → Pages** for the repository:

1. Set **Source** to **Deploy from a branch**
2. Set **Branch** to `gh-pages`
3. Set **Folder** to `/ (root)`

If the source is set to **GitHub Actions** (the default for new repos), pushes to `gh-pages` are ignored and the site will 404.

Reference: [Material for MkDocs - Publishing your site](https://squidfunk.github.io/mkdocs-material/publishing-your-site/)

## Workflow Options

### Link checker

The link checker step is optional when manually triggering the workflow:

- **Push/PR**: Runs by default
- **Manual run**: Check the "Run link checker" option to enable (default is off)

### Workflow file

The deployment workflow is defined in [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).

## Troubleshooting

### 404 on preview or main site

1. Verify **Settings → Pages** uses "Deploy from a branch" with `gh-pages`
2. Check the Actions run for the "Deploy to GitHub Pages" step succeeded
3. Inspect the `gh-pages` branch on GitHub for the expected folder structure

### Preview not deployed for fork PRs

PRs from forks cannot push to the base repository. Deploy is skipped for fork PRs; only same-repo PRs get preview deployments.

### Link checker not skipping when set to false

The workflow uses `inputs.run_link_checker == 'true'` because GitHub Actions passes boolean inputs as strings. Ensure the condition compares to the string `'true'`.
