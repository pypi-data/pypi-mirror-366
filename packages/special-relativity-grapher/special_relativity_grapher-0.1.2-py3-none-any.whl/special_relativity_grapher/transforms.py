"""
Relativistic transformations and coordinate systems.

This module contains functions for Lorentz transformations, velocity addition,
and coordinate system conversions used in special relativity calculations.
"""

import numpy as np


def getGamma(Vf):
    """
    Calculate the Lorentz gamma factor for a given velocity.
    
    Args:
        Vf (list): Velocity vector [vx, vy] relative to the ground frame
        
    Returns:
        float: Gamma factor (1 - v²/c²)^(-1/2)
    """
    return (1 - Vf[0] * Vf[0] - Vf[1] * Vf[1]) ** (-0.5)


def lorentzTranformPt(fourVec, V):
    """
    Apply Lorentz transformation to a 4-vector point.
    
    Transforms a 4-vector from frame S to frame S' where S' is traveling at V w.r.t S.
    
    Args:
        fourVec (list): 4-vector [t, x, y] to transform
        V (list): Velocity [vx, vy] of frame S' relative to frame S
        
    Returns:
        numpy.ndarray: Transformed 4-vector
    """
    newFourVec = np.array(fourVec)
    g = getGamma(V)
    bx = V[0]
    by = V[1]
    g2 = g**2/(1 + g)
    LTMat = np.array([
        [g, -g * bx, -g * by],
        [-g * bx, 1 + g2 * bx * bx, g2 * bx * by],
        [-g * by, g2 * bx * by, 1 + g2 * by * by]
    ])
    return LTMat @ newFourVec


def addVelocities(objectVelo, Vf1, Vf2):
    """
    Apply relativistic velocity addition formula.
    
    Returns the velocity of an object moving at objectVelo in Frame 1 
    (moving at Vf1 w.r.t the ground frame) as seen from Frame 2 
    (moving at Vf2 w.r.t the ground frame).
    
    Args:
        objectVelo (list): Velocity [vx, vy] of object in Frame 1
        Vf1 (list): Velocity [vx, vy] of Frame 1 relative to ground frame  
        Vf2 (list): Velocity [vx, vy] of Frame 2 relative to ground frame
        
    Returns:
        list: Velocity [vx, vy] of object as seen from Frame 2
    """
    gamma = getGamma(objectVelo)
    Vvec = [gamma, gamma * objectVelo[0], gamma * objectVelo[1]]
    # Using -Vf1 since Frame 1 is moving at Vf1 wrt the ground, so the ground is
    # moving at -Vf1 wrt Frame 1
    GroundVec = lorentzTranformPt(Vvec, [-1 * Vf1[0], -1 * Vf1[1]])
    Frame2Vec = lorentzTranformPt(GroundVec, Vf2)
    return [Frame2Vec[1]/Frame2Vec[0], Frame2Vec[2]/Frame2Vec[0]]


def lorentzTransformObject(Object, V):
    """
    Apply Lorentz transformation to all points in an object.
    
    Args:
        Object (list): List of 4-vectors representing object points
        V (list): Velocity [vx, vy] for transformation
        
    Returns:
        list: List of transformed 4-vectors
    """
    newObject4Vectors = []
    for pt in Object:
        newFVec = lorentzTranformPt(pt, V)
        newObject4Vectors.append(newFVec)
    return newObject4Vectors


def getEOM(Object, objectVelo, Vf1, Vf2):
    """
    Get equations of motion for an object in a new reference frame.
    
    Returns the EOM for an object traveling at objectVelo in Frame 1 
    (moving at Vf1 w.r.t the ground frame) as seen from Frame 2.
    The equations are linear since all velocities are constant.
    
    Args:
        Object (list): List of 4-vector points defining the object
        objectVelo (list): Velocity [vx, vy] of object in Frame 1
        Vf1 (list): Velocity [vx, vy] of Frame 1 relative to ground
        Vf2 (list): Velocity [vx, vy] of Frame 2 relative to ground
        
    Returns:
        list: For each point, returns [[a,b],[c,d]] where x = at + b, y = ct + d
    """
    Vf1wrtVf2 = addVelocities([0,0], Vf1, Vf2)
    # We are using Vf1wrtVf2 since we are treating every endpoint of Object1 as
    # a point in spacetime, so it has a coordinate in Frame 1, which we transform
    # to frame 2. Then, we wait a few seconds and then transform the object to
    # frame 2. This gives us two points in frame 2 we can interpolate

    # We shouldn't run into any issues with simultaneity since points on the two
    # Events will be timelikely separated
    Object1 = lorentzTransformObject(Object, Vf1wrtVf2)
    dT = 1
    Object2 = []
    for pt in Object:
        newPt = [pt[0] + dT, pt[1] + dT * objectVelo[0], pt[2] + dT*objectVelo[1]]
        Object2.append(newPt)
    Object2 = lorentzTransformObject(Object2, Vf1wrtVf2)

    EOMS = []
    for i in range(len(Object1)):
        Tps = [Object1[i][0], Object2[i][0]]
        Xps = [Object1[i][1], Object2[i][1]]
        Yps = [Object1[i][2], Object2[i][2]]

        xLine = np.polyfit(np.array(Tps), np.array(Xps), 1)
        yLine = np.polyfit(np.array(Tps), np.array(Yps), 1)
        EOMS.append([xLine, yLine])
    return EOMS
