import tkinter as tk
from tkinter import ttk, messagebox

# Core CPU scheduling logic
#function for first come first serve
def fcfs(processes):
    processes.sort(key=lambda x: x['arrival'])
    n = len(processes)
    completion_time = [0] * n
    gantt = []
    time = 0

    for i in range(n):
        process = processes[i]
        if time < process['arrival']:
            time = process['arrival']
        gantt.append((process['id'], time))
        time += process['burst']
        completion_time[i] = time

    tat, wt = calculate_metrics(processes, completion_time)
    return gantt, tat, wt

#for priority scheduling
def priority_scheduling(processes):
    processes.sort(key=lambda x: (x['arrival'], x['priority']))
    n = len(processes)
    completion_time = [0] * n
    gantt = []
    time = 0
    completed = 0
    visited = [False] * n

    while completed < n:
        candidates = [
            (i, p) for i, p in enumerate(processes)
            if not visited[i] and p['arrival'] <= time
        ]
        if not candidates:
            time += 1
            continue

        idx, selected = min(candidates, key=lambda x: x[1]['priority'])
        gantt.append((selected['id'], time))
        time += selected['burst']
        completion_time[idx] = time
        visited[idx] = True
        completed += 1

    tat, wt = calculate_metrics(processes, completion_time)
    return gantt, tat, wt

#for round robin
def round_robin(processes, time_quantum):
    n = len(processes)
    remaining_burst = [p['burst'] for p in processes]
    arrival_time = [p['arrival'] for p in processes]
    completion_time = [0] * n
    tat = [0] * n
    wt = [0] * n
    gantt = []

    time = 0
    ready_queue = []

    while True:
        # Add processes to the ready queue that have arrived
        for i, process in enumerate(processes):
            if process['arrival'] <= time and i not in ready_queue and remaining_burst[i] > 0:
                ready_queue.append(i)

        if not ready_queue:  # If the ready queue is empty, increment time
            time += 1
            continue

        # Get the first process from the ready queue
        current_process = ready_queue.pop(0)

        # Execute the process for the time quantum or until it finishes
        if remaining_burst[current_process] > time_quantum:
            gantt.append((processes[current_process]['id'], time))
            time += time_quantum
            remaining_burst[current_process] -= time_quantum
        else:
            gantt.append((processes[current_process]['id'], time))
            time += remaining_burst[current_process]
            remaining_burst[current_process] = 0
            completion_time[current_process] = time

        # Re-add the process to the queue if it's not finished
        if remaining_burst[current_process] > 0:
            ready_queue.append(current_process)

        # Break when all processes are finished
        if all(burst == 0 for burst in remaining_burst):
            break

    # Calculate Turnaround Time (TAT) and Waiting Time (WT)
    for i in range(n):
        tat[i] = completion_time[i] - arrival_time[i]
        wt[i] = tat[i] - processes[i]['burst']

    return gantt, tat, wt


def srtf(processes):
    processes = sorted(processes, key=lambda x: x['arrival'])  # Sort by arrival time
    n = len(processes)
    remaining_burst = [p['burst'] for p in processes]
    completion_time = [0] * n
    tat = [0] * n
    wt = [0] * n
    gantt = []

    current_time = 0
    completed = 0
    while completed < n:
        # Find the process with the shortest remaining burst time that has arrived
        idx = -1
        min_burst = float('inf')
        for i in range(n):
            if processes[i]['arrival'] <= current_time and remaining_burst[i] > 0:
                if remaining_burst[i] < min_burst:
                    min_burst = remaining_burst[i]
                    idx = i

        if idx == -1:  # No process is ready
            current_time += 1
            continue

        # Execute the process
        gantt.append((processes[idx]['id'], current_time))
        remaining_burst[idx] -= 1
        current_time += 1

        # If the process is completed
        if remaining_burst[idx] == 0:
            completed += 1
            completion_time[idx] = current_time

    # Calculate Turnaround Time (TAT) and Waiting Time (WT)
    for i in range(n):
        tat[i] = completion_time[i] - processes[i]['arrival']
        wt[i] = tat[i] - processes[i]['burst']

    return gantt, tat, wt

def calculate_metrics(processes, completion_time):
    n = len(processes)
    turnaround_time = [0] * n
    waiting_time = [0] * n

    for i in range(n):
        turnaround_time[i] = completion_time[i] - processes[i]['arrival']
        waiting_time[i] = turnaround_time[i] - processes[i]['burst']

    return turnaround_time, waiting_time

# Helper functions for GUI
def run_algorithm():
    selected_algo = algorithm_var.get()
    processes = []
    for row in process_table.get_children():
        values = process_table.item(row, 'values')
        processes.append({
            'id': values[0],
            'arrival': int(values[1]),
            'burst': int(values[2]),
            'priority': int(values[3]) if len(values) > 3 else None
        })

    if not processes:
        messagebox.showerror("Error", "No processes added.")
        return

    time_quantum = None
    if selected_algo == "Round Robin":
        try:
            time_quantum = int(time_quantum_entry.get())
            if time_quantum <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid Time Quantum.")
            return

    if selected_algo == "First-Come-First-Serve":
        gantt, tat, wt = fcfs(processes)
    elif selected_algo == "Priority Scheduling":
        gantt, tat, wt = priority_scheduling(processes)
    elif selected_algo == "Round Robin":
        gantt, tat, wt = round_robin(processes, time_quantum)
    elif selected_algo == "Shortest Remaining Time First":
        gantt, tat, wt = srtf(processes)
    else:
        messagebox.showerror("Error", "Select a scheduling algorithm.")
        return

    display_results(gantt, tat, wt)

def display_results(gantt, tat, wt):
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Gantt Chart:\n")
    for process, start_time in gantt:
        result_text.insert(tk.END, f"P{process} at time {start_time}\n")
    result_text.insert(tk.END, "\nTurnaround Times:\n")
    result_text.insert(tk.END, f"{tat}\n")
    result_text.insert(tk.END, "\nWaiting Times:\n")
    result_text.insert(tk.END, f"{wt}\n")

# GUI Setup
root = tk.Tk()
root.title("CPU Scheduling Algorithms")

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

process_table = ttk.Treeview(input_frame, columns=("ID", "Arrival", "Burst", "Priority"), show="headings")
process_table.heading("ID", text="Process ID")
process_table.heading("Arrival", text="Arrival Time")
process_table.heading("Burst", text="Burst Time")
process_table.heading("Priority", text="Priority (Optional)")
process_table.pack()

add_button = tk.Button(input_frame, text="Add Process", command=lambda: add_process(process_table))
add_button.pack(side=tk.LEFT, padx=5)

remove_button = tk.Button(input_frame, text="Remove Selected", command=lambda: process_table.delete(*process_table.selection()))
remove_button.pack(side=tk.LEFT, padx=5)

# Algorithm Selection
algo_frame = tk.Frame(root)
algo_frame.pack(pady=10)

algorithm_var = tk.StringVar()
algorithm_var.set("Select Algorithm")
algorithm_menu = ttk.OptionMenu(
    algo_frame, algorithm_var, "Select Algorithm",
    "First-Come-First-Serve", "Priority Scheduling", "Round Robin",
    "Shortest Remaining Time First"
)
algorithm_menu.pack(side=tk.LEFT, padx=5)

time_quantum_label = tk.Label(algo_frame, text="Time Quantum:")
time_quantum_label.pack(side=tk.LEFT, padx=5)

time_quantum_entry = tk.Entry(algo_frame)
time_quantum_entry.pack(side=tk.LEFT, padx=5)

run_button = tk.Button(algo_frame, text="Run", command=run_algorithm)
run_button.pack(side=tk.LEFT, padx=5)

# Results Frame
results_frame = tk.Frame(root)
results_frame.pack(pady=10)

result_text = tk.Text(results_frame, height=15, width=50)
result_text.pack()
def add_process(tree):
    def save_process():
        process_id = entry_id.get()
        arrival_time = entry_arrival.get()
        burst_time = entry_burst.get()
        priority = entry_priority.get()

        # Validate input
        if not process_id or not arrival_time or not burst_time:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            arrival_time = int(arrival_time)
            burst_time = int(burst_time)
            priority = int(priority) if priority else None
        except ValueError:
            messagebox.showerror("Error", "Arrival Time, Burst Time, and Priority must be integers.")
            return

        tree.insert("", "end", values=(process_id, arrival_time, burst_time, priority))
        add_window.destroy()

    # Create a new window for adding a process
    add_window = tk.Toplevel(root)
    add_window.title("Add Process")

    tk.Label(add_window, text="Process ID:").grid(row=0, column=0, padx=5, pady=5)
    entry_id = tk.Entry(add_window)
    entry_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(add_window, text="Arrival Time:").grid(row=1, column=0, padx=5, pady=5)
    entry_arrival = tk.Entry(add_window)
    entry_arrival.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(add_window, text="Burst Time:").grid(row=2, column=0, padx=5, pady=5)
    entry_burst = tk.Entry(add_window)
    entry_burst.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(add_window, text="Priority (Optional):").grid(row=3, column=0, padx=5, pady=5)
    entry_priority = tk.Entry(add_window)
    entry_priority.grid(row=3, column=1, padx=5, pady=5)

    save_button = tk.Button(add_window, text="Save", command=save_process)
    save_button.grid(row=4, column=0, columnspan=2, pady=10)


root.mainloop()
