"""Tests for the simulation module."""

import pytest
import numpy as np
from special_relativity_grapher.simulation import Simulation
from special_relativity_grapher.utils import trueCond


class TestSimulation:
    """Test the Simulation class."""
    
    def test_simulation_init(self):
        """Test simulation initialization."""
        sim = Simulation()
        
        # Should have origin point by default
        assert len(sim.objects) == 1
        assert len(sim.velocieis) == 1
        assert len(sim.frameVelocity) == 1
        
        # Check origin point
        assert sim.objects[0] == [[0, 0, 0]]
        assert sim.velocieis[0] == [0, 0]
        assert sim.frameVelocity[0] == [0, 0]
    
    def test_add_object(self):
        """Test adding a generic object."""
        sim = Simulation()
        initial_count = len(sim.objects)
        
        test_object = [[0, 1, 2], [0, 3, 4]]
        test_velocity = [0.5, 0]
        test_frame_velo = [0.2, 0]
        
        sim.addObject(test_object, test_velocity, test_frame_velo)
        
        assert len(sim.objects) == initial_count + 1
        assert sim.objects[-1] == test_object
        assert sim.velocieis[-1] == test_velocity
        assert sim.frameVelocity[-1] == test_frame_velo
    
    def test_add_point(self):
        """Test adding a single point."""
        sim = Simulation()
        initial_count = len(sim.objects)
        
        test_point = [1, 2, 3]
        test_velocity = [0.3, 0.4]
        test_frame_velo = [0.1, 0]
        
        sim.addPt(test_point, test_velocity, test_frame_velo)
        
        assert len(sim.objects) == initial_count + 1
        assert sim.objects[-1] == [test_point]
        assert sim.velocieis[-1] == test_velocity
        assert sim.frameVelocity[-1] == test_frame_velo
    
    def test_add_line_horizontal(self):
        """Test adding a horizontal line."""
        sim = Simulation()
        initial_count = len(sim.objects)
        
        start_pt = [1, 2]
        length = 5
        t = 0
        
        sim.addLine(start_pt, length, [0, 0], [0, 0], True, t)
        
        assert len(sim.objects) == initial_count + 1
        line = sim.objects[-1]
        assert len(line) == 2  # Start and end points
        assert line[0] == [t, start_pt[0], start_pt[1]]
        assert line[1] == [t, start_pt[0] + length, start_pt[1]]
    
    def test_add_line_vertical(self):
        """Test adding a vertical line."""
        sim = Simulation()
        initial_count = len(sim.objects)
        
        start_pt = [1, 2]
        length = 5
        t = 0
        
        sim.addLine(start_pt, length, [0, 0], [0, 0], False, t)
        
        assert len(sim.objects) == initial_count + 1
        line = sim.objects[-1]
        assert len(line) == 2  # Start and end points
        assert line[0] == [t, start_pt[0], start_pt[1]]
        assert line[1] == [t, start_pt[0], start_pt[1] + length]
    
    def test_add_train(self):
        """Test adding a train (rectangle)."""
        sim = Simulation()
        initial_count = len(sim.objects)
        
        bottom_left = [1, 2]
        length = 4
        height = 3
        t = 0
        
        sim.addTrain(bottom_left, length, height, [0, 0], [0, 0], t)
        
        assert len(sim.objects) == initial_count + 1
        train = sim.objects[-1]
        assert len(train) == 5  # Rectangle has 5 points (closed loop)
        
        # Check corners
        assert train[0] == [t, bottom_left[0], bottom_left[1]]  # Bottom-left
        assert train[1] == [t, bottom_left[0] + length, bottom_left[1]]  # Bottom-right
        assert train[2] == [t, bottom_left[0] + length, bottom_left[1] + height]  # Top-right
        assert train[3] == [t, bottom_left[0], bottom_left[1] + height]  # Top-left
        assert train[4] == [t, bottom_left[0], bottom_left[1]]  # Back to start
    
    def test_add_person(self):
        """Test adding a person figure."""
        sim = Simulation()
        initial_count = len(sim.objects)
        
        pos = [1, 2]
        size = 2
        t = 0
        
        sim.addPerson(pos, [0, 0], [0, 0], size, t)
        
        assert len(sim.objects) == initial_count + 1
        person = sim.objects[-1]
        assert len(person) == 8  # Person figure has 8 points
        
        # All points should have time coordinate t
        for point in person:
            assert point[0] == t
    
    def test_add_event(self):
        """Test adding a spacetime event."""
        sim = Simulation()
        initial_count = len(sim.events)
        
        test_event = [1, 2, 3]  # [t, x, y]
        test_frame_velo = [0.5, 0]
        
        sim.addEvent(test_event, test_frame_velo)
        
        assert len(sim.events) == initial_count + 1
        assert sim.events[-1] == test_event
        assert sim.eventVelos[-1] == test_frame_velo
    
    def test_add_pulse(self):
        """Test adding pulse events."""
        sim = Simulation()
        initial_count = len(sim.events)
        
        pt = [1, 2]
        dT = 1.0
        Ts = 0
        Tend = 3
        frame_velo = [0, 0]
        
        sim.addPulse(pt, dT, Ts, Tend, frame_velo)
        
        # Should add 4 events (at t = 0, 1, 2, 3)
        expected_events = 4
        assert len(sim.events) == initial_count + expected_events
        
        # Check that events are at correct times and positions
        new_events = sim.events[-expected_events:]
        expected_times = [0, 1, 2, 3]
        for i, event in enumerate(new_events):
            assert abs(event[0] - expected_times[i]) < 1e-10  # Time
            assert event[1] == pt[0]  # x position
            assert event[2] == pt[1]  # y position


class TestSimulationRun:
    """Test running simulations."""
    
    def test_run_simulation_basic(self):
        """Test basic simulation run."""
        sim = Simulation()
        
        # Add a simple stationary point
        sim.addPt([0, 1, 2], [0, 0], [0, 0])
        
        # Run simulation
        times, objects = sim.runSimulation([0, 0], 0.1, 0, 1, trueCond)
        
        assert len(times) > 0
        assert len(objects) == len(times)
        
        # Each time step should have objects
        for time_step_objects in objects:
            assert len(time_step_objects) >= 1  # At least the origin
    
    def test_run_simulation_with_events(self):
        """Test simulation with events."""
        sim = Simulation()
        
        # Add an event
        sim.addEvent([0.5, 1, 2], [0, 0])
        
        # Run simulation
        times, objects = sim.runSimulation([0, 0], 0.1, 0, 1, trueCond)
        
        # Should have normal objects plus event representations
        assert len(times) > 0
        assert len(objects) == len(times)
    
    def test_run_simulation_different_frames(self):
        """Test simulation in different reference frames."""
        sim = Simulation()
        
        # Add a moving object
        sim.addPt([0, 0, 0], [0.5, 0], [0, 0])
        
        # Run in ground frame
        times1, objects1 = sim.runSimulation([0, 0], 0.1, 0, 1, trueCond)
        
        # Run in moving frame
        times2, objects2 = sim.runSimulation([0.3, 0], 0.1, 0, 1, trueCond)
        
        # Both should produce results
        assert len(times1) > 0
        assert len(times2) > 0
        
        # Results should be different (same object seen from different frames)
        # This is a basic check - detailed physics verification would need more complex assertions
