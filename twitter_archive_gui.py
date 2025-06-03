#!/usr/bin/env python3
"""
Twitter Archive Merger - GUI Frontend
User interface for the Twitter Archive Merger tool.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path

# Import backend classes
from twitter_archive_merger import TwitterArchiveAnalyzer, TwitterArchiveMerger


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
                   command=self.open_output).grid(row=0, column=2, padx=(0, 10))

        ttk.Button(button_frame, text="Help",
                   command=self.show_help).grid(row=0, column=3)

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

    def show_help(self):
        """Show help popup window"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Twitter Archive Merger - Help")
        help_window.geometry("700x500")
        help_window.resizable(True, True)

        # Create main frame
        main_frame = ttk.Frame(help_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Add title
        title_label = ttk.Label(main_frame, text="Twitter Archive Merger - Help",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))

        # Create scrolled text widget for help content
        help_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=25)
        help_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Load help content from file
        try:
            help_file = Path(__file__).parent / "help_text.md"
            with open(help_file, 'r', encoding='utf-8') as f:
                content = f.read()
            help_text.insert(tk.END, content)
        except FileNotFoundError:
            help_text.insert(tk.END, "Help file not found. Please ensure 'help_text.md' is in the same directory as this program.")
        except Exception as e:
            help_text.insert(tk.END, f"Error loading help content: {str(e)}")

        # Make text read-only
        help_text.configure(state=tk.DISABLED)

        # Add close button
        close_button = ttk.Button(main_frame, text="Close", command=help_window.destroy)
        close_button.pack(pady=(5, 0))

        # Center the window
        help_window.transient(self.root)
        help_window.grab_set()

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

    def show_help(self):
        """Show help popup window"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Twitter Archive Merger - Help")
        help_window.geometry("700x500")
        help_window.resizable(True, True)

        # Create main frame
        main_frame = ttk.Frame(help_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Add title
        title_label = ttk.Label(main_frame, text="Twitter Archive Merger - Help",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))

        # Create scrolled text widget for help content
        help_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=25)
        help_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Load help content from file
        try:
            help_file = Path(__file__).parent / "help_text.md"
            with open(help_file, 'r', encoding='utf-8') as f:
                content = f.read()
            help_text.insert(tk.END, content)
        except FileNotFoundError:
            help_text.insert(tk.END, "Help file not found. Please ensure 'help_text.md' is in the same directory as this program.")
        except Exception as e:
            help_text.insert(tk.END, f"Error loading help content: {str(e)}")

        # Make text read-only
        help_text.configure(state=tk.DISABLED)

        # Add close button
        close_button = ttk.Button(main_frame, text="Close", command=help_window.destroy)
        close_button.pack(pady=(5, 0))

        # Center the window
        help_window.transient(self.root)
        help_window.grab_set()

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
