## NL Interactive

A simple GUI interface for doing non-linear curve fitting.  This is a work in progress.

### Background

Well I am doing my PhD and i need to fit a lot of data, i have a lot of software and even excel but I find it to be slow especially if i need to check a lot of different models. So i decided to make a simple GUI interface for doing non-linear curve fitting. I am using the scipy curve_fit function to do the fitting. I am using tkinter for the GUI, and matplotlib for the plotting.

Well mostly it is written by ChatGPT, the frontend part and the curve fitting part is written by me.

### Installation

```
pip install numpy scipy matplotlib tkinter
```

### Usage

```
python nl_interactive.py
```

Once the GUI is open, you can add your data points in the first two columns, the first column is for the x values and the second is for the y. By default only two rows are added click add data points to add more rows, if you need to remove then click remove.

Once you have added your data points, type the function you want to fit in the model. Add your parameters in the parameters box, and the parameter name and the parameter value in the first and second columns respectively. If you need to add more parameters click add parameters, and if you need to remove then click remove.

Make sure that the parameter names in the model and the parameter names in the parameters box match. If you need to change the parameter names in the model, then change the parameter names in the parameters box to match.

Once you have added your model and parameters, click fit data. The fit will be displayed in the plot. If you need to change the model or parameters, then change them and click fit data again.

### Example

Say you have the a langmuir isotherm and you want to fit it to some data. The langmuir isotherm is given by:

    Qe = Qm * K * Ce / (1 + K * Ce)

Where Qe is the equilibrium adsorption capacity, Qm is the maximum adsorption capacity, K is the adsorption constant, and Ce is the equilibrium concentration.

Then type Qm and K in the parameters box, and the model in the model box:

    Qm * K * x / (1 + K * x)

Then click fit data. The fit will be displayed in the plot.

Remember that you independent variable always needs to be x in the model.

