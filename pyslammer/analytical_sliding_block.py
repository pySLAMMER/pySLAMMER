"""
analytical_sliding_block.py

This module contains the implementation of the analytical model for a sliding block.
It defines the necessary symbols and parameters for the model, and sets up the global variables.

The module imports the necessary libraries, including numpy, sympy, pandas, and matplotlib.

Functions:
    set_globals(): Sets the global variables for the model.
    show_solution_approach(): Displays the definitions of the input acceleration, velocity, and displacement.
    create_harmonic_input_files(freq, resolution, cycles=10): Creates input files for a harmonic motion with a given frequency, resolution, and number of cycles.
    find_harmonic_solution(freq_val, ky_val, grav = 9.81, plot=True): Finds the solution for a harmonic motion with a given frequency and stiffness, optionally plots the solution.
    find_t1(a_in, ky, vals): Finds the time at which the input acceleration equals the stiffness.
    find_t2(v_in, vb, vals, freq_val): Finds the time at which the input velocity equals the block velocity.
    find_displacement(v_in, vb, t1, t2, vals): Finds the displacement of the block.
    apply_find_harmonic_solution(row, plot = False): Applies the find_harmonic_solution function to a row of data.
    harmonic_solutions(harmonic_combinations, save=False, plot=False): Finds the solutions for a set of harmonic combinations, optionally saves the solutions to a file.
    harmonic_solution_plot(a_in, v_in, vb, displacement,time,t1_def_val,t2_val, ky, vals, save=False): Plots the solution for a harmonic motion.

Global variables:
    time, freq, g, ky: Symbols for the analytical solution.
    a_in, v_inmax, v_in, x_in: Function expressions for the model.

Usage:
    Import this module to use the analytical model for a sliding block.
    Call set_globals() to set the global variables.
"""

# import pickle as pkl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sym

sym.init_printing()

# for analytical model
frequencies = np.array([0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
yield_accelerations = np.array([0.1, 0.2, 0.4, 0.6, 0.8, 1.0])
combinations = np.array(np.meshgrid(frequencies, yield_accelerations)).T.reshape(-1, 2)

# for numerical models
sample_resolution = np.array([50, 100, 200, 250, 500, 750, 1000])  # samples per second


def set_globals():
    """
    Set global variables and defines symbols for the analytical solution.

    This function sets the values of global variables `time`, `freq`, `g`, `ky`,
    and defines symbols for the analytical solution.
    It also defines the function expressions for `a_in`, `v_inmax`, `v_in`, and `x_in`.

    Parameters:
        None

    Returns:
        None
    """
    global time, freq, g, ky, a_in, v_inmax, v_in, x_in
    # Define symbols for analytical solution
    # Define parameters
    time, freq, g, ky = sym.symbols("t, f, g, ky", real=True, positive=True)
    # time, freq, g, ky, t1, t2 = sym.symbols('t, f, g, ky, t_1, t_2', real=True, positive=True)
    # display(time, freq, g, ky, t1, t2)

    # Define the function expressions
    a_in = sym.sin(freq * 2 * sym.pi * time)
    v_inmax = g / 2 / sym.pi / freq
    v_in = g * sym.integrate(a_in, time) + v_inmax
    x_in = sym.integrate(v_in, time)


set_globals()


def show_solution_approach():
    """
    Display the solution approach for the sliding block problem.

    This function displays the equations defining the input acceleration, velocity, and displacement
    for the sliding block problem.

    Returns:
        None
    """
    print("The input acceleration (in units of g) is defined by:")
    print(sym.Eq(sym.symbols("\ddot{x_resp}_{in}(t)/g"), a_in))
    print("The input velocity (in m/block_disp) is defined by:")
    print(sym.Eq(sym.symbols("\dot{x_resp}_{in}(t)"), v_in))
    print("The input displacement (in m) is defined by:")
    print(sym.Eq(sym.symbols("u_{in}(t)"), x_in))
    return None


def create_harmonic_input_files(freq, resolution, cycles=10):
    """
    Create harmonic input files.

    Parameters:
    - freq (float): The frequency of the sine wave in Hz.
    - resolution (float): The resolution of the time series in samples per second.
    - cycles (int): The number of cycles of the sine wave.

    Returns:
    None
    """
    duration = cycles / freq
    t = np.linspace(0, duration, int(duration * resolution * cycles))
    a = np.sin(np.pi * 2 * freq * t)
    data = np.column_stack((t, a))
    np.savetxt(
        f"sample_ground_motions/sine_{freq}_Hz_{resolution * freq}_sps.csv",
        data,
        delimiter=",",
        header=f"# Time Series: {freq} Hz sine wave \n # Time (block_disp),Acceleration (g)",
    )
    return None


def find_harmonic_solution(freq_val, ky_val, grav=9.81, plot=True):
    """
    Finds the harmonic solution for a sliding block system.

    Parameters:
        freq_val (float): The frequency value.
        ky_val (float): The ky value.
        grav (float, optional): The gravitational constant. Defaults to 9.81.
        plot (bool, optional): Whether to plot the harmonic solution. Defaults to True.

    Returns:
        float: The total displacement of the block.
    """
    vals = [(g, grav), (ky, ky_val), (freq, freq_val)]

    t1 = find_t1(a_in, ky, vals)
    vb = g * ky * (time - t1) + v_in.subs(time, t1)
    t2 = find_t2(v_in, vb, vals, freq_val)

    dx_block = find_displacement(v_in, vb, t1, t2, vals)
    total_disp = float(dx_block.subs(time, t2).subs(vals))
    if plot:
        harmonic_solution_plot(a_in, v_in, vb, dx_block, time, t1, t2, ky, vals)
    return total_disp


def find_t1(a_in, ky, vals):
    """
    Find the value of t1 by solving the equation a_in - ky = 0.

    Parameters:
    a_in (symbolic expression): The input acceleration function.
    ky (float): The value of ky.
    vals (dict): A dictionary containing variable substitutions for the equation.

    Returns:
    float: The value of t1 after substituting the variable values.
    """
    t1 = sym.solve(a_in - ky, time)[1]
    return t1.subs(vals)


def find_t2(v_in, vb, vals, freq_val):
    """
    Find the value of t2 by solving the equation v_in - vb = 0.

    Parameters:
    v_in (symbolic expression): The input velocity function.
    vb (symbolic expressionn): The block velocity function.
    vals (dict): A dictionary containing variable substitutions for the equation.
    freq_val (float): The frequency value. This guides the solver to find the correct root.

    Returns:
    float: The value of t2, representing the time at which the input velocity equals the block velocity.
    """
    equation = sym.Eq(vb, v_in).subs(vals)
    t2 = sym.nsolve(equation, time, (0.25 / freq_val, 1 / freq_val), solver="bisect")
    return t2


def find_displacement(v_in, vb, t1, t2, vals):
    """
    Calculate the displacement of a sliding block over time.

    Parameters:
    v_in (symbolic expression): Velocity of the block before time t1.
    vb (symbolic expression): Velocity of the block during time t1 to t2.
    t1 (float): Start time of the block'block_disp sliding motion.
    t2 (float): End time of the block'block_disp sliding motion.
    vals (dict): Dictionary of values to substitute into the expressions.

    Returns:
    displacement (symbolic expression): Piecewise function representing the displacement of the block over time.
    """
    x_in = sym.integrate(v_in, time)
    x_block = (
        sym.integrate(vb, time)
        + x_in.subs(time, t1)
        - sym.integrate(vb, time).subs(time, t1)
    )
    total_displacement = x_in.subs(vals).subs(time, t2) - x_block.subs(vals).subs(
        time, t2
    )
    displacement = sym.Piecewise(
        (0, time < t1), (total_displacement, time > t2), (x_in - x_block, True)
    )
    return displacement


def apply_find_harmonic_solution(row, plot=False):
    """
    Apply the find_harmonic_solution function to a given row of data.

    Parameters:
    - row: A pandas DataFrame row containing the 'Frequency (Hz)' and 'ky (g)' values.
    - plot: A boolean indicating whether to plot the results.

    Returns:
    - The result of the find_harmonic_solution function.

    """
    return find_harmonic_solution(row["Frequency (Hz)"], row["ky (g)"], plot=plot)


def harmonic_solutions(harmonic_combinations, save=False, plot=False):
    """
    Calculate the harmonic solutions for given combinations of frequency and ky values.

    Args:
        harmonic_combinations (list): A list of tuples containing the frequency (Hz) and ky (g) values.
        save (bool, optional): Whether to save the harmonic solutions to a CSV file. Defaults to False.
        plot (bool, optional): Whether to plot the harmonic solutions. Defaults to False.

    Returns:
        pandas.DataFrame: A DataFrame containing the harmonic solutions with columns for frequency, ky, and displacement.
    """
    harmonic_solutions = pd.DataFrame(
        harmonic_combinations, columns=["Frequency (Hz)", "ky (g)"]
    )
    harmonic_solutions["Displacement (m)"] = harmonic_solutions.apply(
        lambda row: apply_find_harmonic_solution(row, plot=plot), axis=1
    )
    if save:
        harmonic_solutions.to_csv("common/harmonic_solutions.csv", index=False)
    return harmonic_solutions


def harmonic_solution_plot(
    a_in, v_in, vb, displacement, time, t1_def_val, t2_val, ky, vals, save=False
):
    """
    Plot the harmonic solution of a sliding block system.

    Parameters:
    a_in (sympy.Expr): The acceleration input.
    v_in (sympy.Expr): The velocity input.
    vb (sympy.Expr): The velocity during the block phase.
    displacement (sympy.Expr): The displacement of the block.
    time (sympy.Symbol): The time variable.
    t1_def_val (float): The value of time at which the block phase starts.
    t2_val (float): The value of time at which the block phase ends.
    ky (sympy.Symbol): The stiffness coefficient.
    vals (dict): A dictionary of symbol-value pairs used for substitution.
    save (bool, optional): Whether to save the plot as an image file. Defaults to False.

    Returns:
    None
    """

    ablock = sym.Piecewise((a_in, time < t1_def_val), (a_in, time > t2_val), (ky, True))
    aplot = sym.lambdify(time, a_in.subs(vals), "numpy")
    abplot = sym.lambdify(time, ablock.subs(vals), "numpy")
    vplot = sym.lambdify(time, v_in.subs(vals), "numpy")
    vbplot = sym.lambdify(time, vb.subs(vals), "numpy")

    displacementplot = sym.lambdify(time, displacement.subs(vals), "numpy")
    plt.close("all")
    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(5, 6))
    time_vals = np.linspace(0, 1 / vals[2][1], 1000)
    t1_index = np.argmin(np.abs(time_vals - t1_def_val))
    t2_index = np.argmin(np.abs(time_vals - t2_val))

    axs[0].plot(
        time_vals, ky.subs(vals) * np.ones(len(time_vals)), "k--", linewidth=0.5
    )
    axs[0].plot(time_vals, aplot(time_vals))
    axs[0].plot(time_vals, abplot(time_vals))
    axs[0].legend(["$k_y$", "Input", "Block"])
    axs[0].set_title("Acceleration, g")
    axs[0].set_ylabel("$\ddot x$")

    axs[1].plot(time_vals, vplot(time_vals))
    axs[1].plot(time_vals[0:t1_index], vplot(time_vals)[0:t1_index], "tab:orange")
    axs[1].plot(
        time_vals[t1_index:t2_index], vbplot(time_vals)[t1_index:t2_index], "tab:orange"
    )
    axs[1].plot(time_vals[t2_index:-1], vplot(time_vals)[t2_index:-1], "tab:orange")
    axs[1].fill_between(
        time_vals[t1_index:t2_index],
        vbplot(time_vals)[t1_index:t2_index],
        vplot(time_vals)[t1_index:t2_index],
        color="gray",
        alpha=0.5,
    )
    axs[1].set_title("Velocity, m/s")
    axs[1].set_ylabel("$\dot x$")

    tmax = max(time_vals)
    dmax = displacementplot(tmax)
    axs[2].plot(time_vals, time_vals * 0)
    axs[2].plot(time_vals, displacementplot(time_vals), "tab:orange")
    # axs[2].text(
    #     0.95,
    #     0.5,
    #     f"Total Displacement: {round(float(dmax), 3)} m",
    #     horizontalalignment="right",
    #     verticalalignment="center",
    #     transform=axs[2].transAxes,
    # )
    axs[2].set_title("Relative displacement, m")
    axs[2].set_xlabel("Time, s")
    axs[2].set_ylabel("$\Delta x$")

    # Set x-axis extents for all axes to 0 to 1
    axs[0].set_xlim(0, 1)
    axs[1].set_xlim(0, 1)
    axs[2].set_xlim(0, 1)

    # Remove x-axis tick marks from axes 0 and 1
    axs[0].tick_params(
        axis="x", which="both", bottom=False, top=False, labelbottom=False
    )
    axs[1].tick_params(
        axis="x", which="both", bottom=False, top=False, labelbottom=False
    )

    if save:
        plt.savefig(f"harmonic_solution_freq-{vals[2][1]}_ky-{vals[1][1]}.png")
    return None


class AnalyticalSlidingBlock:
    """
    Analytical solution for sliding block analysis.

    Parameters
    ----------
    ky : float
        Yield acceleration in g.
    ground_motion : GroundMotion
        Ground motion object containing acceleration time series.

    Attributes
    ----------
    ky : float
        Yield acceleration in g.
    ground_motion : GroundMotion
        Ground motion object.
    sliding_displacement : np.ndarray
        Sliding displacement time series.
    """

    def __init__(self, ky, ground_motion):
        self.ky = ky
        self.ground_motion = ground_motion
        self.sliding_displacement = None

    def compute_displacement(self):
        """
        Compute the sliding displacement using the analytical method.

        Returns
        -------
        None
        """
        pass


if __name__ == "__main__":
    from utilities import psfigstyle

    plt.style.use(psfigstyle)
    find_harmonic_solution(1, 0.6, grav=9.81, plot=True)
    plt.show()
