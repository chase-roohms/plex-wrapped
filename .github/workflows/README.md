# GitHub Actions Workflows

## generate-wrapped.yml

This workflow automatically generates Plex Wrapped reports and deploys them to GitHub Pages.

### Triggers
- **Push to main**: Runs automatically when code is pushed to the main branch
- **Manual (workflow_dispatch)**: Can be triggered manually from the Actions tab

### Required Secrets
Configure these in Settings → Secrets and variables → Actions:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TAUTULLI_URL` | Your Tautulli server URL | `http://localhost:8181` |
| `TAUTULLI_API_KEY` | Tautulli API key | `abc123...` |
| `PLEX_URL` | Your Plex server URL | `http://localhost:32400` |
| `PLEX_API_KEY` | Plex authentication token | `xyz789...` |

### Workflow Steps

1. **Checkout repository** - Clones the repo
2. **Set up Python 3.13** - Installs Python with pip caching
3. **Install dependencies** - Installs packages from `requirements.txt`
4. **Generate wrapped reports** - Runs `generate_wrapped.py` with environment variables
5. **Update index.html** - Runs `update_index.py` to regenerate the index page
6. **Commit and push changes** - Commits generated reports back to the repo (with `[skip ci]` to prevent loops)
7. **Upload artifact** - Prepares files for GitHub Pages deployment
8. **Deploy to GitHub Pages** - Publishes the site

### Notes

- The commit message includes `[skip ci]` to prevent infinite workflow loops
- Reports are organized in `wrapped_reports/YEAR/` subdirectories
- The workflow requires GitHub Pages to be enabled with "GitHub Actions" as the source
- All generated HTML files include noindex meta tags for privacy
