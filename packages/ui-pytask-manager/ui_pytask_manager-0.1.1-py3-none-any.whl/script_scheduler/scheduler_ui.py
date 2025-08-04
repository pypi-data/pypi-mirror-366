import json
import sqlite3
import subprocess
import tkinter as tk
import sv_ttk
from tkcalendar import Calendar
from tkinter import ttk, filedialog, messagebox
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import darkdetect


DB_NAME = "scheduler.db"

def init_db():
    """Initialize the SQLite database for job persistence"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create jobs table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  script_path TEXT NOT NULL,
                  trigger_type TEXT NOT NULL,
                  trigger_args TEXT NOT NULL,
                  status TEXT NOT NULL DEFAULT 'active')''')
    
    # Check if status column exists, if not add it
    c.execute("PRAGMA table_info(jobs)")
    columns = [column[1] for column in c.fetchall()]
    if 'status' not in columns:
        c.execute("ALTER TABLE jobs ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
    
    # Create job_logs table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS job_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  job_id INTEGER NOT NULL,
                  execution_time TEXT NOT NULL,
                  log_output TEXT NOT NULL,
                  FOREIGN KEY(job_id) REFERENCES jobs(id))''')
    
    conn.commit()
    conn.close()

def run_script(job_id, script_path):
    """Execute the Python script and capture logs"""
    try:
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO job_logs (job_id, execution_time, log_output) VALUES (?, ?, ?)",
            (job_id, timestamp, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        )
        conn.commit()
        conn.close()
    except Exception as e:
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO job_logs (job_id, execution_time, log_output) VALUES (?, ?, ?)",
            (job_id, timestamp, f"ERROR: {str(e)}")
        )
        conn.commit()
        conn.close()

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Script Scheduler")
        self.root.geometry("600x500")
        
        # Initialize database and scheduler
        init_db()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.load_jobs()
        
        # Create UI components
        self.create_widgets()
        self.populate_job_list()
    
    def create_widgets(self):
        # Script selection frame
        script_frame = ttk.LabelFrame(self.root, text="Script Configuration")
        script_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(script_frame, text="Script Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.script_path = tk.StringVar()
        ttk.Entry(script_frame, textvariable=self.script_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(script_frame, text="Browse", command=self.browse_script).grid(row=0, column=2, padx=5, pady=5)
        
        # Schedule configuration frame
        schedule_frame = ttk.LabelFrame(self.root, text="Schedule Configuration")
        schedule_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(schedule_frame, text="Schedule Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.schedule_type = tk.StringVar()
        schedule_combo = ttk.Combobox(schedule_frame, textvariable=self.schedule_type, 
                                     values=["Date", "Daily", "Weekly", "Interval"],
                                     state="readonly", width=15)
        schedule_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        schedule_combo.bind("<<ComboboxSelected>>", self.update_schedule_options)
        
        # Dynamic schedule options frame
        self.options_frame = ttk.LabelFrame(self.root, text="Schedule Options")
        self.options_frame.pack(fill="x", padx=10, pady=5)
        self.update_schedule_options(None)  # Initialize with default
        
        # Control buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add Job", command=self.add_job).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remove Job", command=self.remove_job).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Pause Job", command=self.pause_job).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Resume Job", command=self.resume_job).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Run Now", command=self.run_selected_job_now).pack(side="left", padx=5)
        
        # Job list frame
        list_frame = ttk.LabelFrame(self.root, text="Scheduled Jobs")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.job_list = tk.Listbox(list_frame, height=8)
        self.job_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.job_list.bind("<<ListboxSelect>>", self.on_job_select)

        # Log display frame
        log_frame = ttk.LabelFrame(self.root, text="Job Logs")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = tk.Text(log_frame, height=6, state="disabled")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_schedule_options(self, event):
        """Update the schedule options based on selected schedule type"""
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.options_frame)
        frame.pack(fill="x", padx=5, pady=5)
        
        schedule_type = self.schedule_type.get()
        
        if schedule_type == "Date":
            # Date selection
            ttk.Label(frame, text="Select Date:").grid(row=0, column=0, padx=5, pady=5, sticky="nw")
            self.calendar = Calendar(frame, selectmode='day', 
                                    year=datetime.now().year,
                                    month=datetime.now().month,
                                    day=datetime.now().day,
                                    date_pattern='y-mm-dd')
            self.calendar.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # Time selection
            ttk.Label(frame, text="Hour:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.hour_spin = ttk.Spinbox(frame, from_=0, to=23, width=4)
            self.hour_spin.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.hour_spin.set(datetime.now().hour)
            
            ttk.Label(frame, text="Minute:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
            self.minute_spin = ttk.Spinbox(frame, from_=0, to=59, width=4)
            self.minute_spin.grid(row=1, column=3, padx=5, pady=5, sticky="w")
            self.minute_spin.set(datetime.now().minute)
            
        elif schedule_type in ["Daily", "Weekly"]:
            # Time configuration
            ttk.Label(frame, text="Hour:").grid(row=0, column=0, padx=5, sticky="nw")
            hours_frame = ttk.Frame(frame)
            hours_frame.grid(row=0, column=1, columnspan=3, padx=5, sticky="w")
            
            self.hour_vars = {}
            for hour in range(24):
                var = tk.BooleanVar(value=hour == datetime.now().hour)
                self.hour_vars[hour] = var
                cb = ttk.Checkbutton(hours_frame, text=f"{hour:02d}", variable=var)
                cb.grid(row=hour//6, column=hour%6, padx=1)
            
            ttk.Label(frame, text="Minute:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
            minutes_frame = ttk.Frame(frame)
            minutes_frame.grid(row=1, column=1, columnspan=3, padx=5, sticky="w")
            
            self.minute_vars = {}
            for i, minute in enumerate([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]):
                var = tk.BooleanVar(value=minute == 0 or minute == 30)
                self.minute_vars[minute] = var
                cb = ttk.Checkbutton(minutes_frame, text=f"{minute:02d}", variable=var)
                cb.grid(row=i//6, column=i%6, padx=1)
            
            # Day of week (for Weekly only)
            if schedule_type == "Weekly":
                ttk.Label(frame, text="Day of Week:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
                days_frame = ttk.Frame(frame)
                days_frame.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")
                
                self.day_vars = {}
                days = ["Mon", "Tue", "Wed", "Thu", "Fri"]  # Only business days
                for i, day in enumerate(days):
                    var = tk.BooleanVar(value=True)
                    self.day_vars[day] = var
                    cb = ttk.Checkbutton(days_frame, text=day, variable=var)
                    cb.grid(row=0, column=i, padx=2)
        
        elif schedule_type == "Interval":
            ttk.Label(frame, text="Run every:").grid(row=0, column=0, padx=5, sticky="w")
            
            self.interval_minutes = tk.IntVar(value=5)
            ttk.Spinbox(frame, textvariable=self.interval_minutes, from_=1, to=59, width=4).grid(row=0, column=1, padx=5)
            ttk.Label(frame, text="minutes").grid(row=0, column=2, padx=5, sticky="w")
    
    def browse_script(self):
        """Open file dialog to select Python script"""
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path:
            self.script_path.set(path)
    
    def add_job(self):
        """Add a new scheduled job"""
        script_path = self.script_path.get()
        schedule_type = self.schedule_type.get()
        
        if not script_path or not schedule_type:
            messagebox.showerror("Error", "Please select a script and schedule type")
            return
        
        # Validate and prepare trigger arguments
        try:
            if schedule_type == "Date":
                selected_date = self.calendar.get_date()
                hour = int(self.hour_spin.get())
                minute = int(self.minute_spin.get())
                run_date = datetime.strptime(f"{selected_date} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
                trigger_args = {"run_date": run_date.isoformat()}
                trigger_type = "date"
            
            elif schedule_type == "Daily":
                selected_hours = [str(h) for h, var in self.hour_vars.items() if var.get()]
                selected_minutes = [str(m) for m, var in self.minute_vars.items() if var.get()]
                
                if not selected_hours or not selected_minutes:
                    messagebox.showerror("Error", "Please select at least one hour and one minute")
                    return
                    
                trigger_args = {
                    "hour": ",".join(selected_hours),
                    "minute": ",".join(selected_minutes)
                }
                trigger_type = "cron"
            
            elif schedule_type == "Weekly":
                selected_hours = [str(h) for h, var in self.hour_vars.items() if var.get()]
                selected_minutes = [str(m) for m, var in self.minute_vars.items() if var.get()]
                selected_days = [day for day, var in self.day_vars.items() if var.get()]
                
                if not selected_days:
                    messagebox.showerror("Error", "Please select at least one day of week")
                    return
                if not selected_hours or not selected_minutes:
                    messagebox.showerror("Error", "Please select at least one hour and one minute")
                    return
                    
                trigger_args = {
                    "day_of_week": ",".join(selected_days),
                    "hour": ",".join(selected_hours),
                    "minute": ",".join(selected_minutes)
                }
                trigger_type = "cron"
            
            elif schedule_type == "Interval":
                minutes = self.interval_minutes.get()
                trigger_args = {"minutes": minutes}
                trigger_type = "interval"
            
            elif schedule_type == "Date":
                selected_date = self.calendar.get_date()
                hour = int(self.hour_spin.get())
                minute = int(self.minute_spin.get())
                run_date = datetime.strptime(f"{selected_date} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
                trigger_args = {"run_date": run_date.isoformat()}
                trigger_type = "date"
            
            # Add to database
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO jobs (script_path, trigger_type, trigger_args, status) VALUES (?, ?, ?, 'active')",
                     (script_path, trigger_type, json.dumps(trigger_args)))
            job_id = c.lastrowid
            conn.commit()
            conn.close()
            
            # Add to scheduler
            self.add_job_to_scheduler(job_id, script_path, trigger_type, trigger_args)
            self.populate_job_list()
            
            messagebox.showinfo("Success", "Job scheduled successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule job: {str(e)}")
    
    def add_job_to_scheduler(self, job_id, script_path, trigger_type, trigger_args):
        """Add job to APScheduler with proper trigger"""
        if trigger_type == "date":
            trigger = DateTrigger(run_date=datetime.fromisoformat(trigger_args["run_date"]))
        elif trigger_type == "interval":
            trigger = IntervalTrigger(**trigger_args)
        elif trigger_type == "cron":
            trigger = CronTrigger(**trigger_args)
        
        self.scheduler.add_job(
            run_script, 
            trigger=trigger, 
            args=[job_id, script_path], 
            id=str(job_id)
        )
    
    def remove_job(self):
        """Remove selected job"""
        selection = self.job_list.curselection()
        if not selection:
            return
        
        job_id = self.job_list.get(selection[0]).split(" - ")[0]
        
        # Remove from scheduler
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass
        
        # Remove from database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
        conn.close()
        
        self.populate_job_list()
    
    def populate_job_list(self):
        """Refresh the job list from database"""
        self.job_list.delete(0, tk.END)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, script_path, trigger_type, trigger_args, status FROM jobs")
        
        for row in c.fetchall():
            job_id, script_path, trigger_type, trigger_args, status = row
            trigger_args = json.loads(trigger_args)
            
            if trigger_type == "date":
                desc = f"Run once on {trigger_args['run_date']}"
            elif trigger_type == "interval":
                minutes = trigger_args.get('minutes', 0)
                desc = f"Every {minutes} minute{'s' if minutes != 1 else ''}"
            elif trigger_type == "cron":
                if "day_of_week" in trigger_args:
                    days = str(trigger_args['day_of_week']).replace(',', ', ')
                    hours = str(trigger_args['hour']).replace(',', ', ')
                    minutes = str(trigger_args['minute']).replace(',', ', ')
                    desc = f"Weekly on {days} at {hours}:{minutes}"
                else:
                    hours = str(trigger_args['hour']).replace(',', ', ')
                    minutes = str(trigger_args['minute']).replace(',', ', ')
                    desc = f"Daily at {hours}:{minutes}"
            
            status_text = " (Paused)" if status == "paused" else ""
            self.job_list.insert(tk.END, f"{job_id} - {script_path} ({desc}){status_text}")
        
        conn.close()
    
    def load_jobs(self):
        """Load jobs from database into scheduler"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, script_path, trigger_type, trigger_args FROM jobs")
        
        for row in c.fetchall():
            job_id, script_path, trigger_type, trigger_args = row
            try:
                self.add_job_to_scheduler(job_id, script_path, trigger_type, json.loads(trigger_args))
            except Exception as e:
                print(f"Error loading job {job_id}: {str(e)}")
        
        conn.close()
    
    def on_job_select(self, event):
        """Handle job selection in listbox"""
        selection = self.job_list.curselection()
        if selection:
            job_info = self.job_list.get(selection[0])
            job_id = job_info.split(" - ")[0]
            # Display job logs
            self.display_job_logs(job_id)
    
    def pause_job(self):
        """Pause selected job"""
        selection = self.job_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a job to pause")
            return
        
        job_info = self.job_list.get(selection[0])
        job_id = job_info.split(" - ")[0]
        
        try:
            # Pause in scheduler
            self.scheduler.pause_job(job_id)
            
            # Update status in database
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("UPDATE jobs SET status = 'paused' WHERE id = ?", (job_id,))
            conn.commit()
            conn.close()
            
            self.populate_job_list()
            messagebox.showinfo("Success", f"Job {job_id} paused successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pause job: {str(e)}")
    
    def resume_job(self):
        """Resume selected job"""
        selection = self.job_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a job to resume")
            return
        
        job_info = self.job_list.get(selection[0])
        job_id = job_info.split(" - ")[0]
        
        try:
            # Resume in scheduler
            self.scheduler.resume_job(job_id)
            
            # Update status in database
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("UPDATE jobs SET status = 'active' WHERE id = ?", (job_id,))
            conn.commit()
            conn.close()
            
            self.populate_job_list()
            messagebox.showinfo("Success", f"Job {job_id} resumed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resume job: {str(e)}")
    
    def run_selected_job_now(self):
        """Execute the selected job immediately"""
        selection = self.job_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a job to run")
            return
        
        job_info = self.job_list.get(selection[0])
        job_id = job_info.split(" - ")[0]
        
        try:
            # Get job details from database
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT script_path FROM jobs WHERE id = ?", (job_id,))
            script_path = c.fetchone()[0]
            conn.close()
            
            # Run the job immediately
            self.scheduler.add_job(
                run_script,
                trigger=None,
                args=[job_id, script_path],
                id=f"{job_id}_now"
            )
            
            messagebox.showinfo("Success", f"Job {job_id} is being executed now!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run job: {str(e)}")
    
    def on_closing(self):
        """Handle application shutdown"""
        self.scheduler.shutdown()
        self.root.destroy()

    def display_job_logs(self, job_id):
        """Display logs for the selected job"""
        # Clear existing logs
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        
        # Fetch logs from database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT execution_time, log_output FROM job_logs WHERE job_id = ? ORDER BY execution_time DESC", (job_id,))
        logs = c.fetchall()
        conn.close()
        
        if not logs:
            self.log_text.insert(tk.END, "No logs available for this job.")
        else:
            for timestamp, log in logs:
                self.log_text.insert(tk.END, f"Execution at {timestamp}:\n{log}\n{'-'*50}\n")
        
        self.log_text.configure(state="disabled")

def main():
    root = tk.Tk()
    app = SchedulerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    sv_ttk.set_theme(darkdetect.theme())
    root.mainloop()

if __name__ == "__main__":
    main()
