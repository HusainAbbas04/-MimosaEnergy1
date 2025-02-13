# 01: Import necessary libraries
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import csv
import time

# Constants for energy levels and update intervals
BASELINE_ENERGY = 0.5  # Baseline energy level in µW
SPIKE_ENERGY = 1.5     # Energy spike level in µW
UPDATE_INTERVAL = 1000  # Interval in ms for live updates
ENERGY_PER_PLANT = 2    # Energy produced by one plant in mV every 10 minutes

# 02: Initialize main window
root = tk.Tk()
root.title("Mimosa Energy")
root.geometry("1200x800")  # Increased width for better layout
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
open_image_path_1 = os.path.join(current_dir, "images/open_1.png")
close_image_path_1 = os.path.join(current_dir, "images/close_1.png")
open_image_path_100 = os.path.join(current_dir, "images/open_100.png")
close_image_path_100 = os.path.join(current_dir, "images/close_100.png")
open_image_path_custom = os.path.join(current_dir, "images/open_custom.png")
close_image_path_custom = os.path.join(current_dir, "images/close_custom.png")

# Load, resize, and convert images for display
def load_image(open_path, close_path):
    try:
        img_open = ImageTk.PhotoImage(Image.open(open_path).resize((200, 200)))
        img_closed = ImageTk.PhotoImage(Image.open(close_path).resize((200, 200)))
        return img_open, img_closed
    except FileNotFoundError:
        print(f"Error: Image files not found at {open_path} or {close_path}")
        return None, None  # Use default placeholder images if needed

plant_img_open_1, plant_img_closed_1 = load_image(open_image_path_1, close_image_path_1)
plant_img_open_100, plant_img_closed_100 = load_image(open_image_path_100, close_image_path_100)
plant_img_open_custom, plant_img_closed_custom = load_image(open_image_path_custom, close_image_path_custom)

# 04: Welcome label at the top
welcome_label = tk.Label(content_frame, text="Welcome to the MIMOSA Energy Dashboard", font=("Arial", 16))
welcome_label.grid(row=0, column=0, columnspan=3, pady=10)

# 05: Function to simulate sensor data
def get_sensor_data():
    return random.uniform(BASELINE_ENERGY, SPIKE_ENERGY)

# 06: Create figure and axis for Matplotlib chart for 1 plant
fig_1, ax_1 = plt.subplots()
canvas_chart_1 = FigureCanvasTkAgg(fig_1, master=content_frame)
canvas_chart_1.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

# Configure plot limits and styling for 1 plant
ax_1.set_title('Energy Production from 1 Plant (µW)', color='blue')
ax_1.set_xlabel('Time (seconds)', color='green')
ax_1.set_ylabel('Energy (µW)', color='green')
ax_1.set_ylim(0, 2)
ax_1.grid(True, which='both', linestyle='--', linewidth=0.5)

# Initialize plot line and data lists for 1 plant
line_1, = ax_1.plot([], [], lw=2, color='red', label='Energy Production')
ax_1.legend(loc='upper right')

# Initialize data lists for time and energy for 1 plant
time_data_1 = []
energy_data_1 = []

# 07: Function to update chart with new energy value for 1 plant
def update_chart_1():
    global time_data_1, energy_data_1, current_energy_1, last_annotation_1
    time_data_1.append(len(time_data_1))
    energy_data_1.append(current_energy_1)

    if len(time_data_1) > 60:
        time_data_1, energy_data_1 = time_data_1[-60:], energy_data_1[-60:]

    line_1.set_data(range(len(time_data_1)), energy_data_1)
    ax_1.set_xlim(0, 60)

    if 'last_annotation_1' in globals() and last_annotation_1:
        last_annotation_1.remove()

    if current_energy_1 > BASELINE_ENERGY:
        y_offset = 15 if current_energy_1 < 1.5 else -15
        last_annotation_1 = ax_1.annotate(f'{current_energy_1:.2f} µW',
                                      xy=(len(time_data_1)-1, current_energy_1),
                                      textcoords='offset points',
                                      xytext=(0, y_offset),
                                      ha='center',
                                      color='blue',
                                      fontsize=8,
                                      bbox=dict(boxstyle="round,pad=0.3", edgecolor="blue", facecolor="lightyellow"))
    else:
        last_annotation_1 = None

    canvas_chart_1.draw()

# 08: Initialize energy level for 1 plant
current_energy_1 = BASELINE_ENERGY
update_chart_1()  # Initial update to set base level

# 09: Function to simulate continuous energy readings for 1 plant
def live_update_1():
    global current_energy_1
    if update_active_1:
        current_energy_1 = get_sensor_data()
        update_chart_1()
        root.after(UPDATE_INTERVAL, live_update_1)
    else:
        current_energy_1 = BASELINE_ENERGY
        plant_label_1.config(image=plant_img_closed_1)

# 10: Function to handle plant touch for 1 plant
def touch_plant_1():
    global current_energy_1
    current_energy_1 = ENERGY_PER_PLANT / 600  # Convert mV to µW for 10 minutes
    plant_label_1.config(image=plant_img_closed_1)
    
    # Update the chart immediately to show the spike
    update_chart_1()
    
    # Schedule to return to baseline energy after 3 seconds
    root.after(3000, return_to_baseline_1)  # Return to baseline after 3 seconds

def return_to_baseline_1():
    global current_energy_1
    current_energy_1 = BASELINE_ENERGY  # Return to baseline energy
    update_chart_1()  # Update the chart to reflect the change
    plant_label_1.config(image=plant_img_open_1)  # Revert image back

# Create a frame for the 1 plant section
plant_frame_1 = tk.Frame(content_frame)
plant_frame_1.grid(row=1, column=1, padx=10, pady=10)

# Display initial plant image in a label for 1 plant
plant_label_1 = tk.Label(plant_frame_1, image=plant_img_open_1)
plant_label_1.pack()

# Button to touch the plant for 1 plant
touch_button_1 = tk.Button(plant_frame_1, text="Touch Plant 1", command=touch_plant_1)
touch_button_1.pack()

# 11: Create figure and axis for Matplotlib chart for 100 plants
fig_100, ax_100 = plt.subplots()
canvas_chart_100 = FigureCanvasTkAgg(fig_100, master=content_frame)
canvas_chart_100.get_tk_widget().grid(row=2, column=0, padx=10, pady=10)

# Configure plot limits and styling for 100 plants
ax_100.set_title('Energy Production from 100 Plants (µW)', color='blue')
ax_100.set_xlabel('Time (seconds)', color='green')
ax_100.set_ylabel('Energy (µW)', color='green')
ax_100.set_ylim(0, 200)
ax_100.grid(True, which='both', linestyle='--', linewidth=0.5)

# Initialize plot line and data lists for 100 plants
line_100, = ax_100.plot([], [], lw=2, color='purple', label='100 Plants Energy Production')
ax_100.legend(loc='upper right')

# Initialize data lists for time and energy for 100 plants
time_data_100 = []
energy_data_100 = []

# 12: Function to update chart with new energy value for 100 plants
def update_chart_100():
    global time_data_100, energy_data_100, current_energy_100, last_annotation_100
    time_data_100.append(len(time_data_100))
    energy_data_100.append(current_energy_100 * 100)  # Scale for 100 plants

    if len(time_data_100) > 60:
        time_data_100, energy_data_100 = time_data_100[-60:], energy_data_100[-60:]

    line_100.set_data(range(len(time_data_100)), energy_data_100)
    ax_100.set_xlim(0, max(60, len(time_data_100)))

    canvas_chart_100.draw()

# 13: Function to simulate continuous energy readings for 100 plants
def live_update_100():
    global current_energy_100
    if update_active_100:
        current_energy_100 = get_sensor_data()
        update_chart_100()
        root.after(UPDATE_INTERVAL, live_update_100)

# 14: Function to handle plant touch for 100 plants
def touch_plant_100():
    global current_energy_100
    current_energy_100 = ENERGY_PER_PLANT / 600  # Convert mV to µW for 10 minutes
    plant_label_100.config(image=plant_img_closed_100)
    
    # Update the chart immediately to show the spike
    update_chart_100()
    
    # Schedule to return to baseline energy after 3 seconds
    root.after(3000, return_to_baseline_100)  # Return to baseline after 3 seconds

def return_to_baseline_100():
    global current_energy_100
    current_energy_100 = BASELINE_ENERGY  # Return to baseline energy
    update_chart_100()  # Update the chart to reflect the change
    plant_label_100.config(image=plant_img_open_100)  # Revert image back

# Create a frame for the 100 plants section
plant_frame_100 = tk.Frame(content_frame)
plant_frame_100.grid(row=2, column=1, padx=10, pady=10)

# Display initial plant image in a label for 100 plants
plant_label_100 = tk.Label(plant_frame_100, image=plant_img_open_100)
plant_label_100.pack()

# Button to touch the plant for 100 plants
touch_button_100 = tk.Button(plant_frame_100, text="Touch 100 Plants", command=touch_plant_100)
touch_button_100.pack()

# 15: Create figure and axis for customizable input plants
fig_custom, ax_custom = plt.subplots()
canvas_chart_custom = FigureCanvasTkAgg(fig_custom, master=content_frame)
canvas_chart_custom.get_tk_widget().grid(row=3, column=0, padx=10, pady=10)

# Configure plot limits and styling for customizable plants
ax_custom.set_title('Energy Production from Custom Plants (µW)', color='blue')
ax_custom.set_xlabel('Time (seconds)', color='green')
ax_custom.set_ylabel('Energy (µW)', color='green')
ax_custom.set_ylim(0, 200)  # Initial limit
ax_custom.grid(True, which='both', linestyle='--', linewidth=0.5)

# Initialize plot line and data lists for customizable plants
line_custom, = ax_custom.plot([], [], lw=2, color='orange', label='Custom Plants Energy Production')
ax_custom.legend(loc='upper right')

# Initialize data lists for time and energy for customizable plants
time_data_custom = []
energy_data_custom = []

# Create a frame for the customizable plants section
plant_frame_custom = tk.Frame(content_frame)
plant_frame_custom.grid(row=3, column=1, padx=10, pady=10)

# Entry for customizable plant count
custom_plant_count = tk.IntVar(value=1)  # Default to 1 plant
custom_plant_entry = tk.Entry(plant_frame_custom, textvariable=custom_plant_count)
custom_plant_entry.pack(side=tk.LEFT)
custom_plant_label = tk.Label(plant_frame_custom, text="Enter number of custom plants:")
custom_plant_label.pack(side=tk.LEFT)

# Function to update chart with new energy value for customizable plants
def update_chart_custom():
    global time_data_custom, energy_data_custom, current_energy_custom, last_annotation_custom
    time_data_custom.append(len(time_data_custom))
    energy_data_custom.append(current_energy_custom * custom_plant_count.get())  # Scale for custom plants

    if len(time_data_custom) > 60:
        time_data_custom, energy_data_custom = time_data_custom[-60:], energy_data_custom[-60:]

    line_custom.set_data(range(len(time_data_custom)), energy_data_custom)

    # Dynamically set the y-axis limit based on the number of custom plants
    max_energy = custom_plant_count.get() * ENERGY_PER_PLANT / 600  # Maximum energy in µW
    ax_custom.set_ylim(0, max(200, max_energy * 1.2))  # Set a minimum of 200 or 20% more than max energy

    ax_custom.set_xlim(0, max(60, len(time_data_custom)))

    canvas_chart_custom.draw()

# Function to update the graph when the custom plant count changes
def update_graph_on_change(*args):
    update_chart_custom()  # Update the graph with the new count

# Trace changes to the custom plant count
custom_plant_count.trace("w", update_graph_on_change)

# 17: Function to simulate continuous energy readings for customizable plants
def live_update_custom():
    global current_energy_custom
    if update_active_custom:
        current_energy_custom = get_sensor_data()
        update_chart_custom()
        root.after(UPDATE_INTERVAL, live_update_custom)

# 18: Function to handle plant touch for customizable plants
def touch_plant_custom():
    global current_energy_custom
    current_energy_custom = ENERGY_PER_PLANT / 600  # Convert mV to µW for 10 minutes
    plant_label_custom.config(image=plant_img_closed_custom)
    
    # Update the chart immediately to show the spike
    update_chart_custom()
    
    # Schedule to return to baseline energy after 3 seconds
    root.after(3000, return_to_baseline_custom)  # Return to baseline after 3 seconds

def return_to_baseline_custom():
    global current_energy_custom
    current_energy_custom = BASELINE_ENERGY  # Return to baseline energy
    update_chart_custom()  # Update the chart to reflect the change
    plant_label_custom.config(image=plant_img_open_custom)  # Revert image back

# Create a frame for the customizable plants section
plant_frame_custom = tk.Frame(content_frame)
plant_frame_custom.grid(row=3, column=1, padx=10, pady=10)

# Display initial plant image in a label for customizable plants
plant_label_custom = tk.Label(plant_frame_custom, image=plant_img_open_custom)
plant_label_custom.pack()

# Button to touch the plant for customizable plants
touch_button_custom = tk.Button(plant_frame_custom, text="Touch Custom Plants", command=touch_plant_custom)
touch_button_custom.pack()

# Entry for customizable plant count
custom_plant_count = tk.IntVar(value=1)  # Default to 1 plant
custom_plant_entry = tk.Entry(plant_frame_custom, textvariable=custom_plant_count)
custom_plant_entry.pack(side=tk.LEFT)
custom_plant_label = tk.Label(plant_frame_custom, text="Enter number of custom plants:")
custom_plant_label.pack(side=tk.LEFT)

# 19: Start and stop controls for 1 plant
update_active_1 = False  # Variable to control if updates are active

def start_updates_1():
    global update_active_1
    update_active_1 = True  # Activate live updates for 1 plant
    live_update_1()  # Start live updates for 1 plant

def stop_updates_1():
    global update_active_1
    update_active_1 = False  # Deactivate live updates for 1 plant

# Create Start and Stop buttons for 1-plant simulation
button_frame_1 = tk.Frame(content_frame)
button_frame_1.grid(row=4, column=0, columnspan=2, pady=10)

start_button_1 = tk.Button(button_frame_1, text="Start 1 Plant", command=start_updates_1)
start_button_1.pack(side=tk.LEFT, padx=10)

stop_button_1 = tk.Button(button_frame_1, text="Stop 1 Plant", command=stop_updates_1)
stop_button_1.pack(side=tk.LEFT, padx=10)

# 20: Start and stop controls for 100 plants
update_active_100 = False  # Variable to control if updates are active

def start_updates_100():
    global update_active_100
    update_active_100 = True  # Activate live updates for 100 plants
    live_update_100()  # Start live updates for 100 plants

def stop_updates_100():
    global update_active_100
    update_active_100 = False  # Deactivate live updates for 100 plants

# Create Start and Stop buttons for 100-plant simulation
button_frame_100 = tk.Frame(content_frame)
button_frame_100.grid(row=5, column=0, columnspan=2, pady=10)

start_button_100 = tk.Button(button_frame_100, text="Start 100 Plants", command=start_updates_100)
start_button_100.pack(side=tk.LEFT, padx=10)

stop_button_100 = tk.Button(button_frame_100, text="Stop 100 Plants", command=stop_updates_100)
stop_button_100.pack(side=tk.LEFT, padx=10)

# 21: Start and stop controls for customizable plants
update_active_custom = False  # Variable to control if updates are active

def start_updates_custom():
    global update_active_custom
    update_active_custom = True  # Activate live updates for custom plants
    live_update_custom()  # Start live updates for custom plants

def stop_updates_custom():
    global update_active_custom
    update_active_custom = False  # Deactivate live updates for custom plants

# Create Start and Stop buttons for customizable plant simulation
button_frame_custom = tk.Frame(content_frame)
button_frame_custom.grid(row=6, column=0, columnspan=2, pady=10)

start_button_custom = tk.Button(button_frame_custom, text="Start Custom Plants", command=start_updates_custom)
start_button_custom.pack(side=tk.LEFT, padx=10)

stop_button_custom = tk.Button(button_frame_custom, text="Stop Custom Plants", command=stop_updates_custom)
stop_button_custom.pack(side=tk.LEFT, padx=10)

# Last block
root.mainloop()