import time
import os
import sys
import psutil
import numpy as np
import csv
from collections import deque
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sklearn.ensemble import IsolationForest
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align

# Import the math function you built in Step 1
from edr_sensor import calculate_shannon_entropy

# --- UI STATE SHARED ACROSS THREADS ---
ui_state = {
    "events": deque(maxlen=15),
    "alert": "Waiting for filesystem activity...",
    "ai_status": "Initializing..."
}

def generate_dashboard():
    """Generates the Rich UI layout dynamically."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=5)
    )
    
    # Header
    layout["header"].update(Panel(Align.center(f"[bold cyan]SPECTER PURPLE TEAM - EDR AI DASHBOARD[/bold cyan] | [green]{ui_state['ai_status']}[/]")))

    # Main Table
    table = Table(expand=True, border_style="cyan")
    table.add_column("Time", style="dim", width=12)
    table.add_column("Target File", style="bold white")
    table.add_column("I/O Speed (5s)", justify="right", style="magenta", width=15)
    table.add_column("Entropy (0-8)", justify="right", style="green", width=15)
    table.add_column("AI Classification", justify="center", width=25)

    for event in list(ui_state["events"]):
        # Color code based on AI classification
        if "THREAT" in event['status']:
            status_colored = f"[bold red blink]{event['status']}[/]"
            file_colored = f"[red]{event['file']}[/]"
        else:
            status_colored = f"[bold green]{event['status']}[/]"
            file_colored = event['file']
            
        table.add_row(event['time'], file_colored, str(event['speed']), f"{event['entropy']:.4f}", status_colored)

    layout["main"].update(Panel(table, title="[yellow]Live File System Activity[/yellow]", border_style="blue"))
    
    # Footer Alert Box
    alert_text = ui_state["alert"]
    if "[!!!]" in alert_text:
        footer_panel = Panel(Align.center(f"[bold red blink]{alert_text}[/]"), title="[bold red]SYSTEM CRITICAL[/]", border_style="red")
    else:
        footer_panel = Panel(Align.center(f"[bold green]{alert_text}[/]"), title="System Status", border_style="green")
        
    layout["footer"].update(footer_panel)
    return layout

class EDRMonitor(FileSystemEventHandler):
    def __init__(self):
        # We use a deque (double-ended queue) to track modification timestamps
        self.recent_modifications = deque(maxlen=100)
        
        ui_state["ai_status"] = "Training Isolation Forest AI..."
        self.ai_model = IsolationForest(contamination=0.05, random_state=42)
        
        # Baseline Data: [I/O Speed, Entropy]
        # This tells the AI what "normal" user activity looks like
        baseline_normal_activity = np.array([
            [1, 3.2], [1, 4.1], [2, 3.8], [1, 4.5], [2, 4.2], [1, 2.5], [3, 4.0], [1, 0.0]
        ])
        self.ai_model.fit(baseline_normal_activity)
        ui_state["ai_status"] = "AI Model Active & Hunting"
        ui_state["alert"] = "EDR Online. Monitoring Sandbox..."

    def on_modified(self, event):
        """This triggers every time a file in the sandbox changes."""
        if event.is_directory:
            return

        file_path = event.src_path

        # FIX: Check if file still exists. 
        # If the ransomware deleted it before the EDR could scan it, skip it.
        if not os.path.exists(file_path):
            return

        current_time = time.time()
        
        # Log the time of this modification
        self.recent_modifications.append(current_time)

        # Calculate I/O Speed: How many files modified in the last 5 seconds?
        while self.recent_modifications and current_time - self.recent_modifications[0] > 5:
            self.recent_modifications.popleft()
        
        io_speed = len(self.recent_modifications)

        # Small delay to ensure the OS has finished writing the file before we read it
        time.sleep(0.05) 
        
        # Calculate Entropy
        entropy = calculate_shannon_entropy(file_path)

        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # --- THE AI DECISION ENGINE ---
        # Feed the real-time metrics to the Machine Learning model
        current_behavior = np.array([[io_speed, entropy]])
        prediction = self.ai_model.predict(current_behavior)

        # -1 means Anomaly (Attack), 1 means Inlier (Normal)
        if prediction[0] == -1:
            status = "THREAT DETECTED"
            ui_state["alert"] = f"[!!!] AI TRIGGERED: Cryptographic anomaly caught on {filename}!"
            self.kill_ransomware()
        else:
            status = "NORMAL ACTIVITY"

        # Add to UI events queue
        ui_state["events"].append({
            "time": timestamp,
            "file": filename,
            "speed": io_speed,
            "entropy": entropy,
            "status": status
        })

        # --- DATA LOGGING FOR ACADEMIC PLOTTING ---
        # Secretly write every event to a CSV file for the graphs
        try:
            with open("edr_telemetry.csv", mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, filename, io_speed, f"{entropy:.4f}", prediction[0]])
        except Exception:
            pass # Fail silently if the file is locked

    def kill_ransomware(self):
        """Hunts down the python process running the encryption engine."""
        ui_state["ai_status"] = "ENGAGING THREAT..."
        current_pid = os.getpid()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Don't kill the EDR itself
                if proc.info['pid'] == current_pid:
                    continue
                
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'python' in proc.info['name'].lower():
                    cmd_str = ' '.join(cmdline).lower()
                    # Look for your specific red team script running in the background
                    if 'engine' in cmd_str or 'encrypt' in cmd_str or 'simulator' in cmd_str:
                        ui_state["alert"] = f"[!!!] NEUTRALIZED THREAT -> PID: {proc.info['pid']} ({cmd_str})"
                        proc.terminate()
                        ui_state["ai_status"] = "THREAT TERMINATED. SANDBOX SECURED."
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

def start_edr(target_directory):
    # Initialize the Telemetry Log with headers
    with open("edr_telemetry.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Filename", "IO_Speed", "Entropy", "AI_Prediction"])

    event_handler = EDRMonitor()
    observer = Observer()
    observer.schedule(event_handler, target_directory, recursive=True)
    observer.start()
    
    try:
        # Use Rich Live Display instead of a basic sleep loop
        with Live(get_renderable=generate_dashboard, refresh_per_second=10, screen=True):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] EDR Shutting down.")
    
    observer.join()

if __name__ == "__main__":
    # Point this to your sandbox directory. 
    # Adjust the path if your Target_Sandbox is located somewhere else!
    sandbox_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Target_Sandbox'))
    
    if not os.path.exists(sandbox_path):
        print(f"[!] Error: Cannot find sandbox at {sandbox_path}")
        sys.exit(1)
        
    start_edr(sandbox_path)
