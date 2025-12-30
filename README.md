# Plex Wrapped

Generate Wrapped-style viewing reports for Plex Media Server users using the Tautulli API.

Check out a demo: https://plex-wrapped.neonvariant.com/wrapped_reports/2025/neonvariant_2025.html

## Features

- Individual user reports with viewing statistics
- User rankings by watch time
- Top watched movies and TV shows with posters
- Peak viewing hours analysis
- Platform breakdown
- Binge session detection
- Watch streak tracking
- Genre analysis
- Server-wide summary statistics
- Monthly or yearly report periods

## Prerequisites

- Python 3.7+
- Plex Media Server
- Tautulli installed and configured
- Tautulli API key
- Plex API token

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/chase-roohms/plex-wrapped.git
cd plex-wrapped
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
touch .env
```

Add the following variables:

```env
TAUTULLI_URL=http://localhost:8181
TAUTULLI_API_KEY=your_tautulli_api_key_here
PLEX_URL=http://localhost:32400
PLEX_API_KEY=your_plex_token_here
```

**Getting API Keys:**

Tautulli API Key:
1. Open Tautulli web interface
2. Go to Settings → Web Interface
3. Scroll to API section
4. Copy your API key

Plex Token:
1. Sign in to Plex Web App
2. Open any media item
3. Click "..." menu → Get Info → View XML
4. Find the `X-Plex-Token` parameter in the URL

### 4. Clear Old Reports

```bash
rm -rf wrapped_reports/2025/*
```

### 5. Generate Reports

```bash
# Generate yearly reports (default)
python generate_wrapped.py

# Generate monthly reports
python generate_wrapped.py --period monthly
```

Reports are generated in `wrapped_reports/YEAR/`.

### 6. View Reports

Open the HTML files in your browser or navigate to the `wrapped_reports/` directory.

## Project Structure

```
plex-wrapped/
├── generate_wrapped.py          # Main script
├── tautulli_client.py           # Tautulli API client
├── wrapped_analytics.py         # Analytics calculations
├── wrapped_html_generator.py    # HTML report generation
├── definitions.py               # Configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── thumbnails/                 # Cached media thumbnails
└── wrapped_reports/            # Generated HTML reports
    └── 2025/                   # Year-specific reports
```

## Configuration

### Tracked Media Types

Modify in [definitions.py](definitions.py):

```python
tracked_media = {'movie', 'episode'}
```

### Report Periods

- **Yearly**: January 1 to current date
- **Monthly**: Previous complete month

## Troubleshooting

### Connection Errors

- Verify Tautulli is running and accessible
- Check URLs in `.env` (no trailing slashes)
- Ensure API keys are valid

### Missing Data

- Verify Tautulli has collected data for the analysis period
- Check Tautulli's history retention settings

### Image Loading Issues

- Ensure `PLEX_URL` and `PLEX_API_KEY` are configured correctly
- Thumbnails are cached in the `thumbnails/` directory

## License

Provided as-is for personal use.

