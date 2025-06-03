# Twitter Archive Merger - Help Guide

## What This Tool Does

The Twitter Archive Merger combines multiple Twitter data exports into one complete archive. If you've downloaded your Twitter data multiple times (e.g., in 2022, 2023, 2024), this tool merges them into a single archive with all your tweets, images, and data in one place.

**Key Benefits:**
- ✅ Combines multiple Twitter archives into one
- ✅ Removes duplicate tweets and data automatically  
- ✅ Preserves all images, videos, and media files
- ✅ Creates a working archive you can browse in your web browser
- ✅ No data sent to the internet - everything stays on your computer

## How to Use This Tool

### Step 1: Prepare Your Archives
1. Download your Twitter archives from Twitter.com → Settings → Your Account → Download archive
2. Extract each ZIP file into separate folders
3. Each folder should contain `data/`, `assets/`, and `Your archive.html`

### Step 2: Add Archives
1. Click **"Add Archive Folder"**
2. Select each extracted Twitter archive folder
3. Repeat for all your archives - they'll appear in the list

### Step 3: Set Output Location
1. Choose where to save the merged archive (default: `merged_archive`)
2. Make sure you have enough disk space (at least 2x your largest archive)

### Step 4: Merge
1. Click **"Analyze Archives"** to preview what will be merged (optional)
2. Click **"Merge Archives"** to start the process
3. Wait for completion - this can take 5-30 minutes depending on archive size

### Step 5: View Results
1. Click **"Open Output"** or navigate to your output folder
2. Double-click **"Your archive.html"** to view in your browser
3. Browse your complete Twitter history!

## What Gets Merged

- **Tweets** (including retweets, replies)
- **Likes/Favorites**
- **Direct Messages**
- **Followers & Following lists**
- **Profile information**
- **All images and videos**
- **Account settings and preferences**

## System Requirements

- **Python 3.6+** (Python 3.8+ recommended)
- **Storage**: At least 2x the size of your largest archive
- **Memory**: 4GB RAM minimum (8GB+ for large archives)
- **OS**: Windows 10/11, macOS 10.14+, or Linux

## Troubleshooting

### Common Issues

**"Invalid Twitter archive" error:**
- Make sure you selected the correct folder (contains `data/` and `Your archive.html`)
- Verify the ZIP file was fully extracted
- Check that `manifest.js` exists in the `data/` folder

**Tool crashes or runs out of memory:**
- Close other applications to free memory
- Try merging fewer archives at once
- Check available disk space

**Images don't show in final archive:**
- Verify source archives have `data/tweets_media/` folders
- Check that output folder has media directories
- Make sure all ZIP files were completely extracted

**Slow performance:**
- Large archives (50K+ tweets) can take 15-30 minutes
- Use an SSD if available for faster file operations
- Close unnecessary programs during merge

### Performance Expectations

- **Small archives** (< 10K tweets): 1-2 minutes
- **Medium archives** (10K-50K tweets): 5-10 minutes  
- **Large archives** (50K+ tweets): 15-30 minutes

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

## Privacy & Security

- ✅ **Everything runs locally** - no internet connection required
- ✅ **No data is uploaded** anywhere
- ✅ **Original archives remain unchanged**
- ✅ **You control all your data**

The tool only reads your Twitter archives and creates a new combined version on your computer. Nothing is transmitted over the internet.

## Backup Recommendations

- **Keep original archives** as backups
- **Copy merged archive** to external storage
- **Test the merged archive** by opening in browser before deleting originals

## Need More Help?

If you encounter persistent issues:
1. Check the progress log for error messages
2. Verify your archives are properly extracted Twitter downloads
3. Try with a single archive first to test the tool
4. Ensure adequate disk space and memory
