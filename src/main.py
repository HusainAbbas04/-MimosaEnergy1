# 01: Import necessary libraries
from PIL import Image, ImageTk
import tkinter as tk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# Constants for energy levels and update intervals
BASELINE_ENERGY = 0.5  # Baseline energy level in µW
SPIKE_ENERGY = 1.5     # Energy spike level in µW
UPDATE_INTERVAL = 1000  # Interval in ms for live updates
# 02: Initialize main window
root = tk.Tk()
root.title("Mimosa Energy")
root.geometry("800x600")
root.resizable(True, True)  # Allow window to be resizable
# 02 A: Add a Canvas and Scrollbar to make the window scrollable
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(canvas_frame)
scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a frame for all content inside the canvas
content_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Update the scroll region when content is added
def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

content_frame.bind("<Configure>", update_scroll_region)
# 03: Define paths for open and closed plant images
current_dir = os.path.dirname(os.path.abspath(__file__))
open_image_path = os.path.join(current_dir, "images/open.png")
close_image_path = os.path.join(current_dir, "images/close.png")

# Load, resize, and convert images for display
try:
    plant_img_open = ImageTk.PhotoImage(Image.open(open_image_path).resize((200, 200)))
    plant_img_closed = ImageTk.PhotoImage(Image.open(close_image_path).resize((200, 200)))
except FileNotFoundError:
    print(f"Error: Image files not found at {open_image_path} or {close_image_path}")
    plant_img_open = plant_img_closed = None  # Use default placeholder images if needed

# Display initial plant image in a label
plant_label = tk.Label(content_frame, image=plant_img_open)
plant_label.pack()
# 04: Welcome label at the top
welcome_label = tk.Label(content_frame, text="Welcome to the MIMOSA Energy Dashboard")
welcome_label.pack()

# 05: Function to simulate sensor data
def get_sensor_data():
    return random.uniform(BASELINE_ENERGY, SPIKE_ENERGY)

# 06: Create figure and axis for Matplotlib chart
fig, ax = plt.subplots()
canvas_chart = FigureCanvasTkAgg(fig, master=content_frame)
canvas_chart.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Configure plot limits and styling
ax.set_title('Energy Production (µW)', color='blue')
ax.set_xlabel('Time (seconds)', color='green')
ax.set_ylabel('Energy (µW)', color='green')
ax.set_ylim(0, 2)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Initialize plot line and data lists
line, = ax.plot([], [], lw=2, color='red', label='Energy Production')
ax.legend(loc='upper right')

# Initialize data lists for time and energy
time_data = []
energy_data = []
# 07: Function to update chart with new energy value
def update_chart():
    global time_data, energy_data, current_energy, last_annotation
    time_data.append(len(time_data))
    energy_data.append(current_energy)

    if len(time_data) > 60:
        time_data, energy_data = time_data[-60:], energy_data[-60:]

    line.set_data(range(len(time_data)), energy_data)
    ax.set_xlim(0, 60)

    if 'last_annotation' in globals() and last_annotation:
        last_annotation.remove()

    if current_energy > BASELINE_ENERGY:
        y_offset = 15 if current_energy < 1.5 else -15
        last_annotation = ax.annotate(f'{current_energy:.2f} µW',
                                      xy=(len(time_data)-1, current_energy),
                                      textcoords='offset points',
                                      xytext=(0, y_offset),
                                      ha='center',
                                      color='blue',
                                      fontsize=8,
                                      bbox=dict(boxstyle="round,pad=0.3", edgecolor="blue", facecolor="lightyellow"))
    else:
        last_annotation = None

    canvas_chart.draw()
# 08: Initialize energy level
current_energy = BASELINE_ENERGY
update_chart()  # Initial update to set base level
# 09: Function to simulate continuous energy readings
def live_update():
    global current_energy
    if update_active:
        current_energy = get_sensor_data()
        update_chart()
        root.after(UPDATE_INTERVAL, live_update)
    else:
        current_energy = BASELINE_ENERGY
        plant_label.config(image=plant_img_closed)

# 10: Function to display flow chart
def display_flow_chart():
    flow_chart = """
    Energy Production Flow Chart:
    1. Plant Movement Detected by Sensors
    2. Energy Spike Generated (1.5 µW)
    3. Energy Decay to Baseline (0.5 µW)
    4. Energy Stored in Battery or Flywheel
    5. Energy Utilization for Dashboard Visualization
    """
    flow_chart_label.config(text=flow_chart)

# Flow chart display button
flow_chart_button = tk.Button(content_frame, text="Show Flow Chart", command=display_flow_chart)
flow_chart_button.pack()

# Flow chart label
flow_chart_label = tk.Label(content_frame, text="")
flow_chart_label.pack()
# 11: Function to simulate flywheel mechanism
def simulate_flywheel():
    global flywheel_energy
    flywheel_energy += current_energy  # Add current energy to flywheel storage
    flywheel_energy_label.config(text=f"Flywheel Energy: {flywheel_energy:.2f} µW")
    root.after(UPDATE_INTERVAL, simulate_flywheel)

# Initialize flywheel energy storage
flywheel_energy = 0.0

# Flywheel energy label
flywheel_energy_label = tk.Label(content_frame, text=f"Flywheel Energy: {flywheel_energy:.2f} µW")
flywheel_energy_label.pack()

# Start flywheel simulation
simulate_flywheel()
# 12: Function to update battery status
def update_battery_status():
    global battery_energy
    if current_energy > BASELINE_ENERGY:
        battery_energy += current_energy - BASELINE_ENERGY  # Charge battery with excess energy
    else:
        battery_energy is max(0, battery_energy - BASELINE_ENERGY + current_energy)  # Discharge battery to maintain baseline

    battery_energy_label.config(text=f"Battery Energy: {battery_energy:.2f} µW")
    root.after(UPDATE_INTERVAL, update_battery_status)

# Initialize battery energy storage
battery_energy = 0.0

# Battery energy label
battery_energy_label = tk.Label(content_frame, text=f"Battery Energy: {battery_energy:.2f} µW")
battery_energy_label.pack()

# Start battery status updates
update_battery_status()
# 13: Function to start and stop live updates for 1 plant
update_active = False  # Variable to control if updates are active

def start_updates():
    global update_active, current_energy
    update_active = True  # Activate live updates
    current_energy = SPIKE_ENERGY
    plant_label.config(image=plant_img_open)
    live_update()  # Start live updates

def stop_updates():
    global update_active, current_energy
    update_active = False  # Deactivate live updates
    current_energy = BASELINE_ENERGY
    plant_label.config(image=plant_img_closed)

# Create a frame to hold the start and stop buttons for 1-plant simulation
button_frame_1 = tk.Frame(content_frame)
button_frame_1.pack(side=tk.TOP, pady=10)

# Create Start and Stop buttons for 1-plant simulation
start_button = tk.Button(button_frame_1, text="Start", command=start_updates)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(button_frame_1, text="Stop", command=stop_updates)
stop_button.pack(side=tk.LEFT, padx=10)


stop_button = tk.Button(button_frame_1, text="Stop", command=stop_updates)
stop_button.pack(side=tk.LEFT, padx=10)
# 14: Create a new figure and axis for the 100-plant chart
chart_frame_100 = tk.Frame(content_frame)
chart_frame_100.pack(fill=tk.BOTH, expand=True)

fig_100, ax_100 = plt.subplots()
canvas_100 = FigureCanvasTkAgg(fig_100, master=chart_frame_100)
canvas_100.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Configure plot limits and styling for 100 plants
ax_100.set_title('Energy Production from 100 Plants (µW)', color='blue')
ax_100.set_xlabel('Time (seconds)', color='green')
ax_100.set_ylabel('Energy (µW)', color='green')
ax_100.set_ylim(0, 200)
ax_100.grid(True, linestyle='--', linewidth=0.5)

# Initialize plot line and data lists for 100-plant simulation
line_100, = ax_100.plot([], [], lw=2, color='purple', label='100 Plants Energy Production')
ax_100.legend(loc='upper right')

# Initialize data lists for time and energy for 100 plants
time_data_100 = []
energy_data_100 = []

def update_chart_100():
    global time_data_100, energy_data_100, current_energy
    time_data_100.append(len(time_data_100))
    energy_data_100.append(current_energy * 100)

    if len(time_data_100) > 60:
        time_data_100, energy_data_100 = time_data_100[-60:], energy_data_100[-60:]

    line_100.set_data(range(len(time_data_100)), energy_data_100)
    ax_100.set_xlim(0, max(60, len(time_data_100)))
    canvas_100.draw()

energy_data_100 = []
# 15: Function to update chart with new energy value for 100 plants
def update_chart_100():
    global time_data_100, energy_data_100, current_energy
    time_data_100.append(len(time_data_100))
    energy_data_100.append(current_energy * 100)

    if len(time_data_100) > 60:
        time_data_100, energy_data_100 = time_data_100[-60:], energy_data_100[-60:]

    line_100.set_data(range(len(time_data_100)), energy_data_100)
    ax_100.set_xlim(0, max(60, len(time_data_100)))
    canvas_100.draw()
# 16: Function to simulate continuous energy readings for 100 plants
def live_update_100():
    if update_active_100:
        current_energy = get_sensor_data()
        update_chart_100()
        root.after(UPDATE_INTERVAL, live_update_100)

# 17: Function to start and stop updates for 100 plants
update_active_100 = False  # Variable to control if updates are active

def start_updates_100():
    global update_active_100
    update_active_100 = True  # Activate live updates for 100 plants
    live_update_100()  # Start live updates for 100 plants

def stop_updates_100():
    global update_active_100
    update_active_100 = False  # Deactivate live updates for 100 plants

# Create a frame to hold the start and stop buttons for 100-plant simulation
button_frame_100 = tk.Frame(content_frame)
button_frame_100.pack(side=tk.TOP, pady=10)

# Create Start and Stop buttons for 100-plant simulation
start_button_100 = tk.Button(button_frame_100, text="Start 100 Plants", command=start_updates_100)
start_button_100.pack(side=tk.LEFT, padx=10)

stop_button_100 = tk.Button(button_frame_100, text="Stop 100 Plants", command=stop_updates_100)
stop_button_100.pack(side=tk.LEFT, padx=10)




#last block
root.mainloop()
