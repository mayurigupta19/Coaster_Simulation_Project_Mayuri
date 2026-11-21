# COASTER 3D — Project Report

## 1. Introduction
COASTER 3D is an interactive roller-coaster simulation developed for a Computer Graphics course. It demonstrates 3D object modelling, transformations, lighting, camera control, geometric construction and animation using Python, GLFW and PyOpenGL.

## 2. Objectives
- Construct a three-dimensional closed roller-coaster track.
- Animate a train continuously along the track.
- Orient each train car to the local direction of travel.
- Provide interactive orbit and on-ride camera modes.
- Demonstrate lighting, depth testing and 3D transformations.

## 3. Tools and Technologies
Python, OpenGL, PyOpenGL, GLFW and the Python standard library.

## 4. System Design
The track is represented by a parametric function of an angle `t`. Its X and Z coordinates form a closed oval while its Y coordinate varies sinusoidally to create hills and dips. Sampling this function creates rail segments and support locations. The train position is calculated from an animation phase. A nearby sample estimates the tangent, which determines the car's orientation. A set of local basis vectors is supplied to the model transformation matrix so cars follow bends and elevation changes.

## 5. Computer Graphics Concepts
- **3D modelling:** cubes, spheres and cylinders form train cars, wheels, rails, ties, supports and trees.
- **Parametric geometry:** a function maps a parameter to a 3D track position.
- **Translation:** places scene objects at their world coordinates.
- **Rotation and orientation:** aligns cars and camera with the track direction.
- **Lighting:** OpenGL light and material settings provide depth and shape cues.
- **Perspective projection:** `gluPerspective` creates a perspective view.
- **Depth buffering:** ensures nearer objects obscure farther objects.
- **Animation:** the train phase advances over time using frame delta time.
- **Interaction:** GLFW callbacks process keyboard and mouse input.

## 6. Algorithm
1. Initialize GLFW and create an OpenGL window.
2. Enable depth testing and lighting.
3. Define a closed parametric track.
4. Sample the track to draw rails, ties and support pillars.
5. Advance the train phase using elapsed frame time.
6. Calculate each car's position and tangent from the track function.
7. Build a local orientation basis and draw the car model.
8. Update the camera from mouse, scroll and keyboard input.
9. Render continuously until the user exits.

## 7. Conclusion
The project combines geometry, transformations, lighting, perspective projection, animation and event-driven interaction in one real-time 3D application. It can be extended with braking zones, stations, passenger models, particle effects, track editing and physically based motion.
