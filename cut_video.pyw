import os
import sys
import threading
import subprocess
from datetime import timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from ttkthemes import ThemedTk

def create_video_cutter_gui(default_file=None):
    # Main window
    root = ThemedTk(theme="arc")
    root.title(f"Video Cutter - {sys.executable}")
    # root.geometry("600x600")

    # Variables
    video_path = tk.StringVar()
    output_filename_var = tk.StringVar()
    start_time_var = tk.StringVar(value="00:00:00")
    end_time_var = tk.StringVar()
    cut_duration_var = tk.StringVar(value="00:00:00")
    video_duration = tk.DoubleVar(value=0.0)
    updating = False  # Flag to prevent recursive updates

    # Function definitions
    def select_video_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4;*.avi"), ("All Files", "*.*")]
        )
        if file_path:
            video_path.set(file_path)
            load_video_info(file_path)

    def load_video_info(path):
        try:
            # Get video duration using ffprobe
            command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path,
            ]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            duration = float(result.stdout.strip())
            video_duration.set(duration)

            # Update sliders and entries
            start_scale.config(to=duration)
            end_scale.config(to=duration)
            end_time_var.set(format_time(duration))
            end_scale.set(duration)

            # Update duration
            start_seconds = parse_time(start_time_var.get())
            if start_seconds is None:
                start_seconds = 0
                start_time_var.set(format_time(0))
            duration_seconds = duration - start_seconds
            cut_duration_var.set(format_time(duration_seconds))

            # Set default output file name
            base_name, ext = os.path.splitext(os.path.basename(path))
            default_output_name = f"{base_name} (cutted){ext}"
            output_filename_var.set(default_output_name)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load video info: {e}")

    def format_time(seconds):
        total_seconds = int(seconds)
        hrs = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hrs:02}:{mins:02}:{secs:02}"

    def parse_time(time_str):
        # Supports formats like 'HH:MM:SS', 'MM:SS', or seconds as float/int
        try:
            parts = list(map(float, time_str.strip().split(":")))
            if len(parts) == 3:
                hrs, mins, secs = parts
            elif len(parts) == 2:
                hrs = 0
                mins, secs = parts
            elif len(parts) == 1:
                hrs = 0
                mins = 0
                secs = parts[0]
            else:
                return None
            seconds = hrs * 3600 + mins * 60 + secs
            return seconds
        except ValueError:
            return None

    def validate_start_time_input():
        nonlocal updating
        if updating:
            return
        updating = True
        try:
            end_time_str = end_time_var.get()
            end_seconds = parse_time(end_time_str)
            duration = video_duration.get()
            if end_seconds is None or not (0 <= end_seconds <= duration):
                messagebox.showwarning("Invalid Input", f"Please enter a valid end time between 00:00:00 and {format_time(duration)}")
            else:
                end_scale.set(end_seconds)
                # Adjust start time if end time is before start time
                start_seconds = parse_time(start_time_var.get())
                if end_seconds < start_seconds:
                    start_seconds = end_seconds
                    start_time_var.set(format_time(start_seconds))
                    start_scale.set(start_seconds)
                # Update duration
                duration_seconds = end_seconds - start_seconds
                cut_duration_var.set(format_time(duration_seconds))
        finally:
            updating = False

    def validate_end_time_input():
        nonlocal updating
        if updating:
            return
        updating = True
        try:
            end_time_str = end_time_var.get()
            end_seconds = parse_time(end_time_str)
            duration = video_duration.get()
            if end_seconds is None or not (0 <= end_seconds <= duration):
                messagebox.showwarning("Invalid Input", f"Please enter a valid end time between 00:00:00 and {format_time(duration)}")
            else:
                end_scale.set(end_seconds)
                # Update duration based on start time
                start_seconds = parse_time(start_time_var.get())
                if start_seconds is not None:
                    duration_seconds = end_seconds - start_seconds
                    if duration_seconds < 0:
                        duration_seconds = 0
                        messagebox.showwarning("Invalid Duration", "End time must be after start time.")
                    cut_duration_var.set(format_time(duration_seconds))
        finally:
            updating = False

    def validate_duration_input():
        nonlocal updating
        if updating:
            return
        updating = True
        try:
            duration_str = cut_duration_var.get()
            duration_seconds = parse_time(duration_str)
            total_duration = video_duration.get()
            if duration_seconds is None or duration_seconds < 0:
                messagebox.showwarning("Invalid Input", "Please enter a valid duration.")
            else:
                start_seconds = parse_time(start_time_var.get())
                if start_seconds is not None:
                    end_seconds = start_seconds + duration_seconds
                    if end_seconds > total_duration:
                        end_seconds = total_duration
                        duration_seconds = total_duration - start_seconds
                        cut_duration_var.set(format_time(duration_seconds))
                    elif end_seconds < start_seconds:
                        # Adjust start time if end time is before start time
                        start_seconds = end_seconds
                        start_time_var.set(format_time(start_seconds))
                        start_scale.set(start_seconds)
                        duration_seconds = end_seconds - start_seconds
                        cut_duration_var.set(format_time(duration_seconds))
                    end_time_var.set(format_time(end_seconds))
                    end_scale.set(end_seconds)
        finally:
            updating = False

    def update_entry_from_scale(var, scale):
        nonlocal updating
        if updating:
            return
        updating = True
        try:
            seconds = scale.get()
            var.set(format_time(seconds))
            if var == start_time_var:
                # Update duration and end time based on new start time
                end_seconds = parse_time(end_time_var.get())
                if seconds > end_seconds:
                    end_seconds = seconds
                    end_time_var.set(format_time(end_seconds))
                    end_scale.set(end_seconds)
                duration_seconds = end_seconds - seconds
                cut_duration_var.set(format_time(duration_seconds))
            elif var == end_time_var:
                # Adjust start time if end time is before start time
                start_seconds = parse_time(start_time_var.get())
                if seconds < start_seconds:
                    start_seconds = seconds
                    start_time_var.set(format_time(start_seconds))
                    start_scale.set(start_seconds)
                duration_seconds = seconds - start_seconds
                cut_duration_var.set(format_time(duration_seconds))
        finally:
            updating = False

    def start_cutting():
        input_path = video_path.get()
        output_dir = os.path.dirname(input_path)
        
        start_time_str = start_time_var.get()
        end_time_str = end_time_var.get()

        start_seconds = parse_time(start_time_str)
        end_seconds = parse_time(end_time_str)
        duration = video_duration.get()

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid video file.")
            return

        if start_seconds is None or end_seconds is None:
            messagebox.showerror("Error", "Please enter valid start and end times.")
            return

        if not (0 <= start_seconds < end_seconds <= duration):
            messagebox.showerror("Error", "Start time must be less than end time and within video duration.")
            return

        output_filename = output_filename_var.get()
        output_path = os.path.join(output_dir, output_filename)

        # Build ffmpeg command
        command = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ss", str(start_seconds),
            "-to", str(end_seconds),
            "-c", "copy",
            output_path,
        ]

        # Start ffmpeg in a separate thread
        threading.Thread(target=run_ffmpeg, args=(command, output_path)).start()

    def run_ffmpeg(command, output_path):
        log_callback("Starting ffmpeg process...")
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )

            for line in process.stdout:
                log_callback(line.strip())

            process.wait()
            if process.returncode == 0:
                log_callback(f"Video saved to: {output_path}")
                messagebox.showinfo("Success", "Video cutting completed successfully.")
            else:
                log_callback("ffmpeg encountered an error.")
                messagebox.showerror("Error", "ffmpeg encountered an error. Check logs for details.")
        except Exception as e:
            log_callback(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def log_callback(message):
        log_output.insert(tk.END, message + "\n")
        log_output.yview(tk.END)

    # GUI components

    # Video selection
    ttk.Label(root, text="Video File:").pack(anchor="w", padx=10, pady=5)
    video_frame = ttk.Frame(root)
    video_frame.pack(fill="x", padx=10)
    video_entry = ttk.Entry(video_frame, textvariable=video_path, width=50)
    video_entry.pack(side="left", fill="x", expand=True)
    select_button = ttk.Button(video_frame, text="Select Video", command=select_video_file)
    select_button.pack(side="left", padx=5)

    # Start time
    ttk.Label(root, text="Start Time (HH:MM:SS):").pack(anchor="w", padx=10, pady=5)
    start_time_entry = ttk.Entry(root, textvariable=start_time_var)
    start_time_entry.pack(fill="x", padx=10)
    start_time_entry.bind("<FocusOut>", lambda e: validate_start_time_input())

    # Start time scale
    start_scale = ttk.Scale(root, from_=0, to=video_duration.get(), orient="horizontal")
    start_scale.pack(fill="x", padx=10, pady=5)
    start_scale.bind("<B1-Motion>", lambda e: update_entry_from_scale(start_time_var, start_scale))
    start_scale.bind("<ButtonRelease-1>", lambda e: update_entry_from_scale(start_time_var, start_scale))

    # Duration
    ttk.Label(root, text="Duration (HH:MM:SS):").pack(anchor="w", padx=10, pady=5)
    duration_entry = ttk.Entry(root, textvariable=cut_duration_var)
    duration_entry.pack(fill="x", padx=10)
    duration_entry.bind("<FocusOut>", lambda e: validate_duration_input())

    # End time
    ttk.Label(root, text="End Time (HH:MM:SS):").pack(anchor="w", padx=10, pady=5)
    end_time_entry = ttk.Entry(root, textvariable=end_time_var)
    end_time_entry.pack(fill="x", padx=10)
    end_time_entry.bind("<FocusOut>", lambda e: validate_end_time_input())

    # End time scale
    end_scale = ttk.Scale(root, from_=0, to=video_duration.get(), orient="horizontal")
    end_scale.pack(fill="x", padx=10, pady=5)
    end_scale.bind("<B1-Motion>", lambda e: update_entry_from_scale(end_time_var, end_scale))
    end_scale.bind("<ButtonRelease-1>", lambda e: update_entry_from_scale(end_time_var, end_scale))

    # Output file name
    ttk.Label(root, text="Output File Name:").pack(anchor="w", padx=10, pady=5)
    output_name_entry = ttk.Entry(root, textvariable=output_filename_var)
    output_name_entry.pack(fill="x", padx=10)

    # Log output
    ttk.Label(root, text="Logs:").pack(anchor="w", padx=10, pady=5)
    log_output = scrolledtext.ScrolledText(root, height=10, width=70)
    log_output.pack(padx=10, pady=5)

    # Start button
    start_button = ttk.Button(root, text="Start Cutting", command=start_cutting)
    start_button.pack(pady=10)

    # If default_file is valid, set it
    if default_file and os.path.exists(default_file):
        video_path.set(default_file)
        load_video_info(default_file)

    root.mainloop()

if __name__ == "__main__":
    import sys
    default_file = sys.argv[1] if len(sys.argv) > 1 else None
    create_video_cutter_gui(default_file)
