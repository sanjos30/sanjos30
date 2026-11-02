# Setup in GitHub

1. Create a **public** GitHub repository named exactly **sanjos30** under the **sanjos30** account; initialize it without a README if you plan to upload all three files together.
2. Upload `README.md`, `scripts/metrics.py`, and `.github/workflows/metrics.yml` preserving folder structure (or commit using git).
3. In the repository, open **Actions → Refresh engineering metrics → Run workflow**.
4. Wait for a successful run. The action will commit `assets/engineering-metrics.svg`; your profile README then displays it.
5. The workflow refreshes once a day. It also supports manual updates.

No personal access token or third-party stats service is required. The workflow uses the built-in `GITHUB_TOKEN` with a scoped `contents: write` permission. If pushing is blocked, check your repository's Actions workflow permissions/settings.

**Metric definitions:** Contributions are GitHub's rolling-12-month profile calendar count, potentially including private contributions based on your contribution visibility settings. Public source repositories omit forks. Active repositories are public source repositories with a push in the last 90 days. Languages are weighted by bytes of files in these repositories (not commit volume or expertise). Recent projects are based on last push timestamps. Scheduled GitHub Actions workflows may be delayed.
