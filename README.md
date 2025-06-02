# Twitter Archive Merger - Technical Documentation

## Overview

The Twitter Archive Merger is a Python utility that combines multiple Twitter data export archives into a single, unified archive. This tool solves the problem of fragmented Twitter data across multiple downloads, creating a complete historical view of your Twitter activity with proper media file handling.

## Core Functionality

### Data Merging Engine

The merger processes Twitter's native archive format, which consists of:
- **JSON data files** containing tweets, likes, DMs, followers, etc.
- **Media directories** containing images, videos, and other attachments
- **Manifest file** that maps data types to their files and media directories
- **Viewer application** (HTML/CSS/JS) for browsing the archive

### Technical Architecture

```
TwitterArchiveMerger
├── Archive Loading & Validation
├── Data Deduplication Engine  
├── Media File Consolidation
├── Manifest Generation
└── Viewer Integration
```

## Data Processing Pipeline

### 1. Archive Discovery & Loading
- Automatically detects Twitter archive folders
- Parses `manifest.js` files to understand data structure
- Validates archive integrity and format compatibility
- Supports both old (`tweet_media`) and new (`tweets_media`) naming conventions

### 2. Data Merging Algorithm
```python
# Pseudo-code for data merging
for each_data_type in all_archives:
    merged_data[data_type] = []
    for archive in source_archives:
        if data_type in archive:
            merged_data[data_type].extend(archive[data_type])
```

Key features:
- **Field normalization**: Maps `tweet` → `tweets` for consistency
- **Chronological ordering**: Preserves temporal relationships
- **Memory efficient**: Streams large datasets without loading everything into RAM

### 3. Deduplication Engine

Uses composite key matching to identify duplicates:

**Tweet deduplication:**
```python
duplicate_key = (tweet_id, creation_date, full_text_hash)
```

**Message deduplication:**
```python
duplicate_key = (conversation_id, timestamp, text_hash, sender_id)
```

**Social graph deduplication:**
```python
duplicate_key = (user_id, account_handle)  # for follows/followers
```

### 4. Media File Consolidation

**Filename collision handling:**
- Detects identical files using size + modified date comparison
- Renames conflicts with incremental suffixes: `image.jpg` → `image_1.jpg`
- Maintains referential integrity between data and media files

**Directory structure normalization:**
```
data/
├── tweets_media/          # Unified tweet images/videos
├── direct_messages_media/ # DM attachments  
├── profile_media/         # Profile pictures, banners
└── [other_media_types]/   # Additional media categories
```

### 5. Manifest Generation

Creates a new `manifest.js` with:
- **Data type registry**: Maps each data category to its files
- **Media directory links**: Connects data types to their media folders
- **File metadata**: Counts, sizes, global variable names
- **Viewer compatibility**: Ensures proper loading in Twitter's viewer

Critical manifest entries:
```javascript
{
  "tweets": {
    "files": [{"fileName": "data/tweets.js", "globalName": "YTD.tweets.part0"}],
    "mediaDirectory": "data/tweets_media"
  },
  "tweetsMedia": {
    "mediaDirectory": "data/tweets_media"  // Required for viewer
  }
}
```

## File Format Compatibility

### Supported Archive Versions
- **Legacy format**: `data/tweet.js` with `data/tweet_media/`
- **Current format**: `data/tweets.js` with `data/tweets_media/`
- **Mixed archives**: Automatically normalizes to current format

### JavaScript Data Structure
Twitter archives use this format:
```javascript
window.YTD.tweets.part0 = [
  {
    "tweet": {
      "id": "1234567890",
      "full_text": "Hello world!",
      "created_at": "2023-01-01T12:00:00.000Z",
      // ... additional fields
    }
  }
]
```

## Performance Characteristics

### Memory Usage
- **Streaming processing**: Handles archives larger than available RAM
- **Incremental deduplication**: O(n) memory complexity for duplicate detection
- **Chunked file operations**: Processes media files in batches

### Time Complexity
- **Data merging**: O(n × m) where n = records, m = archives
- **Deduplication**: O(n log n) with hash-based indexing
- **Media copying**: O(f) where f = total file count

### Scalability Limits
- **Maximum archives**: Limited by available disk space
- **Record limits**: Tested with 100K+ tweets, 1M+ likes
- **Media files**: Handles 10K+ images per archive

## Error Handling & Recovery

### Validation Checks
- Archive format verification
- Manifest schema validation  
- File system permissions
- Disk space requirements

### Graceful Degradation
- Continues processing if individual archives are corrupted
- Skips unreadable media files with logging
- Generates partial manifests when possible

### Logging System
Comprehensive progress tracking:
```
🚀 STARTING MERGE
✅ Added archive: April 2024 archive  
📁 Merging data files...
🔄 Removing duplicates...
📷 Copying media files...
💾 Writing merged files...
✅ Merge complete!
```

## Integration Points

### Twitter Viewer Compatibility
- Maintains full compatibility with Twitter's official viewer
- Preserves all viewer features: search, filtering, date navigation
- Supports media playback and high-resolution image viewing

### Export Format
The merged archive can be:
- Opened directly in any web browser
- Re-archived for backup/sharing
- Further processed by other Twitter analysis tools

## Technical Dependencies

### Core Libraries
- **pathlib**: Modern file system operations
- **json**: Archive data parsing and generation
- **shutil**: High-performance file copying
- **tkinter**: Cross-platform GUI framework
- **datetime**: Timestamp handling and validation

### Python Version Support
- **Minimum**: Python 3.6 (pathlib support)
- **Recommended**: Python 3.8+ (performance optimizations)
- **Tested**: Python 3.8, 3.9, 3.10, 3.11

## Security Considerations

### Data Privacy
- **Local processing**: No data transmitted to external servers
- **File permissions**: Respects system access controls
- **Memory management**: Sensitive data cleared after processing

### Input Validation
- Path traversal protection
- Archive format verification
- Malicious file detection (basic)

This technical foundation ensures reliable, efficient merging of Twitter archives while maintaining full compatibility with Twitter's viewer ecosystem.