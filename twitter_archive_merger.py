#!/usr/bin/env python3
"""
Twitter Archive Merger - Backend Logic
Contains the core analyzer and merger classes.
"""

import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib


class TwitterArchiveAnalyzer:
    """Analyzes Twitter archive structure and content"""

    def __init__(self, archive_path):
        self.archive_path = Path(archive_path)
        self.manifest_data = None

    def load_manifest(self):
        """Load and parse the manifest.js file"""
        possible_paths = [
            self.archive_path / "data" / "manifest.js",
            self.archive_path / "manifest.js",
            self.archive_path / "js" / "manifest.js",
        ]

        manifest_path = None
        for path in possible_paths:
            if path.exists():
                manifest_path = path
                break

        if not manifest_path:
            raise FileNotFoundError(f"No manifest.js found in {self.archive_path}")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'window\.__THAR_CONFIG\s*=\s*({.*});?', content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse manifest.js")

        self.manifest_data = json.loads(match.group(1))
        return self.manifest_data

    def get_archive_info(self):
        """Get basic info about this archive"""
        if not self.manifest_data:
            self.load_manifest()

        user_info = self.manifest_data.get('userInfo', {})
        archive_info = self.manifest_data.get('archiveInfo', {})

        return {
            'username': user_info.get('userName', 'unknown'),
            'display_name': user_info.get('displayName', 'unknown'),
            'account_id': user_info.get('accountId', 'unknown'),
            'generation_date': archive_info.get('generationDate', 'unknown'),
            'size_bytes': int(archive_info.get('sizeBytes', 0)),
            'is_partial': archive_info.get('isPartialArchive', True),
        }

    def analyze_data_types(self):
        """Analyze what data types exist and their counts"""
        if not self.manifest_data:
            self.load_manifest()

        data_types = self.manifest_data.get('dataTypes', {})
        analysis = {}

        for data_type, info in data_types.items():
            files = info.get('files', [])
            total_count = sum(int(f.get('count', 0)) for f in files)

            if total_count > 0:
                analysis[data_type] = {
                    'total_count': total_count,
                    'has_media': info.get('mediaDirectory') is not None
                }

        return analysis

    @staticmethod
    def is_valid_archive(archive_path):
        """Check if a path contains a valid Twitter archive"""
        archive_path = Path(archive_path)
        
        # Check for required files/folders
        required_items = [
            archive_path / "data",
            archive_path / "Your archive.html"
        ]
        
        # Check for manifest in possible locations
        manifest_paths = [
            archive_path / "data" / "manifest.js",
            archive_path / "manifest.js",
        ]
        
        has_manifest = any(path.exists() for path in manifest_paths)
        has_required = all(item.exists() for item in required_items)
        
        return has_manifest and has_required


class TwitterArchiveMerger:
    """Merges multiple Twitter archives into one unified archive"""

    def __init__(self, output_path, progress_callback=None):
        self.output_path = Path(output_path)
        self.source_archives = []
        self.merged_data = defaultdict(list)
        self.progress_callback = progress_callback or (lambda x: None)

    def log_progress(self, message):
        """Log progress message"""
        self.progress_callback(message)

    def add_archive(self, archive_path):
        """Add an archive to be merged"""
        archive_path = Path(archive_path)

        # Find manifest
        possible_paths = [
            archive_path / "data" / "manifest.js",
            archive_path / "manifest.js",
        ]

        manifest_path = None
        for path in possible_paths:
            if path.exists():
                manifest_path = path
                break

        if not manifest_path:
            raise FileNotFoundError(f"No manifest.js found in {archive_path}")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'window\.__THAR_CONFIG\s*=\s*({.*});?', content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse manifest.js in {archive_path}")

        manifest_data = json.loads(match.group(1))

        self.source_archives.append({
            'path': archive_path,
            'manifest': manifest_data
        })

        self.log_progress(f"✅ Added archive: {archive_path.name}")
        return manifest_data

    def load_js_data_file(self, file_path):
        """Load data from a JavaScript data file"""
        if not file_path.exists():
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'window\.YTD\.[^=]+=\s*(\[.*\]);?', content, re.DOTALL)
        if not match:
            return []

        try:
            data = json.loads(match.group(1))
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def merge_data_files(self):
        """Merge all data files from all archives"""
        self.log_progress("📁 Merging data files...")

        # Sort archives by generation date (oldest first) so newest data is processed last
        self.source_archives.sort(
            key=lambda x: x['manifest']['archiveInfo']['generationDate']
        )
        self.log_progress(f"   Processing archives from oldest to newest...")

        # Handle format compatibility - map old field names to new ones
        field_mappings = {
            'tweet': 'tweets',  # Old format used 'tweet', new uses 'tweets'
            'tweetHeader': 'tweetHeaders',
        }

        all_data_types = set()
        for archive in self.source_archives:
            for data_type in archive['manifest']['dataTypes'].keys():
                # Normalize field names
                normalized_type = field_mappings.get(data_type, data_type)
                all_data_types.add(normalized_type)

        for data_type in all_data_types:
            combined_data = []

            for archive in self.source_archives:
                # Check both the normalized name and any original names that map to it
                possible_names = [data_type]
                for old_name, new_name in field_mappings.items():
                    if new_name == data_type:
                        possible_names.append(old_name)

                for possible_name in possible_names:
                    data_type_info = archive['manifest']['dataTypes'].get(possible_name, {})
                    files = data_type_info.get('files', [])

                    for file_info in files:
                        file_path = archive['path'] / file_info['fileName']
                        data = self.load_js_data_file(file_path)
                        combined_data.extend(data)

            if combined_data:
                self.merged_data[data_type] = combined_data
                self.log_progress(f"   {data_type}: {len(combined_data)} items")

    def deduplicate_data(self):
        """Remove duplicate entries"""
        self.log_progress("🔄 Removing duplicates...")

        dedup_strategies = {
            'tweets': lambda x: x.get('tweet', {}).get('id_str'),  # Updated to handle normalized field name
            'like': lambda x: x.get('like', {}).get('tweetId'),
            'follower': lambda x: x.get('follower', {}).get('accountId'),
            'following': lambda x: x.get('following', {}).get('accountId'),
            'directMessages': lambda x: x.get('dmConversation', {}).get('conversationId'),
            'directMessagesGroup': lambda x: x.get('dmConversation', {}).get('conversationId'),
        }

        for data_type, data_list in self.merged_data.items():
            if data_type not in dedup_strategies:
                continue

            original_count = len(data_list)
            key_func = dedup_strategies[data_type]

            seen_keys = set()
            deduplicated = []

            for item in data_list:
                key = key_func(item)
                if key and key not in seen_keys:
                    seen_keys.add(key)
                    deduplicated.append(item)
                elif not key:
                    deduplicated.append(item)

            if original_count != len(deduplicated):
                removed = original_count - len(deduplicated)
                self.log_progress(f"   {data_type}: removed {removed} duplicates")
                self.merged_data[data_type] = deduplicated

        # Special handling for singleton data types - keep only the latest entry
        singleton_types = ['profile', 'account', 'ageinfo', 'accountTimezone', 'accountCreationIp']
        for data_type in singleton_types:
            if data_type in self.merged_data and len(self.merged_data[data_type]) > 1:
                original_count = len(self.merged_data[data_type])
                # Keep only the last entry (from the newest archive)
                self.merged_data[data_type] = [self.merged_data[data_type][-1]]
                self.log_progress(f"   {data_type}: kept latest entry (removed {original_count - 1} older entries)")

    def copy_media_files(self):
        """Copy media files with deduplication"""
        self.log_progress("📷 Copying media files...")

        # Handle format compatibility - normalize media directory names too
        media_dir_mappings = {
            'data/tweet_media': 'data/tweets_media',  # Old format → new format
            'data/direct_messages_media': 'data/direct_messages_media',  # Keep as is
            'data/profile_media': 'data/profile_media',  # Keep as is
        }

        copied_count = 0
        skipped_count = 0
        file_hashes = {}

        for archive in self.source_archives:
            for data_type, type_info in archive['manifest']['dataTypes'].items():
                media_dir = type_info.get('mediaDirectory')
                if not media_dir:
                    continue

                source_media_path = archive['path'] / media_dir
                if not source_media_path.exists():
                    continue

                # Normalize the media directory name
                normalized_media_dir = media_dir_mappings.get(media_dir, media_dir)
                target_media_path = self.output_path / normalized_media_dir
                target_media_path.mkdir(parents=True, exist_ok=True)

                self.log_progress(f"   Copying from {media_dir} → {normalized_media_dir}")

                for file_path in source_media_path.rglob('*'):
                    if not file_path.is_file():
                        continue

                    # Simple deduplication by file size and name
                    file_key = f"{file_path.name}_{file_path.stat().st_size}"
                    target_file = target_media_path / file_path.name

                    if file_key in file_hashes:
                        skipped_count += 1
                        continue

                    # Handle filename conflicts
                    counter = 1
                    original_target = target_file
                    while target_file.exists():
                        stem = original_target.stem
                        suffix = original_target.suffix
                        target_file = target_media_path / f"{stem}_{counter}{suffix}"
                        counter += 1

                    shutil.copy2(file_path, target_file)
                    file_hashes[file_key] = str(target_file)
                    copied_count += 1

        self.log_progress(f"   Copied {copied_count} files, skipped {skipped_count} duplicates")

    def write_merged_files(self):
        """Write merged data and manifest"""
        self.log_progress("💾 Writing merged files...")

        data_dir = self.output_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Write data files
        for data_type, data_list in self.merged_data.items():
            filename = data_type.replace('_', '-') + '.js'

            filename_mappings = {
                'directMessages': 'direct-messages.js',
                'directMessagesGroup': 'direct-messages-group.js',
                'emailAddressChange': 'email-address-change.js',
                'screenNameChange': 'screen-name-change.js',
            }

            if data_type in filename_mappings:
                filename = filename_mappings[data_type]

            file_path = data_dir / filename
            global_name = f"YTD.{data_type.replace('-', '_')}.part0"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"window.{global_name} = ")
                json.dump(data_list, f, ensure_ascii=False, separators=(',', ':'))
                f.write(';')

        # Generate manifest
        self.log_progress("📋 Generating manifest...")
        latest_archive = max(self.source_archives,
                             key=lambda x: x['manifest']['archiveInfo']['generationDate'])

        user_info = latest_archive['manifest']['userInfo']
        total_size = sum(f.stat().st_size for f in self.output_path.rglob('*') if f.is_file())

        # Build data types - ensure tweets entry exists
        data_types = {}
        for data_type, data_list in self.merged_data.items():
            filename = data_type.replace('_', '-') + '.js'

            filename_mappings = {
                'directMessages': 'direct-messages.js',
                'directMessagesGroup': 'direct-messages-group.js',
                'emailAddressChange': 'email-address-change.js',
                'screenNameChange': 'screen-name-change.js',
                'deletedTweets': 'deleted-tweets.js',
                'tweetHeaders': 'tweet-headers.js',
            }

            if data_type in filename_mappings:
                filename = filename_mappings[data_type]

            global_name = f"YTD.{data_type.replace('-', '_')}.part0"

            data_types[data_type] = {
                "files": [{
                    "fileName": f"data/{filename}",
                    "globalName": global_name,
                    "count": str(len(data_list))
                }]
            }

            # Add media directory if it exists
            if data_type == 'tweets' and (self.output_path / 'data/tweets_media').exists():
                data_types[data_type]["mediaDirectory"] = "data/tweets_media"
                self.log_progress(f"   ✅ Added tweets media directory")

            # Add media directory for profile if it exists
            if data_type == 'profile' and (self.output_path / 'data/profile_media').exists():
                data_types[data_type]["mediaDirectory"] = "data/profile_media"
                self.log_progress(f"   ✅ Added profile media directory")

        # Add tweetsMedia entry
        if (self.output_path / 'data/tweets_media').exists():
            data_types['tweetsMedia'] = {"mediaDirectory": "data/tweets_media"}
            self.log_progress(f"   ✅ Added tweetsMedia entry")

        # Add profileMedia entry
        if (self.output_path / 'data/profile_media').exists():
            data_types['profileMedia'] = {"mediaDirectory": "data/profile_media"}
            self.log_progress(f"   ✅ Added profileMedia entry")

        manifest = {
            "userInfo": user_info,
            "archiveInfo": {
                "sizeBytes": str(total_size),
                "generationDate": datetime.now().isoformat() + "Z",
                "isPartialArchive": False,
                "maxPartSizeBytes": "53687091200"
            },
            "readmeInfo": {
                "fileName": "data/README.txt",
                "directory": "data/",
                "name": "README.txt"
            },
            "dataTypes": data_types
        }

        manifest_path = self.output_path / "data" / "manifest.js"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write("window.__THAR_CONFIG = ")
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write(";")

    def copy_viewer_files(self):
        """Copy viewer files from source archive"""
        self.log_progress("🔧 Copying viewer files...")

        source_archive = None
        for archive in self.source_archives:
            if (archive['path'] / "Your archive.html").exists():
                source_archive = archive['path']
                break

        if not source_archive:
            self.log_progress("   Warning: No viewer files found")
            return

        viewer_files = ["Your archive.html", "assets"]

        for item in viewer_files:
            source_item = source_archive / item
            target_item = self.output_path / item

            if source_item.exists():
                if source_item.is_dir():
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_item, target_item)

    def merge_archives(self):
        """Main merge process"""
        self.log_progress(f"🚀 Starting merge of {len(self.source_archives)} archives...")

        self.output_path.mkdir(parents=True, exist_ok=True)

        self.merge_data_files()
        self.deduplicate_data()
        self.copy_media_files()
        self.write_merged_files()
        self.copy_viewer_files()

        self.log_progress("✅ Merge complete!")
        self.log_progress(f"📁 Output saved to: {self.output_path}")
