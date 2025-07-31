"""
This module provides utility functions for the laser-measles project.

Functions:
    calc_distances(latitudes: np.ndarray, longitudes: np.ndarray, verbose: bool = False) -> np.ndarray:
        Calculate the pairwise distances between points given their latitudes and longitudes.

    calc_capacity(population: np.uint32, nticks: np.uint32, cbr: np.float32, verbose: bool = False) -> np.uint32:
        Calculate the population capacity after a given number of ticks based on a constant birth rate.

    seed_infections_randomly(model, ninfections: int = 100) -> None:
        Seed initial infections in random locations at the start of the simulation.

    seed_infections_in_patch(model, ipatch: int, ninfections: int = 100) -> None:
        Seed initial infections in a specific location at the start of the simulation.

    cast_type(a, dtype) -> Any:
        Cast a value to a specified data type.

    select_implementation(numpy_func, numba_func, use_numba: bool = True) -> callable:
        Select between numpy and numba implementations based on availability and preference.

    dual_implementation(numpy_func: callable, numba_func: callable) -> callable:
        Decorator to create function selector that chooses between numpy and numba implementations.
"""

import os
import warnings
from collections.abc import Callable
from functools import wraps

import numpy as np
from laser_core.laserframe import LaserFrame
from laser_core.migration import distance


def assert_row_vector(vec: np.ndarray) -> None:
    # for scalars
    if vec.size == 1:
        return

    # For 1D arrays (shape: (n,))
    assert vec.ndim == 1, f"Expected 1D array, got {vec.ndim}D"

    # OR for 2D row vectors (shape: (1, n))
    assert vec.ndim == 2, f"Expected 2D array, got {vec.ndim}D"
    assert vec.shape[0] == 1, f"Expected row vector, got shape {vec.shape}"


def calc_distances(latitudes: np.ndarray, longitudes: np.ndarray, verbose: bool = False) -> np.ndarray:
    """
    Calculate the pairwise distances between points given their latitudes and longitudes.

    Parameters:

        latitudes (np.ndarray): A 1-dimensional array of latitudes.
        longitudes (np.ndarray): A 1-dimensional array of longitudes with the same shape as latitudes.
        verbose (bool, optional): If True, prints the upper left corner of the distance matrix. Default is False.

    Returns:

        np.ndarray: A 2-dimensional array where the element at [i, j] represents the distance in km between the i-th and j-th points.

    Raises:

        AssertionError: If latitudes is not 1-dimensional or if latitudes and longitudes do not have the same shape.
    """

    assert latitudes.ndim == 1, "Latitude array must be one-dimensional"
    assert longitudes.shape == latitudes.shape, "Latitude and longitude arrays must have the same shape"
    npatches = len(latitudes)
    distances = np.zeros((npatches, npatches), dtype=np.float32)
    for i, (lat, long) in enumerate(zip(latitudes, longitudes, strict=False)):
        distances[i, :] = distance(lat, long, latitudes, longitudes)

    if verbose:
        print(f"Upper left corner of distance matrix:\n{distances[0:4, 0:4]}")

    return distances


def calc_capacity(population: np.uint32, nticks: np.uint32, cbr: np.float32, verbose: bool = False) -> int:
    """
    Calculate the population capacity after a given number of ticks based on a constant birth rate (CBR).

    Args:

        population (np.uint32): The initial population.
        nticks (np.uint32): The number of ticks (time steps) to simulate.
        cbr (np.float32): The constant birth rate per 1000 people per year.
        verbose (bool, optional): If True, prints detailed population growth information. Defaults to False.

    Returns:

        np.uint32: The estimated population capacity after the given number of ticks.
    """

    # We assume a constant birth rate (CBR) for the population growth
    # The formula is: P(t) = P(0) * (1 + CBR)^t
    # where P(t) is the population at time t, P(0) is the initial population, and t is the number of ticks
    # We need to allocate space for the population data for each tick
    # We will use the maximum population growth to estimate the capacity
    # We will use the maximum population growth to estimate the capacity
    daily_rate = (cbr / 1000) / 365.0  # CBR is per 1000 people per year
    capacity = np.uint32(population * (1 + daily_rate) ** nticks)

    if verbose:
        print(f"Population growth: {population:,} … {capacity:,}")
        alternate = np.uint32(population * (1 + cbr / 1000) ** (nticks / 365))
        print(f"Alternate growth:  {population:,} … {alternate:,}")

    return int(capacity)


def seed_infections_randomly(model, ninfections: int = 100) -> None:
    """
    Seed initial infections in random locations at the start of the simulation.
    This function randomly selects individuals from the population and seeds
    them with an infection, based on the specified number of initial infections.

    Args:

        model: The simulation model containing the population and parameters.
        ninfections (int, optional): The number of initial infections to seed.
                                     Defaults to 100.

    Returns:

        None
    """

    # Seed initial infections in random locations at the start of the simulation
    cinfections = 0
    while cinfections < ninfections:
        index = model.prng.integers(0, model.population.count)
        if model.population.susceptibility[index] > 0:
            model.population.itimer[index] = model.params.inf_mean
            cinfections += 1

    return


def seed_infections_in_patch(model, ipatch: int, ninfections: int = 100) -> None:
    """
    Seed initial infections in a specific patch of the population at the start of the simulation.
    This function randomly selects individuals from the specified patch and sets their infection timer
    to the mean infection duration, effectively marking them as infected. The process continues until
    the desired number of initial infections is reached.

    Args:

        model: The simulation model containing the population and parameters.
        ipatch (int): The identifier of the patch where infections should be seeded.
        ninfections (int, optional): The number of initial infections to seed. Defaults to 100.

    Returns:

        None
    """

    # Seed initial infections in a specific location at the start of the simulation
    ids = np.nonzero(np.logical_and(model.population.nodeid == ipatch, model.population.susceptibility > 0))[0]
    np.random.shuffle(ids)
    model.population.itimer[ids[: min(ninfections, len(ids))]] = model.params.inf_mean

    return


def cast_type(a, dtype, round: bool = False):
    """
    Cast a value to a specified data type.
    Note that this casting truncates by default.

    Args:
        a: The value to cast
        dtype: The target data type

    Returns:
        The value cast to the specified data type
    """
    if isinstance(a, np.ndarray):
        if round:
            return np.round(a.astype(dtype)) if a.dtype != dtype else a
        else:
            return a.astype(dtype) if a.dtype != dtype else a
    else:
        return a


class StateArray(np.ndarray):
    """
    A numpy array wrapper that provides attribute access to state compartments.

    This class allows accessing state compartments by name (e.g., states.S, states.I, states.R)
    while maintaining full numpy array functionality and backward compatibility with
    numeric indexing (e.g., states[0], states[1]).

    Example:
        >>> states = StateArray(np.zeros((3, 100)), state_names=["S", "I", "R"])
        >>> states.S[0] = 1000  # Set susceptible population in patch 0
        >>> prevalence = states.I / states.sum(axis=0)  # Calculate prevalence
        >>> states[0] += births  # Numeric indexing still works

    Args:
        input_array: The numpy array to wrap
        state_names: List of state compartment names (e.g., ["S", "E", "I", "R"])
    """

    def __new__(cls, input_array, state_names=None):
        obj = np.asarray(input_array).view(cls)
        obj._state_names = state_names or []
        obj._state_indices = {name: i for i, name in enumerate(obj._state_names)}
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._state_names = getattr(obj, "_state_names", [])
        self._state_indices = getattr(obj, "_state_indices", {})

    def __getattr__(self, name):
        if name in self._state_indices:
            return self[self._state_indices[name]]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name.startswith("_") or name in ["base", "dtype", "shape", "size", "ndim"]:
            super().__setattr__(name, value)
        elif hasattr(self, "_state_indices") and name in self._state_indices:
            self[self._state_indices[name]] = cast_type(value, self.dtype)
        else:
            # For invalid state names, raise AttributeError
            if hasattr(self, "_state_indices") and name not in ["base", "dtype", "shape", "size", "ndim"]:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
            super().__setattr__(name, value)

    @property
    def state_names(self):
        """Return the list of state compartment names."""
        return self._state_names.copy()

    def get_state_index(self, name):
        """Get the numeric index for a state compartment name."""
        return self._state_indices.get(name)


def get_laserframe_properties(laserframe: LaserFrame):
    """
    Get the scalar and vector properties of a laserframe that are numpy arrays.
    """
    properties = set()
    for key, value in laserframe.__dict__.items():
        if isinstance(value, np.ndarray) and value.shape[-1] == laserframe._capacity:
            properties.add(key)
    return properties


# Function Selection Utilities


def _check_numba_available() -> bool:
    """
    Check if numba is available and importable.

    Returns:
        bool: True if numba is available, False otherwise.
    """
    try:
        import numba  # noqa: PLC0415, F401

        return True
    except ImportError:
        return False


def _get_numba_preference() -> bool:
    """
    Get user preference for numba usage from environment variables.

    Returns:
        bool: True if numba should be used (default), False otherwise.
    """
    env_var = os.environ.get("LASER_MEASLES_USE_NUMBA", "true").lower()
    return env_var in ("true", "1", "yes", "on")


def select_implementation(numpy_func: Callable, numba_func: Callable, use_numba: bool = True) -> Callable:
    """
    Select between numpy and numba implementations based on availability and preference.

    Args:
        numpy_func: The numpy implementation function.
        numba_func: The numba implementation function.
        use_numba: Whether to prefer numba implementation if available.

    Returns:
        The selected function implementation.
    """
    # Check user preference
    if not use_numba:
        return numpy_func

    # Check environment variable
    if not _get_numba_preference():
        return numpy_func

    # Check numba availability
    if not _check_numba_available():
        warnings.warn(
            "Numba is not available, falling back to numpy implementation. Set LASER_MEASLES_USE_NUMBA=false to suppress this warning.",
            UserWarning,
            stacklevel=2,
        )
        return numpy_func

    return numba_func


def dual_implementation(numpy_func: Callable, numba_func: Callable) -> Callable:
    """
    Decorator to create function selector that chooses between numpy and numba implementations.

    Args:
        numpy_func: The numpy implementation function.
        numba_func: The numba implementation function.

    Returns:
        A wrapper function that selects the appropriate implementation.
    """

    @wraps(numpy_func)
    def wrapper(*args, use_numba: bool = True, **kwargs):
        selected_func = select_implementation(numpy_func, numba_func, use_numba)
        return selected_func(*args, **kwargs)

    # Store both implementations as attributes for direct access
    wrapper.numpy_func = numpy_func
    wrapper.numba_func = numba_func

    return wrapper
