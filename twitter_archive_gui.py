#!/usr/bin/env python3
"""
Twitter Archive Merger - GUI Version
A user-friendly interface for analyzing and merging Twitter archives.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib


class TwitterArchiveAnalyzer:
    """Embedded analyzer class for the GUI"""

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


class TwitterArchiveMerger:
    """Embedded merger class for the GUI"""

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

        # Add tweetsMedia entry
        if (self.output_path / 'data/tweets_media').exists():
            data_types['tweetsMedia'] = {"mediaDirectory": "data/tweets_media"}
            self.log_progress(f"   ✅ Added tweetsMedia entry")

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


class TwitterArchiveGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Archive Merger")
        self.root.geometry("800x600")

        self.archives = []
        self.setup_ui()

    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Twitter Archive Merger",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Archives section
        archives_frame = ttk.LabelFrame(main_frame, text="Select Twitter Archives", padding="10")
        archives_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(archives_frame, text="Add Archive Folder",
                   command=self.add_archive).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(archives_frame, text="Remove Selected",
                   command=self.remove_archive).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(archives_frame, text="Clear All",
                   command=self.clear_archives).grid(row=0, column=2)

        # Archives listbox
        self.archives_listbox = tk.Listbox(archives_frame, height=6)
        self.archives_listbox.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E),
                                   pady=(10, 0))

        scrollbar = ttk.Scrollbar(archives_frame, orient="vertical",
                                  command=self.archives_listbox.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S), pady=(10, 0))
        self.archives_listbox.configure(yscrollcommand=scrollbar.set)

        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky=tk.W)

        self.output_var = tk.StringVar(value="./merged_archive")
        ttk.Entry(output_frame, textvariable=self.output_var, width=50).grid(row=1, column=0,
                                                                             sticky=(tk.W, tk.E),
                                                                             padx=(0, 10))

        ttk.Button(output_frame, text="Browse",
                   command=self.browse_output).grid(row=1, column=1)

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(button_frame, text="Analyze Archives",
                   command=self.analyze_archives).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(button_frame, text="Merge Archives",
                   command=self.merge_archives).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(button_frame, text="Open Output",
                   command=self.open_output).grid(row=0, column=2)

        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=15, width=70)
        self.progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        archives_frame.columnconfigure(2, weight=1)
        output_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)

    def log(self, message):
        """Add message to progress log"""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update()

    def add_archive(self):
        """Add an archive folder"""
        folder = filedialog.askdirectory(title="Select Twitter Archive Folder")
        if not folder:
            return

        try:
            # Validate it's a Twitter archive
            analyzer = TwitterArchiveAnalyzer(folder)
            info = analyzer.get_archive_info()

            archive_entry = {
                'path': folder,
                'info': info
            }

            self.archives.append(archive_entry)

            display_text = f"@{info['username']} - {info['generation_date'][:10]} - {folder}"
            self.archives_listbox.insert(tk.END, display_text)

            self.log(f"✅ Added: @{info['username']} ({Path(folder).name})")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid Twitter archive:\n{str(e)}")

    def remove_archive(self):
        """Remove selected archive"""
        selection = self.archives_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        removed = self.archives.pop(index)
        self.archives_listbox.delete(index)

        self.log(f"❌ Removed: {Path(removed['path']).name}")

    def clear_archives(self):
        """Clear all archives"""
        self.archives.clear()
        self.archives_listbox.delete(0, tk.END)
        self.log("🗑️ Cleared all archives")

    def browse_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)

    def analyze_archives(self):
        """Analyze selected archives"""
        if not self.archives:
            messagebox.showwarning("Warning", "Please add some archives first!")
            return

        self.log("🔍 ANALYZING ARCHIVES")
        self.log("=" * 50)

        for i, archive in enumerate(self.archives, 1):
            try:
                analyzer = TwitterArchiveAnalyzer(archive['path'])
                info = analyzer.get_archive_info()
                data_analysis = analyzer.analyze_data_types()

                self.log(f"\n{i}. @{info['username']} ({info['display_name']})")
                self.log(f"   📅 Generated: {info['generation_date'][:10]}")
                self.log(f"   💾 Size: {info['size_bytes'] / 1024 / 1024:.1f} MB")

                # Show top data types
                sorted_data = sorted(data_analysis.items(),
                                     key=lambda x: x[1]['total_count'],
                                     reverse=True)[:5]

                for data_type, data in sorted_data:
                    media_info = " 📷" if data['has_media'] else ""
                    self.log(f"   📊 {data_type}: {data['total_count']:,}{media_info}")

            except Exception as e:
                self.log(f"❌ Error analyzing {archive['path']}: {e}")

    def merge_archives(self):
        """Merge archives in background thread"""
        if len(self.archives) < 2:
            messagebox.showwarning("Warning", "Please add at least 2 archives to merge!")
            return

        output_path = self.output_var.get()
        if not output_path:
            messagebox.showwarning("Warning", "Please specify an output folder!")
            return

        # Run merge in background thread
        def run_merge():
            try:
                merger = TwitterArchiveMerger(output_path, self.log)

                for archive in self.archives:
                    merger.add_archive(archive['path'])

                merger.merge_archives()

                # Show success message in main thread
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Merge completed!\n\nOpen '{output_path}/Your archive.html' to view your combined archive."
                ))

            except Exception as e:
                error_msg = f"Merge failed: {str(e)}"
                self.log(f"❌ {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

        self.log("🚀 STARTING MERGE")
        self.log("=" * 50)

        thread = threading.Thread(target=run_merge)
        thread.daemon = True
        thread.start()

    def open_output(self):
        """Open output folder"""
        output_path = Path(self.output_var.get())
        if output_path.exists():
            os.startfile(output_path)  # Windows
        else:
            messagebox.showwarning("Warning", "Output folder doesn't exist yet!")


def main():
    root = tk.Tk()
    app = TwitterArchiveGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()