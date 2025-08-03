"""Tests for the transforms module."""

import pytest
import numpy as np
from special_relativity_grapher.transforms import (
    getGamma, lorentzTranformPt, addVelocities, 
    lorentzTransformObject, getEOM
)

class TestGamma:
    """Test the gamma factor calculation."""
    
    def test_gamma_at_rest(self):
        """Test gamma factor for zero velocity."""
        result = getGamma([0, 0])
        assert abs(result - 1.0) < 1e-10
    
    def test_gamma_half_c(self):
        """Test gamma factor at v = 0.5c."""
        result = getGamma([0.5, 0])
        expected = 1 / np.sqrt(1 - 0.25)  # 1/sqrt(0.75)
        assert abs(result - expected) < 1e-10
    
    def test_gamma_relativistic(self):
        """Test gamma factor at high velocity."""
        result = getGamma([0.9, 0])
        expected = 1 / np.sqrt(1 - 0.81)  # 1/sqrt(0.19)
        assert abs(result - expected) < 1e-10
    
    def test_gamma_2d_velocity(self):
        """Test gamma factor with 2D velocity."""
        result = getGamma([0.6, 0.8])
        expected = 1 / np.sqrt(1 - 0.36 - 0.64)  # Should approach infinity
        # This is v = c, so gamma should be very large
        assert result > 100  # Should be much larger than normal values


class TestLorentzTransform:
    """Test Lorentz transformations."""
    
    def test_transform_at_rest(self):
        """Test transformation with zero velocity."""
        point = [1, 2, 3]  # [t, x, y]
        velocity = [0, 0]
        result = lorentzTranformPt(point, velocity)
        np.testing.assert_allclose(result, point, atol=1e-10)
    
    def test_transform_time_only(self):
        """Test transformation affects time coordinate."""
        point = [1, 0, 0]  # Event at origin
        velocity = [0.5, 0]  # Moving in x direction
        result = lorentzTranformPt(point, velocity)
        
        # Time should be dilated
        gamma = getGamma(velocity)
        expected_time = gamma * 1  # t' = γt when x=0
        assert abs(result[0] - expected_time) < 1e-10
    
    def test_transform_spatial_coordinates(self):
        """Test transformation of spatial coordinates."""
        point = [0, 1, 0]  # Spatial point at t=0
        velocity = [0.5, 0]
        result = lorentzTranformPt(point, velocity)
        
        # x coordinate should be affected
        gamma = getGamma(velocity)
        assert abs(result[1] - 1.0) > 1e-10  # Should be different
        # y coordinate should be unchanged
        assert abs(result[2] - 0.0) < 1e-10


class TestVelocityAddition:
    """Test relativistic velocity addition."""
    
    def test_velocity_addition_zero(self):
        """Test adding zero velocities."""
        result = addVelocities([0, 0], [0, 0], [0, 0])
        np.testing.assert_allclose(result, [0, 0], atol=1e-10)
    
    def test_velocity_addition_classical_limit(self):
        """Test velocity addition in classical limit."""
        # Small velocities should behave classically
        result = addVelocities([0.1, 0], [0.1, 0], [0, 0])
        # Should be approximately 0.2 in classical limit
        assert abs(result[0] - 0.2) < 0.01
    
    def test_velocity_addition_relativistic(self):
        """Test velocity addition at high speeds."""
        result = addVelocities([0.5, 0], [0.5, 0], [0, 0])
        # Result should be less than 1.0 (speed of light)
        assert result[0] < 1.0
        # Should be greater than simple addition would give at high speeds
        assert result[0] > 0.8  # Relativistic formula gives ~0.8


class TestObjectTransforms:
    """Test object-level transformations."""
    
    def test_transform_object(self):
        """Test transforming a multi-point object."""
        obj = [[0, 0, 0], [0, 1, 0], [0, 0, 1]]  # Three points
        velocity = [0.5, 0]
        result = lorentzTransformObject(obj, velocity)
        
        assert len(result) == 3  # Same number of points
        # Each point should be transformed
        for original, transformed in zip(obj, result):
            individual_transform = lorentzTranformPt(original, velocity)
            np.testing.assert_allclose(transformed, individual_transform, atol=1e-10)


class TestEOM:
    """Test equation of motion generation."""
    
    def test_eom_stationary_object(self):
        """Test EOM for stationary object."""
        obj = [[0, 1, 2]]  # Single point at t=0, x=1, y=2
        object_velo = [0, 0]  # Stationary
        frame1_velo = [0, 0]  # Ground frame
        frame2_velo = [0, 0]  # Ground frame
        
        result = getEOM(obj, object_velo, frame1_velo, frame2_velo)
        
        assert len(result) == 1  # One point means one EOM
        x_eom, y_eom = result[0]
        
        # For stationary object: x = 0*t + 1, y = 0*t + 2
        assert abs(x_eom[0]) < 1e-10  # x slope should be ~0
        assert abs(x_eom[1] - 1) < 1e-5  # x intercept should be ~1
        assert abs(y_eom[0]) < 1e-10  # y slope should be ~0  
        assert abs(y_eom[1] - 2) < 1e-5  # y intercept should be ~2
    
    def test_eom_moving_object(self):
        """Test EOM for moving object."""
        obj = [[0, 0, 0]]  # Point at origin
        object_velo = [0.5, 0]  # Moving in x direction
        frame1_velo = [0, 0]  # Object's frame
        frame2_velo = [0, 0]  # Observation frame (same as object frame)
        
        result = getEOM(obj, object_velo, frame1_velo, frame2_velo)
        
        assert len(result) == 1
        x_eom, y_eom = result[0]
        
        # x should have positive slope (moving in +x)
        assert x_eom[0] > 0
        # y should be constant (no y motion)
        assert abs(y_eom[0]) < 1e-5
