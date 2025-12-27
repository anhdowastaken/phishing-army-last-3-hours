#!/usr/bin/env python3
"""
Monitor Phishing Army blocklist for new records.
Checks every 3 hours for newly added phishing URLs/domains.
"""

import os
import requests
from datetime import datetime, UTC
from email.utils import parsedate_to_datetime
from git import Repo
from pathlib import Path

# Configuration
BLOCKLIST_URL = "https://phishing.army/download/phishing_army_blocklist_extended.txt"
LAST_MODIFIED_FILE = "last_modified.txt"
CACHE_FILE = "phishing_army_cache.txt"
OUTPUT_FILE = "phishing_army_NEW_last_3_hours.txt"

def parse_http_date(http_date_str):
    """
    Parse HTTP date string to epoch time.
    Returns epoch timestamp as integer.
    """
    if not http_date_str:
        return None

    try:
        dt = parsedate_to_datetime(http_date_str)
        epoch = int(dt.timestamp())
        return epoch
    except (TypeError, ValueError) as e:
        print(f"Warning: Failed to parse date '{http_date_str}': {e}")
        return None

def epoch_to_http_date(epoch):
    """Convert epoch timestamp to HTTP date format."""
    dt = datetime.fromtimestamp(epoch, UTC)
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

def load_last_modified():
    """Load the last modified epoch timestamp from file."""
    if os.path.exists(LAST_MODIFIED_FILE):
        with open(LAST_MODIFIED_FILE, 'r') as f:
            epoch_str = f.read().strip()
            try:
                epoch = int(epoch_str)
                http_date = epoch_to_http_date(epoch)
                print(f"Last modified: {http_date} (epoch: {epoch})")
                return epoch
            except ValueError:
                print(f"Warning: Invalid epoch timestamp in file: {epoch_str}")
                return None
    return None

def save_last_modified(epoch):
    """Save the last modified epoch timestamp to file."""
    with open(LAST_MODIFIED_FILE, 'w') as f:
        f.write(str(epoch))
    http_date = epoch_to_http_date(epoch)
    print(f"Saved last modified: {http_date} (epoch: {epoch})")

def check_last_modified():
    """
    Check the Last-Modified header using HEAD request.
    Returns epoch timestamp or None.
    """
    print(f"Checking Last-Modified header from {BLOCKLIST_URL}")
    response = requests.head(BLOCKLIST_URL, timeout=30)
    response.raise_for_status()

    last_modified_str = response.headers.get('Last-Modified')
    if not last_modified_str:
        print("Warning: No Last-Modified header in response")
        return None

    last_modified_epoch = parse_http_date(last_modified_str)
    if not last_modified_epoch:
        print("Warning: Failed to parse Last-Modified header")
        return None

    print(f"Current Last-Modified: {last_modified_str}")
    print(f"Parsed to epoch: {last_modified_epoch}")

    return last_modified_epoch

def download_blocklist():
    """
    Download the blocklist from Phishing Army.
    Returns content or None on error.
    """
    print(f"Downloading blocklist from {BLOCKLIST_URL}")
    response = requests.get(BLOCKLIST_URL, timeout=60)
    response.raise_for_status()

    print(f"Downloaded {len(response.text)} bytes")
    return response.text

def parse_records(content):
    """Parse records from blocklist content, filtering comments and empty lines."""
    if not content:
        return set()

    records = set()
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            records.add(line)
    return records

def load_cached_content():
    """Load previously cached blocklist content."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return f.read()
    return None

def save_cached_content(content):
    """Save current blocklist content to cache."""
    with open(CACHE_FILE, 'w') as f:
        f.write(content)
    print(f"Cached blocklist content")

def save_new_records(records, last_modified_epoch):
    """Save newly added records to output file."""
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    last_modified_http = epoch_to_http_date(last_modified_epoch) if last_modified_epoch else "Unknown"

    with open(OUTPUT_FILE, 'w') as f:
        f.write(f"# New records added to Phishing Army Extended Blocklist\n")
        f.write(f"# Source: {BLOCKLIST_URL}\n")
        f.write(f"# Last updated: {timestamp}\n")
        f.write(f"# Blocklist Last-Modified: {last_modified_http}\n")
        f.write(f"# Blocklist Last-Modified (epoch): {last_modified_epoch}\n")
        f.write(f"# Total new records: {len(records)}\n\n")

        if records:
            for record in sorted(records):
                f.write(f"{record}\n")
        else:
            f.write("# No new records detected in the last check\n")

    print(f"Saved {len(records)} new records to {OUTPUT_FILE}")

def commit_changes():
    """Commit changes to this repository."""
    try:
        repo = Repo('.')

        files_to_commit = [OUTPUT_FILE, LAST_MODIFIED_FILE, CACHE_FILE]

        # Check if there are changes
        has_changes = False
        for file in files_to_commit:
            if os.path.exists(file) and (repo.is_dirty(path=file) or file in repo.untracked_files):
                has_changes = True
                break

        if has_changes:
            timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
            repo.index.add(files_to_commit)
            repo.index.commit(f'Update new phishing records - {timestamp}')
            print(f"\nCommitted changes")
        else:
            print("\nNo changes to commit")
    except Exception as e:
        print(f"\nError committing changes: {e}")

def main():
    """Main execution function."""
    try:
        print("=" * 60)
        print("Phishing Army - New Records Tracker")
        print("=" * 60)
        print()

        # Load last modified epoch timestamp
        last_modified_epoch = load_last_modified()

        # Check current Last-Modified using HEAD request
        current_last_modified_epoch = check_last_modified()

        if not current_last_modified_epoch:
            print("\nError: Could not determine Last-Modified timestamp")
            return

        # Compare with stored timestamp
        if last_modified_epoch and last_modified_epoch == current_last_modified_epoch:
            print("\nNo changes detected (Last-Modified unchanged)")
            # Still update output file with empty results
            save_new_records(set(), last_modified_epoch)
            commit_changes()
            return

        # Last-Modified has changed, download the blocklist
        print("\nLast-Modified has changed, downloading blocklist...")
        current_content = download_blocklist()

        if not current_content:
            print("\nError: Failed to download blocklist")
            return

        # Parse current records
        current_records = parse_records(current_content)
        print(f"Current blocklist has {len(current_records)} records")

        # Load and parse previous cached content
        previous_content = load_cached_content()
        if previous_content:
            previous_records = parse_records(previous_content)
            print(f"Previous blocklist had {len(previous_records)} records")

            # Find new records
            new_records = current_records - previous_records
            print(f"Found {len(new_records)} new records")
        else:
            print("First run, no previous cache to compare")
            new_records = set()

        # Save results
        save_new_records(new_records, current_last_modified_epoch)

        # Update cache and last modified timestamp
        save_cached_content(current_content)
        save_last_modified(current_last_modified_epoch)

        # Commit changes
        commit_changes()

        print("\n" + "=" * 60)
        print("Process completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during execution: {e}")
        raise

if __name__ == "__main__":
    main()
