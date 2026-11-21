# COASTER 3D — Viva Questions and Answers

**1. What is the aim of this project?**  
To create an interactive 3D roller-coaster visualization in which a train moves along a curved track.

**2. Which technologies are used?**  
Python, PyOpenGL for OpenGL graphics, and GLFW for window creation and input events.

**3. What is OpenGL?**  
OpenGL is a cross-platform graphics API used to render 2D and 3D graphics.

**4. What is GLFW used for?**  
It creates the application window, manages the OpenGL context and receives keyboard and mouse input.

**5. How is the track generated?**  
A parametric function maps an angle to X, Y and Z coordinates. Sampling the function produces points used to draw the rails and supports.

**6. What is a parametric curve?**  
A curve whose coordinates are expressed as functions of a parameter, such as `x(t)`, `y(t)` and `z(t)`.

**7. How does the train move?**  
An animation parameter increases with elapsed time. The current parameter value is used to calculate the train's position on the track.

**8. How do cars rotate with the track?**  
The program estimates the local tangent using nearby track points and builds a local orientation basis for each car.

**9. What is a tangent vector?**  
It indicates the direction in which a curve is moving at a particular point.

**10. What is perspective projection?**  
It makes distant objects appear smaller, producing a depth impression similar to human vision.

**11. Why is a depth buffer needed?**  
It stores depth information so objects are drawn in the correct front-to-back order.

**12. What is frame delta time?**  
The elapsed time between frames. Using it makes animation speed less dependent on frame rate.

**13. Which transformations are used?**  
Translation positions objects, while rotation and orientation align them with the track and camera.

**14. How can the user control the camera?**  
The user can drag to orbit, scroll to zoom and press C to switch to the on-ride camera.

**15. What are the limitations?**  
The track and speed are stylized for visualization; the simulation does not calculate real ride forces or structural safety.

**16. What is future scope?**  
Add realistic physics, braking and lift systems, passenger models, sound, particle effects, track editing and VR support.
