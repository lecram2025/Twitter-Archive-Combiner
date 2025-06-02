# Twitter Archive Merger - Installation & Usage Guide

## What This Tool Does

The Twitter Archive Merger combines multiple Twitter data exports into one complete archive. If you've downloaded your Twitter data multiple times (e.g., in 2022, 2023, 2024), this tool merges them into a single archive with all your tweets, images, and data in one place.

**Key Benefits:**
- ✅ Combines multiple Twitter archives into one
- ✅ Removes duplicate tweets and data automatically  
- ✅ Preserves all images, videos, and media files
- ✅ Creates a working archive you can browse in your web browser
- ✅ No data sent to the internet - everything stays on your computer

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Storage**: At least 2x the size of your largest Twitter archive
- **Memory**: 4GB RAM minimum (8GB+ recommended for large archives)

## Installation Instructions

### Step 1: Install Python

#### Windows Users:
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click "Download Python 3.11.x" (latest version)
3. **Important**: Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```
   You should see something like "Python 3.11.5"

#### Mac Users:
**Option A - Using Homebrew (Recommended):**
1. Install Homebrew from [brew.sh](https://brew.sh)
2. Open Terminal and run:
   ```bash
   brew install python
   ```

**Option B - Direct Download:**
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. Verify by opening Terminal and typing:
   ```bash
   python3 --version
   ```

#### Linux Users:
**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

**CentOS/RHEL/Fedora:**
```bash
sudo dnf install python3 python3-pip python3-tkinter
```

### Step 2: Download the Twitter Archive Merger

1. Download the `twitter_archive_merger.py` file
2. Save it to a folder where you want to work (e.g., `Documents/TwitterMerger/`)

### Step 3: Prepare Your Twitter Archives

1. **Download your Twitter archives** from Twitter if you haven't already:
   - Go to Twitter.com → Settings → Your Account → Download archive
   - You'll receive email links to download ZIP files

2. **Extract your archives**:
   - Create a folder called `twitter_archives`
   - Extract each ZIP file into a separate subfolder:
   ```
   twitter_archives/
   ├── april_2022/
   │   ├── data/
   │   ├── assets/
   │   └── Your archive.html
   ├── march_2023/
   │   ├── data/
   │   ├── assets/
   │   └── Your archive.html
   └── december_2024/
       ├── data/
       ├── assets/
       └── Your archive.html
   ```

## Using the Tool

### Step 1: Run the Merger

**Windows:**
1. Open Command Prompt
2. Navigate to where you saved the tool:
   ```
   cd Documents\TwitterMerger
   ```
3. Run the tool:
   ```
   python twitter_archive_merger.py
   ```

**Mac/Linux:**
1. Open Terminal
2. Navigate to the tool location:
   ```bash
   cd ~/Documents/TwitterMerger
   ```
3. Run the tool:
   ```bash
   python3 twitter_archive_merger.py
   ```

### Step 2: Use the Interface

1. **A window will open** with the Twitter Archive Merger interface
2. **Click "Add Archive"** button
3. **Select each Twitter archive folder** (the folder containing `data/`, `assets/`, etc.)
4. **Repeat** for all your archives - you'll see them listed in the window
5. **Click "Merge Archives"** when ready
6. **Choose output location** when prompted

### Step 3: Monitor Progress

The tool will display progress messages:
```
🚀 STARTING MERGE
✅ Added archive: April 2024 archive
✅ Added archive: March 2023 archive
📁 Merging data files...
   tweets: 2,543 items
   likes: 15,678 items
🔄 Removing duplicates...
   likes: removed 234 duplicates
📷 Copying media files...
   Copied 1,247 files
💾 Writing merged files...
✅ Merge complete!
```

### Step 4: View Your Merged Archive

1. **Navigate to the output folder** (default: `merged_archive`)
2. **Double-click "Your archive.html"** to open in your web browser
3. **Browse your complete Twitter history!**

## What Gets Merged

The tool combines these data types:
- **Tweets** (including retweets, replies)
- **Likes/Favorites**
- **Direct Messages**
- **Followers & Following lists**
- **Profile information**
- **All images and videos**
- **Account settings and preferences**

## Troubleshooting

### Common Issues

**"Python is not recognized as an internal or external command"**
- Solution: Reinstall Python and check "Add Python to PATH"

**"Permission denied" errors**
- Solution: Run as administrator (Windows) or use `sudo` (Mac/Linux)

**"No module named 'tkinter'"**
- Linux solution: `sudo apt install python3-tk`
- Mac solution: Reinstall Python from python.org

**Tool crashes or freezes**
- Check available disk space (need 2x archive size)
- Close other programs to free memory
- Try merging fewer archives at once

**Images don't show in final archive**
- Make sure you extracted all ZIP files completely
- Check that media folders exist in source archives
- Verify output folder has `data/tweets_media/` directory

### Getting Help

If you encounter issues:

1. **Check the console output** for error messages
2. **Verify your archives** are properly extracted Twitter downloads
3. **Try with a single archive first** to test the tool
4. **Check disk space** - you need room for the merged result

### Performance Tips

**For Large Archives (50K+ tweets):**
- Close other applications to free memory
- Use an SSD if available for faster file operations
- Merge in smaller batches if needed

**Speed Expectations:**
- Small archives (< 10K tweets): 1-2 minutes
- Medium archives (10K-50K tweets): 5-10 minutes  
- Large archives (50K+ tweets): 15-30 minutes

## File Structure After Merging

Your merged archive will contain:
```
merged_archive/
├── Your archive.html          # Open this in browser
├── data/
│   ├── manifest.js           # Archive configuration
│   ├── tweets.js             # All your tweets
│   ├── likes.js              # All your likes
│   ├── tweets_media/         # All tweet images/videos
│   └── [other data files]
└── assets/                   # Viewer application files
```

## Backup Recommendations

- **Keep original archives** as backups
- **Copy merged archive** to external storage
- **Test the merged archive** by opening in browser before deleting originals

## Privacy & Security

- ✅ **Everything runs locally** - no internet connection required
- ✅ **No data is uploaded** anywhere
- ✅ **Original archives remain unchanged**
- ✅ **You control all your data**

The tool only reads your Twitter archives and creates a new combined version on your computer. Nothing is transmitted over the internet.