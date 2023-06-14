import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress
from tkinter import Tk, Button, Label, Entry, Frame, messagebox, filedialog


# Function to calculate R-squared
def calculate_r_squared(y, y_fit):
    y_mean = np.mean(y)
    ss_total = np.sum((y - y_mean) ** 2)
    ss_residual = np.sum((y - y_fit) ** 2)
    r_squared = 1 - (ss_residual / ss_total)
    return r_squared

# Function to fit the model to data and update the plot
def fit_model():
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
    r_squared = calculate_r_squared(y, y_fit)

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

    # Update predicted parameter values label
    param_values = ", ".join("{:.4f}".format(value) for value in params)
    label_params.config(text="Predicted Parameter Values: {}".format(param_values))

    # Update the predicted parameter values in the entries
    for entry_param_value, param_value in zip(entries_param_value, params):
        entry_param_value.delete(0, "end")
        entry_param_value.insert(0, param_value)
    

    # Redraw the plot
    ax.relim()
    ax.autoscale_view()
    plt.draw()


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
    entry_x.grid(row=len(points) + 1, column=1, padx=5, pady=5)

    entry_y = Entry(frame)
    entry_y.grid(row=len(points) + 1, column=2, padx=5, pady=5)

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

# Create labels and entry boxes for the initial two data points
labels_x = []
entries_x = []
labels_y = []
entries_y = []
points = []
for i in range(2):
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

# Create labels for R-squared, p-value, and predicted parameter values
label_r_squared = Label(root, text="R-squared: ")
label_r_squared.grid(row=3, column=0, padx=5, pady=10)

label_p_value = Label(root, text="p-value: ")
label_p_value.grid(row=3, column=1, padx=5, pady=10)

label_params = Label(root, text="Predicted Parameter Values: ")
label_params.grid(row=4, column=0, columnspan=3, padx=5, pady=10)

# Create a figure and plot
fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot([], [], 'r-', label='Fitted Curve')
scatter, = ax.plot([], [], 'bo', label='Data Points')
ax.legend()

# Display the plot
plt.ion()
plt.show()

# Start the GUI event loop
root.mainloop()
