# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated data refresh and maintenance.

## Workflows

### `data-refresh.yml` - Daily Data Refresh

**Purpose**: Automatically refresh mutual fund data daily to keep information up-to-date.

**Schedule**: Daily at 9:00 AM IST (3:30 AM UTC)

**Manual Trigger**: You can also trigger manually from GitHub Actions UI (`workflow_dispatch`)

**Pipeline Steps**:
1. **Phase 1**: Extract data from 5 Groww URLs using Playwright scraper
2. **Phase 2**: Process and chunk documents
3. **Phase 3**: Index chunks in ChromaDB vector database
4. **Validation**: Verify data quality
5. **Commit**: Push updated data to repository

**Requirements**:
- GitHub repository with write permissions
- Python 3.9+ environment
- All dependencies in `requirements.txt`

## Setup Instructions

### 1. Enable GitHub Actions
Go to your repository → Actions tab → Enable GitHub Actions

### 2. Configure Permissions
Ensure GitHub Actions has write permissions:
- Settings → Actions → General
- Workflow permissions → "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests"

### 3. Monitor Workflow Runs
View workflow runs at:
`https://github.com/YOUR_USERNAME/YOUR_REPO/actions`

### 4. Manual Trigger
To run the workflow manually:
1. Go to Actions tab
2. Select "Daily Data Refresh"
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Workflow Status Badges

Add this to your main README.md:

```markdown
![Data Refresh](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/data-refresh.yml/badge.svg)
```

## Troubleshooting

### Workflow Fails

Check the logs in GitHub Actions:
1. Go to Actions tab
2. Click on failed workflow run
3. Expand failed step to see logs

### Common Issues

1. **Playwright Installation Fails**
   - The workflow installs Chromium browser
   - If it fails, the extraction will use cached data

2. **Data Quality Check Fails**
   - Verify Phase 2 generated chunks
   - Check Phase 3 indexed vector database

3. **Git Push Fails**
   - Check repository permissions
   - Ensure `GITHUB_TOKEN` has write access

### Data Update Frequency

- **Automatic**: Daily at 9:00 AM IST
- **Manual**: Anytime via GitHub UI
- **Recommended**: Keep daily schedule for fresh NAV data

## Customization

### Change Schedule

Edit the cron expression in `data-refresh.yml`:

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
```

Cron format: `minute hour day month day-of-week`

Common schedules:
- Daily at 6 AM: `0 1 * * *`
- Every 6 hours: `0 */6 * * *`
- Weekly on Sunday: `0 0 * * 0`

### Skip Auto-Commit

To skip automatic commits, remove or comment out the "Commit Updated Data" step.

### Add Notifications

Add notification steps (Slack, Email, Discord) after the workflow:

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Data refresh completed!"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Security Notes

- No API keys needed for data extraction (public URLs)
- GITHUB_TOKEN is automatically provided by GitHub
- All data committed is public (mutual fund factsheets)
- No PII or sensitive data is involved
