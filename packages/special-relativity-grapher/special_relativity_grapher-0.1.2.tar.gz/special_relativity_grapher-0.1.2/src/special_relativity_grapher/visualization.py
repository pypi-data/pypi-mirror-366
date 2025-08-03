"""
Visualization functions for special relativity simulations.

This module provides functions for creating Minkowski diagrams and animations
of relativistic effects.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation


def Minkowski(frame2Velo, frame1Objects, frame2Objects, Ielev=30, Iazi=45):
    """
    Create a 3D Minkowski spacetime diagram.
    
    Plots objects in two different reference frames on a 3D Minkowski diagram
    showing both coordinate systems and their respective axes.
    
    Args:
        frame2Velo (list): Velocity [vx, vy] of the second frame
        frame1Objects (list): Objects in the first (rest) frame
        frame2Objects (list): Objects in the second (moving) frame  
        Ielev (int): Elevation angle for 3D view (default 30)
        Iazi (int): Azimuth angle for 3D view (default 45)
    """
    vPar = frame2Velo
    vPerp = np.array([0, frame2Velo[1], -1 * frame2Velo[0]])
    vMag = (vPar[0] * vPar[0] + vPar[1] * vPar[1])** 0.5
    vUnit = np.array(vPar)/vMag

    vPerpUnit = vPerp/vMag
    vParUnit = np.array(vPar)/vMag

    newTime = np.array([1, vPar[0], vPar[1]])
    newV = np.array([vMag, vUnit[0], vUnit[1]])

    tUnit = newTime/(np.linalg.norm(newTime))
    vUnit = newV/np.array(np.linalg.norm(newV))
    Uprime = ((1 + vMag ** 2) /(1 - vMag**2)) ** 0.5
    tUnit = Uprime * tUnit
    vUnit = Uprime * vUnit

    newX = (vParUnit[0] * vUnit + vParUnit[1] * vPerpUnit)
    newY = (vParUnit[1] * vUnit - vParUnit[0] * vPerpUnit)
    newT = tUnit

    xAxis = []
    yAxis = []
    tAxis = []
    for i in range(50):
        xAxis.append(newX * i)
        yAxis.append(newY * i)
        tAxis.append(newT * i)
    xAxis = np.array(xAxis)
    yAxis = np.array(yAxis)
    tAxis = np.array(tAxis)

    newFrame2 = []
    for obj in frame2Objects:
        objArr = []
        for pt in obj:
            newPt = pt[0] * newT + pt[1] * newX + pt[2] * newY
            objArr.append(newPt)
        newFrame2.append(objArr)
    newFrame2 = np.array(newFrame2)

    Axis = np.linspace(0, 50, 50)
    Zeros = np.zeros(50)

    # Plotting
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 50)
    ax.set_zlim(0, 50)
    ax.plot(Axis, Zeros, Zeros, label="x", color="dodgerblue")
    ax.plot(Zeros, Axis, Zeros, label="y", color="deepskyblue")
    ax.plot(Zeros, Zeros, Axis, label="t", color="lightskyblue")

    ax.plot(xAxis[:,1], xAxis[:,2], xAxis[:,0], label="x'", color="red")
    ax.plot(yAxis[:,1], yAxis[:,2], yAxis[:,0], label="y'", color="firebrick")
    ax.plot(tAxis[:,1], tAxis[:,2], tAxis[:,0], label="t'", color="salmon")

    for obj in frame1Objects:
        obj = np.array(obj)
        ax.plot(obj[:,0], obj[:,1], obj[:,2], 'o', markersize=2)

    for obj in newFrame2:
        obj = np.array(obj)
        ax.plot(obj[:,0], obj[:,1], obj[:,2], 'o', markersize=2)

    ax.legend()
    ax.view_init(elev=Ielev, azim=Iazi)
    plt.title("Minkowski Diagram")
    plt.show()


def RelatavisticAnimation(simulations, plotLimits, title):
    """
    Create an animated visualization of relativistic effects.
    
    Takes a list of simulations and creates an animation showing the evolution
    of objects over time. Multiple simulations can be stitched together to show
    discontinuous changes in velocity.
    
    Args:
        simulations (list): List of simulation outputs from runSimulation()
        plotLimits (list): Plot bounds [xmin, xmax, ymin, ymax]
        title (str): Title for the animation
        
    Returns:
        matplotlib.animation.FuncAnimation: Animation object
    """
    maxObjectNum = 0
    AllSimulations = []
    for simulation in simulations:
        for timeStep in simulation:
            AllSimulations.append(timeStep)
            if len(timeStep) > maxObjectNum:
                maxObjectNum = len(timeStep)
                
    fig, ax = plt.subplots()
    ax.set_xlim(plotLimits[0], plotLimits[1])
    ax.set_ylim(plotLimits[2], plotLimits[3])
    plt.title(title)
    lines = []
    for i in range(maxObjectNum):
        line, = ax.plot([], [], '-', marker='o')
        lines.append(line)

    def update(i, AllSimulations, lines, maxObjNum):
        """Update function for animation frames."""
        currentTs = AllSimulations[i]
        for j in range(maxObjNum):
            if j < len(currentTs):
                obj = np.array(currentTs[j])
                lines[j].set_data(obj[:,0], obj[:,1])
            else:
                lines[j].set_data([], [])
        return lines

    ani = animation.FuncAnimation(fig, update, len(AllSimulations), 
                                 fargs=[AllSimulations, lines, maxObjectNum],
                                 interval=20, blit=True, repeat=False)
    plt.close()
    return ani
