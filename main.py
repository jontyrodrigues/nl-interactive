import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress
from functions import calculate_statistics, calculate_adj_r_square, bruteforce_fit
import base64
import io
import webbrowser
import re
from tkinter import Tk, Button, Label, Entry, Frame, messagebox, filedialog

# Function to fit the model to data and update the plot
def fit_model():
    # Create a figure and plot
    fig = plt.figure(dpi=150)
    ax = fig.add_subplot(111)
    line, = ax.plot([], [], 'r-', label='Fitted Curve')
    scatter, = ax.plot([], [], 'bo', label='Data Points')
    ax.set_xlabel(xlabel=x_axis_label.get())
    ax.set_ylabel(ylabel=y_axis_label.get())
    ax.legend()


    x = np.array([float(entry_x.get()) for entry_x in entries_x])
    y = np.array([float(entry_y.get()) for entry_y in entries_y])

    param_names = [entry_param_name.get() for entry_param_name in entries_param_name]
    params = [float(entry_param_value.get()) for entry_param_value in entries_param_value]

    try:
        # Get the formula entered by the user
        formula = entry_formula.get()

        # Create a string that can be evaluated by Python
        string = "nonlinear_model = lambda x, {}: {}".format(", ".join(param_names), formula)
        exec(string,globals())
    except Exception as e:
        messagebox.showerror("Error", "Invalid formula or parameter names: {}".format(str(e)))
        return

    try:
        # Perform curve fitting
        params, _ = curve_fit(nonlinear_model, x, y, p0=params)
    except Exception as e:
        messagebox.showerror("Error", "Curve fitting failed: {}".format(str(e)))
        return

    # Calculate R-squared
    y_fit = nonlinear_model(x, *params)
    r_squared = calculate_statistics(y, y_fit)["r_squared"]
    std_err = calculate_statistics(y, y_fit)["std_err"]

    # Calculate adjusted R-squared
    n = len(x)
    k = len(params)
    adj_r_squared = calculate_adj_r_square(r_squared, n, k)

    # Calculate p-value
    slope, _, r_value, p_value, _ = linregress(y, y_fit)

    # Update the plot with fitted curve and points
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = nonlinear_model(x_fit, *params)
    line.set_data(x_fit, y_fit)

    scatter.set_data(x, y)

    # Update R-squared and p-value labels
    label_r_squared.config(text="R-squared: {:.4f}".format(r_squared))
    label_p_value.config(text="p-value: {:.4f}".format(p_value))
    label_adjusted_r_squared.config(text="Adjusted R-squared: {:.4f}".format(adj_r_squared))
    label_std_err.config(text="Standard Error: {:.4f}".format(std_err))

    # Update predicted parameter values label
    param_values = ", ".join("{:.4f}".format(value) for value in params)
    label_params.config(text="Predicted Parameter Values: {}".format(param_values))

    # Update the predicted parameter values in the entries
    for entry_param_value, param_value in zip(entries_param_value, params):
        entry_param_value.delete(0, "end")
        entry_param_value.insert(0, param_value)
    
    # Display the plot
    plt.ion()
    plt.show()
    # Redraw the plot
    ax.relim()
    ax.autoscale_view()
    plt.draw()

def bruteforce_params():
    param_names = [entry_param_name.get() for entry_param_name in entries_param_name]
    params = [float(entry_param_value.get()) for entry_param_value in entries_param_value]
    x = np.array([float(entry_x.get()) for entry_x in entries_x])
    y = np.array([float(entry_y.get()) for entry_y in entries_y])
    try:
        # Get the formula entered by the user
        formula = entry_formula.get()
        # Create a string that can be evaluated by Python
        string = "nonlinear_model = lambda x, {}: {}".format(", ".join(param_names), formula)
        exec(string,globals())
    except Exception as e:
        messagebox.showerror("Error", "Invalid formula or parameter names: {}".format(str(e)))
        return

    try:
        # Perform curve fitting
        params, _ = curve_fit(nonlinear_model, x, y, p0=params)
    except Exception as e:
        messagebox.showerror("Error", "Curve fitting failed: {}".format(str(e)))
        return
    tup = bruteforce_fit(nonlinear_model,x,y,params)
    # Update the predicted parameter values label and entries
    param_values = ", ".join("{:.4f}".format(value) for value in tup[1])
    label_params.config(text="Predicted Parameter Values: {}".format(param_values))
    for entry_param_value, param_value in zip(entries_param_value, tup[1]):
        entry_param_value.delete(0, "end")
        entry_param_value.insert(0, param_value)
    # Now perform the fit with the new parameters
    fit_model()


# Function to generate a report of the model, including the formula, R-squared, p-value, and predicted parameter values
# It generates an HTML file and opens it in the default web browser
def generate_report():
    # Check if there is already a plot
    if len(plt.get_fignums()) == 0:
        fit_model()

    # Make a variable with the name of each parameter and it's value in the format of "name = value"
    param_names = [entry_param_name.get() for entry_param_name in entries_param_name]
    params = [float(entry_param_value.get()) for entry_param_value in entries_param_value]
    param_values = ", ".join("{} = {:.4f}".format(name, value) for name, value in zip(param_names, params))

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    formula = entry_formula.get()
    formula = formula.replace("^", "**")
    if x_axis_label.get() != "":
        # Check the occourance of x in the formula, where it is not a part of another variable name
        # For example, if the formula is "a*x + b", then it should be replaced with "a*<x-axis-label> + b"
        # But if the formula is "ax + b", then it should not be replaced
        # So, we check if the character before and after x is a letter or not
        # If it is a letter, then it is a part of another variable name, so it should not be replaced
        # If it is not a letter, then it is not a part of another variable name, so it should be replaced
        formula = re.sub(r"(?<![a-zA-Z])x(?![a-zA-Z])", x_axis_label.get(), formula)
    
    # Create the HTML report
    report = f"""
    <html>
        <head>
        <style>
            table, th, td {{
            border: 1px solid black;
            border-collapse: collapse;
            }}
            th, td {{
            padding: 15px;
            }}
        </style>
            <title>Model Report</title>
        </head>
        <body>
            <h1>Model Report</h1>
            <img src="data:image/png;base64,{image_base64}" />
            <table>
                <tr>
                    <th>Formula</th>
                    <td>{formula}</td>
                </tr>
                <tr>
                    <th>R-squared</th>
                    <td>{label_r_squared["text"].split(" ")[1]}</td>
                </tr>
                <tr>
                    <th>Adjusted R-squared</th>
                    <td>{label_adjusted_r_squared["text"].split(" ")[2]}</td>
                </tr>
                <tr>
                    <th>p-value</th>
                    <td>{label_p_value["text"].split(" ")[1]}</td>
                </tr>
                <tr>
                    <th>Standard Error</th>
                    <td>{label_std_err["text"].split(" ")[2]}</td>
                </tr>
                <tr>
                    <th>Predicted Parameter Values</th>
                    <td>{param_values}</td>
                </tr>
            </table>
        </body>
    </html>
    """

    # Write the report to a file
    with open("report.html", "w") as file:
        file.write(report)

    # Open the report in the default web browser
    webbrowser.open("report.html")




# Function to add data points from a file
def add_data_points_from_file():
    # Make an "Open" window appear and store the chosen file path as a string
    file_path = filedialog.askopenfilename()

    # If the user chose a file
    if file_path:
        # Clear the current data points
        clear_data_points()
        # Open the file in read mode
        with open(file_path, "r", encoding="UTF-8") as file:
            # Read the file contents and split them by newline
            lines = file.read().split("\n")

            # If the first line contains anything other than a number, or dot then it is the header
            if not re.match(r"^\d+\.?\d*$", lines[0].split(",")[0]) or not re.match(r"^\d+\.?\d*$", lines[0].split(",")[1]):
                # Add the x and y axis labels
                x_axis_label.insert(0, lines[0].split(",")[0])
                y_axis_label.insert(0, lines[0].split(",")[1])
                # then remove the header from the list of lines
                lines.pop(0)

            # Add a data point for each line
            for line in lines:
                # Split the line by comma
                x, y = line.split(",")

                # Add a data point
                add_data_point()

                # Set the x and y values of the last data point
                entries_x[-1].insert(0, x)
                entries_y[-1].insert(0, y)

# Function to save data points to a file
def save_data_points_to_file():
    # Make a "Save" window appear and store the chosen file path as a string
    file_path = filedialog.asksaveasfilename()

    # If the user chose a file
    if file_path:
        # Open the file in write mode
        with open(file_path, "w",encoding="UTF-8") as file:
            # Write each data point to the file
            for point in points:
                file.write("{},{}\n".format(point[0].get(), point[1].get()))



# function to clear the current data points
def clear_data_points():
    # Remove the x-label and y-labels
    x_axis_label.delete(0,"end")
    y_axis_label.delete(0,"end")
    # Remove all data points from the list
    for point in points:
        point[0].destroy()
        point[1].destroy()

    # Remove all data points from the list
    points.clear()
    entries_x.clear()
    entries_y.clear()

# Function to save the model to a file, so that it can be loaded later, without having to re-enter the formula
# If the user has not entered a formula, an error message will be displayed
def save_model():
    # If the user has not entered a formula
    if not entry_formula.get():
        messagebox.showerror("Error", "Please enter a formula first")
        return

    # Make a "Save" window appear and store the chosen file path as a string
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")],initialfile="model.txt",initialdir="../models")

    # If the user chose a file
    if file_path:
        # Open the file in write mode
        with open(file_path, "w", encoding="UTF-8") as file:
            # Write the formula to the file
            file.write("{}\n".format(entry_formula.get()))

            # Write the parameter names and values to the file
            for param_name, param_value in zip(entries_param_name, entries_param_value):
                file.write("{},{}\n".format(param_name.get(), param_value.get()))

# Function to load a model from a file
def load_model():
    # Make an "Open" window appear and store the chosen file path as a string
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")],initialdir="../models")

    # If the user chose a file
    if file_path:
        # Clear the current parameter points
        clear_param_points()

        # Open the file in read mode
        with open(file_path, "r", encoding="UTF-8") as file:
            # Read the file contents and split them by newline
            lines = file.read().split("\n")

            # Set the formula
            # Get the length of the formula
            formula_length = len(entry_formula.get())
            entry_formula.delete(0, formula_length)
            entry_formula.insert(0, lines[0])

            # Add a parameter point for each line
            for line in lines[1:]:
                # Split the line by comma
                param_name, param_value = line.split(",")

                # Add a parameter point
                add_param_point()

                # Set the name and value of the last parameter point
                entries_param_name[-1].insert(0, param_name)
                entries_param_value[-1].insert(0, param_value)

# Function to clear the current parameter points
def clear_param_points():
    labels_param_name.pop().destroy()
    entries_param_name.pop().destroy()
    labels_param_value.pop().destroy()
    entries_param_value.pop().destroy()
    # Remove all parameter points from the list
    for param_point in entries_param_value:
        labels_param_name.pop().destroy()
        entries_param_name.pop().destroy()
        labels_param_value.pop().destroy()
        entries_param_value.pop().destroy()

# Function to add a new data point
def add_data_point():
    entry_x = Entry(frame)
    entry_x.grid(row=len(points) + 4, column=1, padx=5, pady=5)

    entry_y = Entry(frame)
    entry_y.grid(row=len(points) + 4, column=2, padx=5, pady=5)

    entries_x.append(entry_x)
    entries_y.append(entry_y)

    points.append((entry_x, entry_y))


# Function to remove the last data point
def remove_data_point():
    if len(points) > 2:
        last_point = points.pop()
        last_point[0].destroy()
        last_point[1].destroy()

        entries_x.remove(last_point[0])
        entries_y.remove(last_point[1])

def add_param_point():
    i = len(labels_param_name)
    label_param_name = Label(root, text="Parameter Name {}".format(i + 1))
    label_param_name.grid(row=i + 2, column=3, padx=5, pady=5, sticky="E")
    entry_param_name = Entry(root)
    entry_param_name.grid(row=i + 2, column=4, padx=5, pady=5)
    labels_param_name.append(label_param_name)
    entries_param_name.append(entry_param_name)

    label_param_value = Label(root, text="Parameter Value {}".format(i + 1))
    label_param_value.grid(row=i + 2, column=5, padx=5, pady=5, sticky="E")
    entry_param_value = Entry(root)
    entry_param_value.grid(row=i + 2, column=6, padx=5, pady=5)
    labels_param_value.append(label_param_value)
    entries_param_value.append(entry_param_value)

    

def remove_param_point():
    if len(labels_param_name) > 1:
        labels_param_name.pop().destroy()
        entries_param_name.pop().destroy()
        labels_param_value.pop().destroy()
        entries_param_value.pop().destroy()

# Create a GUI window
root = Tk()
root.title("Nonlinear Model Fitting")
root.resizable(False, False)

# Create a frame for the data points
frame = Frame(root)
frame.grid(row=0, columnspan=3)

# Create a label and entry box for the the x-axis label and the y-axis label of the graph
label_x = Label(frame, text="X-Axis Label")
label_x.grid(row=1, column=1, padx=5, pady=5)
x_axis_label = Entry(frame)
x_axis_label.grid(row=2, column=1, padx=5, pady=5)

label_y = Label(frame, text="Y-Axis Label")
label_y.grid(row=1, column=2, padx=5, pady=5)
y_axis_label = Entry(frame)
y_axis_label.grid(row=2, column=2, padx=5, pady=5)

# Create a label for the x and y data points
label_data_points = Label(frame, text="X Data")
label_data_points.grid(row=3, column=1, padx=5, pady=5)
label_data_points = Label(frame, text="Y Data")
label_data_points.grid(row=3, column=2, padx=5, pady=5)


# Create labels and entry boxes for the initial two data points
labels_x = []
entries_x = []
labels_y = []
entries_y = []
points = []
for i in range(3,5):
    entry_x = Entry(frame)
    entry_y = Entry(frame)

    entry_x.grid(row=i + 1, column=1, padx=5, pady=5)
    entry_y.grid(row=i + 1, column=2, padx=5, pady=5)

    entries_x.append(entry_x)
    entries_y.append(entry_y)

    points.append((entry_x, entry_y))

# Create buttons for adding and removing data points
add_button = Button(root, text="Add Data Point", command=add_data_point)
add_button.grid(row=1, column=0, padx=5, pady=10)

remove_button = Button(root, text="Remove Last Point", command=remove_data_point)
remove_button.grid(row=1, column=1, padx=5, pady=10)

add_button_param = Button(root, text="Add Params", command=add_param_point)
add_button_param.grid(row=2, column=0, padx=5, pady=10)

remove_button_param = Button(root, text="Remove Param", command=remove_param_point)
remove_button_param.grid(row=2, column=1, padx=5, pady=10)

# Create labels and entry boxes for the parameters
labels_param_name = []
entries_param_name = []
labels_param_value = []
entries_param_value = []
params = []
for i in range(2):
    label_param_name = Label(root, text="Parameter Name {}".format(i + 1))
    label_param_name.grid(row=i + 2, column=3, padx=5, pady=5, sticky="E")
    entry_param_name = Entry(root)
    entry_param_name.grid(row=i + 2, column=4, padx=5, pady=5)
    labels_param_name.append(label_param_name)
    entries_param_name.append(entry_param_name)

    label_param_value = Label(root, text="Parameter Value {}".format(i + 1))
    label_param_value.grid(row=i + 2, column=5, padx=5, pady=5, sticky="E")
    entry_param_value = Entry(root)
    entry_param_value.grid(row=i + 2, column=6, padx=5, pady=5)
    labels_param_value.append(label_param_value)
    entries_param_value.append(entry_param_value)

# Create a label and entry box for the formula
label_formula = Label(root, text="Formula: ")
label_formula.grid(row=1, column=3, padx=5, pady=10, sticky="E")

entry_formula = Entry(root)
entry_formula.grid(row=1, column=4, padx=5, pady=10)

# Create a button to save the formula and parameters into a file
save_model_button = Button(root, text="Save Model", command=save_model)
save_model_button.grid(row=1, column=5, padx=5, pady=10)

load_model_button = Button(root, text="Load Model", command=load_model)
load_model_button.grid(row=1, column=6, padx=5, pady=10)


# Create a button to fit the model
fit_button = Button(root, text="Fit Model", command=fit_model)
fit_button.grid(row=2, column=2, padx=5, pady=10)

# Create a button to load the data from a csv file
load_button = Button(root, text="Load Data", command=add_data_points_from_file)
load_button.grid(row=1, column=2, padx=5, pady=10)

# Create a button to save the data to a csv file
save_button = Button(root, text="Save Data", command=save_data_points_to_file)
save_button.grid(row=3, column=1, padx=5, pady=10)

# Create a button to generate a report of the data
report_button = Button(root, text="Generate Report", command=generate_report)
report_button.grid(row=3, column=0, padx=5, pady=10)

# Create a button to brute force the model
brute_force_button = Button(root, text="Brute Force Params", command=bruteforce_params)
brute_force_button.grid(row=3, column=2, padx=5, pady=10)

# Create labels for R-squared, p-value, and predicted parameter values
label_r_squared = Label(root, text="R-squared: ")
label_r_squared.grid(row=4, column=0, padx=5, pady=10)

label_p_value = Label(root, text="p-value: ")
label_p_value.grid(row=4, column=1, padx=5, pady=10)

label_adjusted_r_squared = Label(root, text="Adjusted R-squared: ")
label_adjusted_r_squared.grid(row=4, column=2, padx=5, pady=10)

label_std_err = Label(root, text="Standard Error: ")
label_std_err.grid(row=4, column=3, padx=5, pady=10)

label_params = Label(root, text="Predicted Parameter Values: ")
label_params.grid(row=5, column=0, columnspan=3, padx=5, pady=10)


# Start the GUI event loop
root.mainloop()