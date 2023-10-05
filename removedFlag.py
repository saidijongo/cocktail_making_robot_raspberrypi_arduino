#!/usr/bin/python3
# -*- coding: utf8 -*-

#THE REAL DEAL
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import requests
from io import BytesIO
import RPi.GPIO as GPIO
import time
import os
import threading
import serial


# Defining the GPIO pins connected to the relay module
relay_pins = [26, 21, 19, 15, 13, 11, 7, 5, 31, 33, 35]
#pump_running = False

# Initialize GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

# Flow rate of the pump motors in mL/second
flow_rate = 1.5

# Loading recipes from JSON
#with open('/home/jongo/Desktop/cbr/ex/nanugi.json') as file:
with open('/home/damin/Desktop/cbr/holiday.json') as file:
    recipes = json.load(file)

# Map the index of relay_pins with the pump motor number
motor_mapping = {i + 1: pin for i, pin in enumerate(relay_pins)}

# Variables to record start and end times for each pump
pump_start_times = {}
pump_end_times = {}

# Variable to record the cocktail start time
cocktail_start_time = None

# Mutex to synchronize motor pumping when selected_motor is not "All Motors"
motor_mutex = threading.Lock()

# Define the serial port and baud rate for Arduino communication
#ser = serial.Serial('/dev/ttyUSB0', 115200)  # Update the port as needed


# Function to send commands to the Arduino
#def send_command_to_arduino(command):
#    ser.write(command.encode())
#    print(f"Sent command {command} to Arduino")


try:
    ser = serial.Serial('/dev/ttyUSB0', 115200) 
except serial.SerialException:
    ser = None  # Arduino not connected

# Function to send commands to the Arduino, checking for Arduino connection
def send_command_to_arduino(command):
    if ser:
        ser.write(command.encode())
        print(f"Sent command {command} to Arduino")
    else:
        print("Arduino not connected")

# Function to send the "WAITING" command to the Arduino
def send_waiting_command():
    send_command_to_arduino("WAITING")
    print("Script is running...")


# Function to start a pump motor
def start_pump(motor_pin, volume):
    run_time = volume / flow_rate  # run time based on volume
    GPIO.output(motor_pin, GPIO.LOW)  # Turn on the motor
    start_time = time.time()  # Record the start time

    # Check if the pump operation is still running
    while (time.time() - start_time) < run_time:
        pass

    end_time = time.time()  # Record the end time
    GPIO.output(motor_pin, GPIO.HIGH)  # Turn off the motor
    elapsed_time = end_time - start_time
    pump_start_times[motor_pin] = start_time  # Record the start time
    pump_end_times[motor_pin] = end_time  # Record the end time
    print(f"Pumping {volume} mL from Motor {relay_pins.index(motor_pin) + 1}. Time: {int(elapsed_time // 60)} minutes {int(elapsed_time % 60)} seconds")

# Function to start all motors simultaneously
def start_all_motors(volume):
    global cocktail_start_time
    cocktail_start_time = time.time()  # Record the cocktail start time

    # Sending the corresponding cocktail command to Arduino for LED strip control
    # send_command_to_arduino("ALLMOTORS")

    threads = []

    for motor_pin in relay_pins:
        thread = threading.Thread(target=start_pump, args=(motor_pin, volume))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    end_time = time.time()  # Record the end time for the last motor

    print(f"Pumping {volume} mL from All Motors")
    total_time = end_time - cocktail_start_time
    print(f"Total time: {int(total_time // 60)} minutes {int(total_time % 60)} seconds")

    # Sending the completion command to Arduino for LED strip control
    send_command_to_arduino("COMPLETE")


# Function to load cocktail image
def load_cocktail_image(cocktail):
    local_img_path = recipes[cocktail]['imgpath']
    if os.path.exists(local_img_path):
        try:
            image = Image.open(local_img_path)
            image = image.resize((170, 170), Image.BILINEAR)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image for {cocktail} from local imgpath: {e}")
    else:
        # Load the image from "image_url"
        response = requests.get(recipes[cocktail]['image_url'])
        try:
            image = Image.open(BytesIO(response.content))
            image = image.resize((170, 170), Image.BILINEAR)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image for {cocktail} from image_url: {e}")
    # Return None if image loading fails
    return None

# Function to display cocktail details
def show_cocktail_details(cocktail):
    selected_cocktail.set(cocktail)
    cocktail_data = recipes[cocktail]

    details_label.config(text=f"Selected Cocktail\n{cocktail}")
    ingredients_label.config(text="\n".join([f"{ingredient['name']}: {ingredient['quantity']} mL" for ingredient in cocktail_data['ingredients']]))

    order_button.config(state=tk.NORMAL)

# Function to make a cocktail
def make_cocktail(cocktail):
    global cocktail_start_time, pump_running
    cocktail_start_time = time.time()  # Record the cocktail start time
    pump_running = True  # Start the pump operation

    # Sending the corresponding cocktail command to Arduino for LED strip control
    if cocktail == "AMF":
        send_command_to_arduino("ADIOS")
    elif cocktail == "Long Island Ice Tea":
        send_command_to_arduino("LONGISLAND")
    elif cocktail == "Peach Crush":
        send_command_to_arduino("PEACHCRUSH")
    elif cocktail == "Midori Sour":
        send_command_to_arduino("MIDORISOUR")

    print(f"Preparing 1 {cocktail}...")

    # Getting the ingredient motors and volumes for the selected cocktail
    ingredients = recipes[cocktail]['ingredients']

    # Calculate the estimated pump run times based on ingredient volumes
    run_times = [(motor_mapping[ingredient['motor']], ingredient['quantity']) for ingredient in ingredients]

    # Sort the run_times in ascending order of volume
    run_times.sort(key=lambda x: x[1])

    # Create a list to store threads
    threads = []

    # Turn on all required motors using threads
    for motor_pin, volume in run_times:
        thread = threading.Thread(target=start_pump, args=(motor_pin, volume))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    end_time = time.time()  # Record the end time for the last motor

    print("Cocktail ready!")

    # Sending the completion command to Arduino for LED strip control
    send_command_to_arduino("COMPLETE")

    pump_running = False  # Stop the pump operation

# Function to stop the cocktail making process
def stop_pumps():
    global pump_running
    GPIO.output(relay_pins, GPIO.HIGH)  # Turn off the motor
    #send_command_to_arduino("WAITING")
    pump_running = False

# Create the main tkinter window
root = tk.Tk()
root.title("Cocktail Bartender Robot")

# Create a tkinter style for the buttons
style = ttk.Style()
style.configure("Large.TButton", font=("Helvetica", 20), width=11)

# Create frames
btn_frame = ttk.Frame(root, padding=10)
btn_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

order_frame = ttk.Frame(root, padding=10)
order_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

custom_frame = ttk.Frame(root, padding=10)
#custom_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
custom_frame.grid(row=1, column=0, padx=10, pady=2, sticky="nsew")

# Create vertical dotted line separator
separator = ttk.Separator(root, orient="vertical")
separator.grid(row=0, column=1, rowspan=2, sticky="ns")

# Create horizontal dotted line separator
separator2 = ttk.Separator(btn_frame, orient="horizontal")
separator2.grid(row=2, column=0, columnspan=2, sticky="ew")

# Create horizontal dotted line separator
#separator3 = ttk.Separator(root, orient="horizontal")
#separator3.grid(row=1, column=0, columnspan=3, sticky="ew")

# Initialize variables
selected_cocktail = tk.StringVar()
selected_cocktail.set("")

# Dropdown menu to select the ingredient motor
selected_motor = tk.StringVar()
ingredient_motor_dropdown = ttk.Combobox(custom_frame, textvariable=selected_motor)
motor_options = [f"Motor {i+1}" for i in range(len(relay_pins))] + ["All Motors"]
ingredient_motor_dropdown['values'] = motor_options
ingredient_motor_dropdown.grid(row=0, column=0, padx=10)
ingredient_motor_dropdown.set("All Motors")  # Set default value to 'All Motors'

# Create a combo box for selecting the volume
volume_entry = tk.StringVar()
volume_dropdown = ttk.Combobox(custom_frame, textvariable=volume_entry)
volume_options = [5, 10, 15, 25, 30, 45, 60, 80]
volume_dropdown['values'] = volume_options
volume_dropdown.grid(row=0, column=1, padx=10)
volume_dropdown.set(25)  # Set default value to 25mL

# Start button to activate the selected motor(s)
start_button = ttk.Button(custom_frame, text="Start", command=lambda: start_all_motors(int(volume_entry.get())) if selected_motor.get() == "All Motors" else start_pump(motor_mapping[int(selected_motor.get().split()[-1])], int(volume_entry.get())),style="Large.TButton")
start_button.grid(row=1, column=0, columnspan=2, padx=10, pady =5)

# Create buttons for LED control and pump stopping at the bottom of the order_frame
LED_waiting_button = ttk.Button(order_frame, text="LED Waiting", command=lambda: send_command_to_arduino("WAITING"),style="Large.TButton")
LED_waiting_button.grid(row=8, column=0, padx=10, pady=10)

LED_off_button = ttk.Button(order_frame, text="LED Off", command=lambda: send_command_to_arduino("FINISHED"),style="Large.TButton")
LED_off_button.grid(row=8, column=1, padx=10, pady=10)

pump_stop_button = ttk.Button(order_frame, text="STOP PUMPS", command=stop_pumps)
#pump_stop_button = ttk.Button(order_frame, text="STOP PUMPS", command=stop_pumps,style="Large.TButton")
pump_stop_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

# Initialize labels
details_label = ttk.Label(order_frame, text="Selected Cocktail", font=("Helvetica", 14, "bold"))
details_label.grid(row=0, column=0, columnspan=2, pady=10)

ingredients_label = ttk.Label(order_frame, text="", font=("Helvetica", 12))
ingredients_label.grid(row=1, column=0, columnspan=2, pady=10)

order_button = ttk.Button(order_frame, text="Click to order", command=lambda: make_cocktail(selected_cocktail.get()), state=tk.DISABLED,style="Large.TButton")
order_button.grid(row=2, column=0, columnspan=2, pady=10)

# Load cocktail images and create buttons
cocktail_buttons = []
for i, cocktail in enumerate(recipes):
    image = load_cocktail_image(cocktail)
    if image:
        cocktail_button = ttk.Button(btn_frame, image=image, text=cocktail, compound=tk.TOP, command=lambda c=cocktail: show_cocktail_details(c))
        cocktail_button.image = image  # Store the PhotoImage object
        cocktail_button.grid(row=i // 2, column=i % 2, padx=10, pady=10)
        cocktail_buttons.append(cocktail_button)
        

# Send the "WAITING" command when the program starts
send_waiting_command()
#print("Script is running...")

# Start the tkinter main loop
root.mainloop()

# Cleanup GPIO
GPIO.cleanup()
