# Documentation Sync Setup Guide

This guide explains how to set up automated documentation updates when pySLAMMER releases are published.

## Setup Steps

### 1. Create Personal Access Token

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Create a new token with these permissions:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
3. Copy the token - you'll need it in the next step

### 2. Add Secrets to pySLAMMER Repository

In your pySLAMMER repository settings, add these secrets:

- `DOCS_REPO_TOKEN`: The personal access token from step 1
- `DOCS_REPO_OWNER`: Your GitHub username/organization (e.g., "lornearnold")  
- `DOCS_REPO_NAME`: Your documentation repository name (e.g., "pyslammer-docs")

### 3. Set Up Documentation Repository

1. Copy the workflow file `docs-repo-workflow-example.yml` to your docs repo as:
   ```
   .github/workflows/update-for-pyslammer-release.yml
   ```

2. Customize the workflow for your docs structure:
   - Update file paths in the "Update version references" step
   - Modify the release notes location if needed
   - Adjust the PR template as desired

### 4. Test Directory Structure

The workflow assumes this structure in your docs repo:
```
docs-repo/
├── .github/workflows/
│   └── update-for-pyslammer-release.yml
├── releases/                  # Created automatically
│   └── v1.2.3.md             # Generated release notes
├── mkdocs.yml                 # Optional - version updated here
└── docs/                      # Your documentation files
    └── *.md                   # Version references updated
```

## How It Works

1. **Release Trigger**: When you publish a release in the pySLAMMER repo, the workflow triggers
2. **Cross-Repo Dispatch**: Sends a webhook to your documentation repository
3. **Branch Creation**: Creates a new branch named `release/pyslammer-vX.Y.Z`
4. **Automated Updates**: Updates version references and creates release notes
5. **Pull Request**: Opens a PR for you to review before merging

## Workflow Customization

### Version Reference Updates

The workflow looks for these patterns to update:
- `pySLAMMER vX.Y.Z` → updated to new version
- `pyslammer==X.Y.Z` → updated to new version
- `version: X.Y.Z` in `mkdocs.yml`

Add more patterns in the "Update version references" step as needed.

### Release Notes

Release notes are automatically extracted from the GitHub release and saved to `releases/vX.Y.Z.md`. Customize the template in the "Create release notes file" step.

## Testing

1. Create a test release in pySLAMMER (you can delete it later)
2. Check that the workflow runs in both repositories
3. Verify the PR is created in your docs repo with correct updates

## Troubleshooting

- **Workflow doesn't trigger**: Check that secrets are set correctly
- **Permission errors**: Ensure the PAT has correct permissions
- **Branch already exists**: The workflow will fail if the branch name exists
- **No changes committed**: If no version references are found, no changes will be committed