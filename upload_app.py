"""
TactivAI Knowledge Base Upload Tool
====================================
Desktop app for uploading markdown KB articles to Supabase with OpenAI embeddings.

Run:  python upload_app.py

Requirements:
    pip install openai httpx

Version: 1.0.0
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import httpx
from openai import OpenAI

VERSION = "1.0.0"


class UploadApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"TactivAI KB Upload Tool v{VERSION}")
        self.root.geometry("700x680")
        self.root.resizable(False, False)

        # Set icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        # Default values
        self.default_dir = os.path.expanduser("~")

        self.build_ui()

    def build_ui(self):
        # Main container with padding
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        # Title
        title = ttk.Label(main, text="TactivAI KB Upload Tool", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w")
        subtitle = ttk.Label(main, text="Upload markdown articles to Supabase with vector embeddings", font=("Segoe UI", 9))
        subtitle.pack(anchor="w", pady=(0, 15))

        # --- Folder Selection ---
        folder_frame = ttk.LabelFrame(main, text="Folder", padding=10)
        folder_frame.pack(fill="x", pady=(0, 10))

        folder_row = ttk.Frame(folder_frame)
        folder_row.pack(fill="x")

        self.folder_var = tk.StringVar(value=self.default_dir)
        folder_entry = ttk.Entry(folder_row, textvariable=self.folder_var, width=60)
        folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_btn = ttk.Button(folder_row, text="Browse...", command=self.browse_folder)
        browse_btn.pack(side="right")

        self.file_count_label = ttk.Label(folder_frame, text="", font=("Segoe UI", 9))
        self.file_count_label.pack(anchor="w", pady=(5, 0))

        # --- Credentials ---
        cred_frame = ttk.LabelFrame(main, text="Credentials", padding=10)
        cred_frame.pack(fill="x", pady=(0, 10))

        # OpenAI Key
        ttk.Label(cred_frame, text="OpenAI API Key:").grid(row=0, column=0, sticky="w", pady=3)
        self.openai_key_var = tk.StringVar()
        openai_entry = ttk.Entry(cred_frame, textvariable=self.openai_key_var, show="*", width=55)
        openai_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=3)

        # Supabase URL
        ttk.Label(cred_frame, text="Supabase URL:").grid(row=1, column=0, sticky="w", pady=3)
        self.supabase_url_var = tk.StringVar()
        url_entry = ttk.Entry(cred_frame, textvariable=self.supabase_url_var, width=55)
        url_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=3)
        url_entry.insert(0, "https://your-project.supabase.co")

        # Supabase Key
        ttk.Label(cred_frame, text="Supabase Key:").grid(row=2, column=0, sticky="w", pady=3)
        self.supabase_key_var = tk.StringVar()
        supa_entry = ttk.Entry(cred_frame, textvariable=self.supabase_key_var, show="*", width=55)
        supa_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=3)

        # Category
        ttk.Label(cred_frame, text="Category tag:").grid(row=3, column=0, sticky="w", pady=3)
        self.category_var = tk.StringVar(value="demo-articles")
        cat_entry = ttk.Entry(cred_frame, textvariable=self.category_var, width=55)
        cat_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=3)

        cred_frame.columnconfigure(1, weight=1)

        # Update file count on folder change (after category_var exists)
        self.folder_var.trace_add("write", lambda *_: self.update_file_count())
        self.update_file_count()

        # --- Progress ---
        progress_frame = ttk.LabelFrame(main, text="Progress", padding=10)
        progress_frame.pack(fill="x", pady=(0, 10))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 5))

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=("Segoe UI", 9))
        self.status_label.pack(anchor="w")

        # --- Log ---
        log_frame = ttk.LabelFrame(main, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.log_text = tk.Text(log_frame, height=8, font=("Consolas", 9), state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Buttons ---
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x")

        self.upload_btn = ttk.Button(btn_frame, text="Upload", command=self.start_upload)
        self.upload_btn.pack(side="right", padx=(5, 0))

        self.validate_btn = ttk.Button(btn_frame, text="Validate Connections", command=self.start_validate)
        self.validate_btn.pack(side="right")

        clear_btn = ttk.Button(btn_frame, text="Clear Log", command=self.clear_log)
        clear_btn.pack(side="left")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def update_file_count(self):
        folder = self.folder_var.get()
        if os.path.isdir(folder):
            count = len([f for f in os.listdir(folder) if f.endswith(".md")])
            self.file_count_label.config(text=f"Found {count} markdown files")
            self.category_var.set(os.path.basename(folder))
        else:
            self.file_count_label.config(text="Folder not found")

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Ready")

    def set_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        self.upload_btn.config(state=state)
        self.validate_btn.config(state=state)

    def check_inputs(self):
        if not os.path.isdir(self.folder_var.get()):
            messagebox.showerror("Error", "Please select a valid folder.")
            return False
        if not self.openai_key_var.get().strip():
            messagebox.showerror("Error", "Please enter your OpenAI API Key.")
            return False
        if not self.supabase_url_var.get().strip():
            messagebox.showerror("Error", "Please enter your Supabase URL.")
            return False
        if not self.supabase_key_var.get().strip():
            messagebox.showerror("Error", "Please enter your Supabase Service Role Key.")
            return False
        return True

    def validate_openai(self):
        try:
            client = OpenAI(api_key=self.openai_key_var.get().strip())
            client.embeddings.create(model="text-embedding-3-small", input="test")
            return True, client
        except Exception as e:
            return False, str(e)

    def validate_supabase(self):
        try:
            url = self.supabase_url_var.get().strip()
            if "your-project" in url or not url.startswith("https://"):
                return False, "Please enter your actual Supabase URL"
            headers = {
                "apikey": self.supabase_key_var.get().strip(),
                "Authorization": f"Bearer {self.supabase_key_var.get().strip()}"
            }
            response = httpx.get(
                f"{url}/rest/v1/documents?select=id&limit=1",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401:
                return False, "Invalid API key"
            elif response.status_code == 404:
                return False, "Table 'documents' not found - check your Supabase setup"
            else:
                return False, f"HTTP {response.status_code}"
        except httpx.ConnectError:
            return False, "Could not connect - check URL"
        except httpx.TimeoutException:
            return False, "Connection timed out"
        except Exception as e:
            return False, str(e)

    def get_existing_files(self):
        try:
            headers = {
                "apikey": self.supabase_key_var.get().strip(),
                "Authorization": f"Bearer {self.supabase_key_var.get().strip()}",
                "Content-Type": "application/json"
            }
            response = httpx.get(
                f"{self.supabase_url_var.get().strip()}/rest/v1/documents?select=metadata",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                results = response.json()
                return {r["metadata"].get("filename", "") for r in results if r.get("metadata")}
        except Exception:
            pass
        return set()

    def start_validate(self):
        if not self.check_inputs():
            return
        self.set_buttons(False)
        threading.Thread(target=self.run_validate, daemon=True).start()

    def run_validate(self):
        self.log("Validating OpenAI...")
        self.status_var.set("Validating OpenAI...")
        ok, result = self.validate_openai()
        if ok:
            self.log("  OpenAI: OK")
        else:
            self.log(f"  OpenAI: FAILED - {result}")
            self.status_var.set("Validation failed")
            self.set_buttons(True)
            return

        self.log("Validating Supabase...")
        self.status_var.set("Validating Supabase...")
        ok, err = self.validate_supabase()
        if ok:
            self.log("  Supabase: OK")
        else:
            self.log(f"  Supabase: FAILED - {err}")
            self.status_var.set("Validation failed")
            self.set_buttons(True)
            return

        self.log("All connections valid!")
        self.status_var.set("Connections valid")
        self.set_buttons(True)

    def start_upload(self):
        if not self.check_inputs():
            return
        self.set_buttons(False)
        threading.Thread(target=self.run_upload, daemon=True).start()

    def run_upload(self):
        folder = self.folder_var.get()
        md_files = sorted([f for f in os.listdir(folder) if f.endswith(".md")])

        if not md_files:
            self.log("No .md files found.")
            self.status_var.set("No files to upload")
            self.set_buttons(True)
            return

        # Validate
        self.log("Validating connections...")
        self.status_var.set("Validating...")

        ok, result = self.validate_openai()
        if not ok:
            self.log(f"OpenAI validation failed: {result}")
            self.status_var.set("Validation failed")
            self.set_buttons(True)
            return
        openai_client = result
        self.log("  OpenAI: OK")

        ok, err = self.validate_supabase()
        if not ok:
            self.log(f"Supabase validation failed: {err}")
            self.status_var.set("Validation failed")
            self.set_buttons(True)
            return
        self.log("  Supabase: OK")

        # Check duplicates
        self.log("Checking for duplicates...")
        self.status_var.set("Checking duplicates...")
        existing = self.get_existing_files()
        new_files = [f for f in md_files if f not in existing]
        skipped = [f for f in md_files if f in existing]

        if skipped:
            self.log(f"  Skipping {len(skipped)} already uploaded")
        self.log(f"  {len(new_files)} new files to upload")

        if not new_files:
            self.log("\nAll files already uploaded!")
            self.status_var.set("Nothing to upload")
            self.progress_var.set(100)
            self.set_buttons(True)
            return

        # Upload
        self.log(f"\nUploading {len(new_files)} files...")
        category = self.category_var.get().strip()
        supabase_url = self.supabase_url_var.get().strip()
        supabase_key = self.supabase_key_var.get().strip()
        success = 0
        failed = 0

        for i, filename in enumerate(new_files):
            filepath = os.path.join(folder, filename)
            progress = ((i) / len(new_files)) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"Uploading {filename}...")

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                metadata = {"category": category, "filename": filename}

                response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=content
                )
                embedding = response.data[0].embedding

                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                }
                data = {
                    "content": content,
                    "metadata": metadata,
                    "embedding": embedding
                }
                resp = httpx.post(
                    f"{supabase_url}/rest/v1/documents",
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if resp.status_code == 201:
                    success += 1
                    self.log(f"  [{i+1}/{len(new_files)}] {filename} - OK")
                else:
                    failed += 1
                    self.log(f"  [{i+1}/{len(new_files)}] {filename} - FAILED ({resp.status_code})")

            except Exception as e:
                failed += 1
                self.log(f"  [{i+1}/{len(new_files)}] {filename} - ERROR: {e}")

        self.progress_var.set(100)

        # Summary
        self.log(f"\n=== Upload Complete ===")
        self.log(f"  Uploaded: {success}")
        self.log(f"  Failed:   {failed}")
        self.log(f"  Skipped:  {len(skipped)}")
        self.status_var.set(f"Done - {success} uploaded, {failed} failed, {len(skipped)} skipped")
        self.set_buttons(True)

        if failed == 0 and success > 0:
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Successfully uploaded {success} articles!"))


if __name__ == "__main__":
    root = tk.Tk()
    app = UploadApp(root)
    root.mainloop()
