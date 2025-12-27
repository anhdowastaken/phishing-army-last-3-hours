# Phishing Army - New Records Tracker

[![Update New Phishing Records](https://github.com/anhdowastaken/phishing-army-last-3-hours/actions/workflows/update.yml/badge.svg)](https://github.com/anhdowastaken/phishing-army-last-3-hours/actions/workflows/update.yml)

An automated monitoring tool that tracks newly added phishing URLs and domains from the [Phishing Army Extended Blocklist](https://phishing.army/download/phishing_army_blocklist_extended.txt). This lightweight tracker checks for updates every 3 hours and identifies only the newly added malicious entries.

## What It Does

- **3-Hour Monitoring**: Automatically checks for new additions to the Phishing Army blocklist every 3 hours
- **Incremental Tracking**: Identifies only the newly added phishing records since the last check
- **Efficient Updates**: Uses HTTP Last-Modified headers to detect changes before downloading
- **Auto-Commit**: Automatically commits changes to track historical additions
- **Zero Infrastructure**: Runs entirely on GitHub Actions with no server costs

## Why It's Useful

If you need to:
- Stay updated on the latest phishing threats as they're discovered
- Track new malicious URLs/domains in near real-time
- Integrate new phishing entries into your security infrastructure
- Monitor phishing trends and patterns
- Build custom filtering or alerting based on new additions

This tool provides a lightweight, automated solution that runs on GitHub Actions with zero infrastructure costs.

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- GitHub account (for automated 3-hourly updates via Actions)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/anhdowastaken/phishing-army-last-3-hours.git
cd phishing-army-last-3-hours
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

#### Run Locally

Execute the monitoring script:

```bash
python update_and_extract_new.py
```

#### Automated Updates (GitHub Actions)

The workflow runs automatically every 3 hours. You can also trigger it manually:

1. Go to the "Actions" tab in your GitHub repository
2. Select "Update New Phishing Records" workflow
3. Click "Run workflow"

### Output

New records are saved to `phishing_army_NEW_last_3_hours.txt` with the following format:

```
# New records added to Phishing Army Extended Blocklist
# Source: https://phishing.army/download/phishing_army_blocklist_extended.txt
# Last updated: 2025-12-27 22:00:00 UTC
# Blocklist Last-Modified: Thu, 27 Dec 2025 21:45:00 GMT
# Total new records: 15

example-phishing-site.com
malicious-domain.net
phishing-url.org
...
```

Each output file includes:
- Header with source URL
- Timestamp of last update
- Blocklist's Last-Modified timestamp
- Count of new records
- Sorted list of new phishing URLs/domains

## How It Works

1. **HTTP HEAD Check**: Checks the `Last-Modified` header to detect changes
2. **Conditional Download**: Only downloads if the blocklist has been modified
3. **Content Comparison**: Compares cached previous version with current version
4. **Diff Calculation**: Identifies newly added records using set difference
5. **Output Generation**: Saves new records to timestamped output file
6. **State Tracking**: Updates `last_modified.txt` and caches current content
7. **Auto-Commit**: Commits changes to track historical new additions

## File Structure

```
├── update_and_extract_new.py              # Main monitoring script
├── requirements.txt                       # Python dependencies
├── last_modified.txt                      # Last-Modified timestamp (auto-generated)
├── phishing_army_cache.txt                # Cached blocklist (auto-generated)
├── phishing_army_NEW_last_3_hours.txt     # New records (auto-generated)
└── .github/
    └── workflows/
        └── update.yml                     # GitHub Actions workflow
```

## Requirements

Dependencies are listed in `requirements.txt`:
- **GitPython**: Git operations and repository management
- **requests**: HTTP requests to download blocklist

## About Phishing Army

[Phishing Army](https://phishing.army/) maintains an extensive blocklist of phishing URLs and domains, updated regularly to protect users from phishing attacks. This tracker helps you stay informed about new threats as they emerge.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- **[Phishing Army](https://phishing.army/)**: For maintaining the comprehensive phishing blocklist
- Blocklist sourced from [phishing.army](https://phishing.army/download/phishing_army_blocklist_extended.txt)

## License

This project is open source and available for use. Please check the original [Phishing Army](https://phishing.army/) website for their licensing terms regarding the blocklist data.
