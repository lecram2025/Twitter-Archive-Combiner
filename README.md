# Twitter Archive Merger

A Python tool that combines multiple X / Twitter data exports into a single, unified archive with full media preservation and browser compatibility.

## What It Does

If you've downloaded your X / Twitter data multiple times over the years, this tool can merge them into one complete archive containing all your tweets, likes, DMs, followers, and media files.

## Key Features

- **Combines multiple archives** into one unified export including Tweet archives from 2016 onwards!
- **Removes duplicates** automatically across all data types
- **Preserves all media** (images, videos, attachments) present in the archives
- **Maintains viewer compatibility** - works with X / Twitter's browser interface
- **Local processing only** - no data leaves your computer

## How It Works

1. **Load** multiple X /Twitter archive folders
2. **Merge** all data files (tweets, likes, DMs, etc.)
3. **Deduplicate** entries using smart matching
4. **Consolidate** media files with collision handling
5. **Generate** new manifest for browser compatibility

## What Gets Merged

- Tweets, retweets, and replies
- Likes/favorites and bookmarks
- Direct messages and group chats
- Followers and following lists
- Profile data and settings
- All images, videos, and media files

## Requirements

- Python 3.6+ (3.8+ recommended)
- Storage: 2x your largest archive size
- Memory: 4GB+ RAM for large archives

## Quick Start

Download the Zipfile from this page

Install Python if you don't have it

Run in the terminal:

```bash
python twitter_archive_gui.py
```

Then use the GUI to select your archive folders and merge them.

**Result:** A complete `Your archive.html` file you can open in any browser to view your entire Twitter history.

## Documentation

- [Installation & Usage Guide](user_instructions.md) - Detailed setup and usage instructions
- [Technical Documentation](Technical_Documentation.md) - Architecture and implementation details