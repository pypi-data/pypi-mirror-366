"""
Utility functions for special relativity simulations.

This module contains helper functions and common conditions used
throughout the special relativity grapher library.
"""


def trueCond(t):
    """
    Always true condition function for simulations.
    
    This is a simple condition function that always returns True,
    useful for running simulations without any stopping conditions.
    
    Args:
        t (float): Current time (unused)
        
    Returns:
        bool: Always True
    """
    return True


def stopAtTime(stop_time):
    """
    Create a condition function that stops at a specific time.
    
    Args:
        stop_time (float): Time at which to stop the simulation
        
    Returns:
        function: Condition function that returns False when t >= stop_time
    """
    def condition(t):
        return t < stop_time
    return condition


def stopAtEvent(event_time, tolerance=0.1):
    """
    Create a condition function that stops near a specific event time.
    
    Args:
        event_time (float): Time of the event to stop at
        tolerance (float): Time tolerance around the event (default 0.1)
        
    Returns:
        function: Condition function that returns False near event_time
    """
    def condition(t):
        return abs(t - event_time) > tolerance
    return condition
