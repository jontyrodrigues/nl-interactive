import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress

# Function to calculate R-squared
def calculate_statistics(y, y_fit):
    # y_mean = np.mean(y)
    # ss_total = np.sum((y - y_mean) ** 2)
    # ss_residual = np.sum((y - y_fit) ** 2)
    # r_squared = 1 - (ss_residual / ss_total)
    # return r_squared
    slope, intercept, r_value, p_value, std_err = linregress(y, y_fit)
    return {
        'r_squared': r_value ** 2,
        'slope': slope,
        'intercept': intercept,
        'p_value': p_value,
        'std_err': std_err
    }

def calculate_adj_r_square(r_square, n, k):
    adj_r_square = 1 - (1 - r_square) * ((n - 1) / (n - k - 1))
    return adj_r_square


# Bruteforce function to find the best fit, it takes a lot of time
# but the gist is that it takes a list of initial parameters and
# then tries to fit the curve with each of the parameters and then
# returns the best fit
def bruteforce_fit(func, x, y, initial_parameters):
    best_fit = None
    best_fit_parameters = None
    best_fit_statistics = None
    bruteforce_params = [0.1, -0.1,100,1,1e6,-0.1e3,0.1e3,0.1e6,-0.1e6]
    for index, initial_parameter in enumerate(initial_parameters):
        # get the index number of the parameter
        try:
            for bruteforce_param in bruteforce_params:
                initial_parameters[index] = bruteforce_param
                popt, pcov = curve_fit(func, x, y, initial_parameters)
                y_fit = func(x, *popt)
                statistics = calculate_statistics(y, y_fit)
                if best_fit is None or statistics['r_squared'] > best_fit_statistics['r_squared']:
                    best_fit = y_fit
                    best_fit_parameters = popt
                    best_fit_statistics = statistics
        except:
            pass
    return best_fit, best_fit_parameters, best_fit_statistics