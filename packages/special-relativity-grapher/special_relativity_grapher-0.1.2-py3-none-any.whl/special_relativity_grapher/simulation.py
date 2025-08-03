"""
Core simulation classes for special relativity demonstrations.

This module contains the main Simulation class that manages objects, events,
and reference frames for relativistic physics simulations.
"""

import numpy as np
from .transforms import addVelocities, lorentzTranformPt, getEOM


class Simulation:
    """
    Main simulation class for special relativity visualizations.
    
    Manages objects, their velocities, reference frames, and spacetime events.
    Objects are represented as collections of points, and the simulation can
    transform everything into different reference frames.
    
    Uses natural units where c = 1.
    """
    
    def __init__(self):
        """Initialize simulation with empty object lists."""
        self.objects = []
        self.velocieis = []  # Note: keeping original typo for compatibility
        self.frameVelocity = []
        self.events = []
        self.eventVelos = []
        # Adding the origin to the simulation when we initialize
        self.objects.append([[0,0,0]])
        self.velocieis.append([0,0])
        self.frameVelocity.append([0,0])

    def addObject(self, ptList, velocity, frameVelo):
        """
        Add a generic object to the simulation.
        
        Args:
            ptList (list): List of 4-vector points [t,x,y] defining the object
            velocity (list): Object velocity [vx, vy] in its frame
            frameVelo (list): Velocity [vx, vy] of the object's frame relative to ground
        """
        self.objects.append(ptList)
        self.velocieis.append(velocity)
        self.frameVelocity.append(frameVelo)

    def addPt(self, fVec, velocity, frameVelo):
        """
        Add a single point to the simulation.
        
        Args:
            fVec (list): 4-vector [t,x,y] position
            velocity (list): Point velocity [vx, vy] in its frame
            frameVelo (list): Velocity [vx, vy] of the point's frame relative to ground
        """
        self.objects.append([fVec])
        self.velocieis.append(velocity)
        self.frameVelocity.append(frameVelo)

    def addLine(self, startPt, L, velocity, frameVelo, doX, t):
        """
        Add a line segment to the simulation.
        
        Args:
            startPt (list): Starting point [x, y]
            L (float): Length of the line
            velocity (list): Line velocity [vx, vy] in its frame
            frameVelo (list): Velocity [vx, vy] of the line's frame relative to ground
            doX (bool): If True, line extends in X direction; if False, in Y direction
            t (float): Time coordinate for the line
        """
        line = [[t, startPt[0], startPt[1]]]
        if doX:
            line.append([t, startPt[0] + L, startPt[1]])
        if not doX:
            line.append([t, startPt[0], startPt[1] + L])
        self.objects.append(line)
        self.velocieis.append(velocity)
        self.frameVelocity.append(frameVelo)

    def addTrain(self, bottomLeft, L, H, velocity, frameVelo, t):
        """
        Add a rectangular train/box to the simulation.
        
        Args:
            bottomLeft (list): Bottom-left corner position [x, y]
            L (float): Length (width) of the train
            H (float): Height of the train
            velocity (list): Train velocity [vx, vy] in its frame
            frameVelo (list): Velocity [vx, vy] of the train's frame relative to ground
            t (float): Time coordinate for the train
        """
        startPt = bottomLeft
        train = [[t, bottomLeft[0], bottomLeft[1]], [t, startPt[0] + L, startPt[1]], 
                [t, startPt[0] + L, startPt[1] + H], [t, startPt[0], startPt[1] + H], 
                [t, bottomLeft[0], bottomLeft[1]]]

        self.objects.append(train)
        self.velocieis.append(velocity)
        self.frameVelocity.append(frameVelo)

    def addPerson(self, pos, velocity, frameVelo, size, t):
        """
        Add a simple person figure to the simulation.
        
        Args:
            pos (list): Position [x, y] of the person
            velocity (list): Person velocity [vx, vy] in its frame
            frameVelo (list): Velocity [vx, vy] of the person's frame relative to ground
            size (float): Size scale factor for the person
            t (float): Time coordinate for the person
        """
        h = 0.5 * size

        person = [[t,pos[0],pos[1]], [t, pos[0] + 0.5 * h, pos[1]], [t,pos[0] + 0.5 * h, pos[1] + h],
                  [t, pos[0] - 0.5 * h, pos[1]+h], [t,pos[0] - 0.5 * h, pos[1]], [t,pos[0],pos[1]],
                  [t,pos[0] + 0.5 * h, pos[1] - 1.5 * h], [t,pos[0] - 0.5 * h, pos[1] - 1.5 * h]]

        self.objects.append(person)
        self.velocieis.append(velocity)
        self.frameVelocity.append(frameVelo)

    def addEvent(self, event, fVelo):
        """
        Add a spacetime event to the simulation.
        
        Args:
            event (list): Spacetime event [t, x, y]
            fVelo (list): Velocity [vx, vy] of the event's frame relative to ground
        """
        self.events.append(event)
        self.eventVelos.append(fVelo)

    def addPulse(self, pt, dT, Ts, Tend, frameVelo):
        """
        Add a series of pulse events like a clock.
        
        Creates uniformly spaced events from Ts to Tend with interval dT.
        
        Args:
            pt (list): Position [x, y] where pulses occur
            dT (float): Time interval between pulses
            Ts (float): Start time
            Tend (float): End time
            frameVelo (list): Velocity [vx, vy] of the pulse frame relative to ground
        """
        range_vals = np.linspace(Ts, Tend, int((Tend - Ts) / dT) + 1, endpoint=True)
        for i in range_vals:
            self.events.append([i, pt[0], pt[1]])
            self.eventVelos.append(frameVelo)

    def addLightBounce(self, pt, dT, Ts, Tend, frameVelo):
        """
        Add light bouncing between y = -1 and y = 1.
        
        Args:
            pt (list): Starting position [x, y]
            dT (float): Time step
            Ts (float): Start time
            Tend (float): End time
            frameVelo (list): Velocity [vx, vy] of the frame relative to ground
        """
        range_vals = np.arange(Ts, Tend + dT, dT)
        y = pt[1]
        direction = 1.0  # up
        for i in range_vals:  # Create a piece-wise function for the light bouncing
            if y >= 1 or y > 0.999:
                y = 1.0
                direction = -1.0
            elif y <= -1 or y <= -0.999:
                y = -1.0
                direction = 1.0
            self.events.append([i, pt[0], y])
            self.eventVelos.append(frameVelo)
            y = y + direction * dT

    def runSimulation(self, frameVelocity, dT, Ts, Tend, condition):
        """
        Run the simulation in a given reference frame.
        
        Transforms all objects and events to the specified frame and generates
        position data over time.
        
        Args:
            frameVelocity (list): Velocity [vx, vy] of the observation frame
            dT (float): Time step size
            Ts (float): Start time
            Tend (float): End time
            condition (function): Function that takes time and returns bool to continue
            
        Returns:
            tuple: (times, objects) where objects[t][i][j][pos] gives position data
        """
        newEvents = []
        objectEOMS = []
        for i in range(len(self.events)):
            relVel = addVelocities([0,0], self.eventVelos[i], frameVelocity)
            newEvents.append(lorentzTranformPt(self.events[i], relVel))
        for i in range(len(self.objects)):
            EOM = getEOM(self.objects[i], self.velocieis[i],
                        self.frameVelocity[i], frameVelocity)
            objectEOMS.append(EOM)

        times = []
        objects = []
        currentT = Ts
        while currentT < Tend and condition(currentT):
            times.append(currentT)
            timeStepObjects = []
            for EOM in objectEOMS:
                currentObject = []
                for pt in EOM:
                    Xpos = pt[0][0] * currentT + pt[0][1]
                    Ypos = pt[1][0] * currentT + pt[1][1]
                    vec = [Xpos, Ypos]
                    currentObject.append(vec)
                timeStepObjects.append(currentObject)

            for event in newEvents:
                if np.abs(event[0] - currentT) < 10 * dT:
                    timeStepObjects.append([[event[1], event[2]]])

            objects.append(timeStepObjects)
            currentT = currentT + dT

        return times, objects

    def runSimulationLight(self, frameVelocity, dT, Ts, Tend, condition):
        """
        Run simulation with different event timing for light bouncing.
        
        Similar to runSimulation but with tighter timing tolerance for events.
        
        Args:
            frameVelocity (list): Velocity [vx, vy] of the observation frame
            dT (float): Time step size
            Ts (float): Start time
            Tend (float): End time
            condition (function): Function that takes time and returns bool to continue
            
        Returns:
            tuple: (times, objects) where objects[t][i][j][pos] gives position data
        """
        newEvents = []
        objectEOMS = []
        for i in range(len(self.events)):
            relVel = addVelocities([0,0], self.eventVelos[i], frameVelocity)
            newEvents.append(lorentzTranformPt(self.events[i], relVel))
        for i in range(len(self.objects)):
            EOM = getEOM(self.objects[i], self.velocieis[i],
                        self.frameVelocity[i], frameVelocity)
            objectEOMS.append(EOM)

        times = []
        objects = []
        currentT = Ts
        while currentT < Tend and condition(currentT):
            times.append(currentT)
            timeStepObjects = []
            for EOM in objectEOMS:
                currentObject = []
                for pt in EOM:
                    Xpos = pt[0][0] * currentT + pt[0][1]
                    Ypos = pt[1][0] * currentT + pt[1][1]
                    vec = [Xpos, Ypos]
                    currentObject.append(vec)
                timeStepObjects.append(currentObject)

            for event in newEvents:
                if np.abs(event[0] - currentT) < 0.8 * dT:
                    timeStepObjects.append([[event[1], event[2]]])

            objects.append(timeStepObjects)
            currentT = currentT + dT

        return times, objects
