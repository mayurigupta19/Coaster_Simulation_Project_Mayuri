"""A 3D roller-coaster simulation built with Python, GLFW and PyOpenGL."""
import math
import sys
import time
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

WIDTH, HEIGHT = 1280, 800
TRACK_STEPS = 420
CAR_COUNT = 5
CAR_SPACING = 0.018

paused = False
show_supports = True
show_hud = True
speed = 0.085
camera_yaw = 38.0
camera_pitch = 24.0
camera_distance = 25.0
last_mouse = None
mouse_down = False
ride_camera = False


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def track_point(t):
    # A closed, undulating 3D track. t is measured in radians.
    x = 9.0 * math.cos(t)
    z = 6.5 * math.sin(t)
    y = 2.0 + 1.55 * math.sin(2.0 * t + 0.35) + 0.45 * math.sin(3.0 * t - 0.4)
    return (x, y, z)


def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def mul(a, s): return (a[0]*s, a[1]*s, a[2]*s)
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def length(a): return math.sqrt(dot(a, a))
def norm(a):
    l = length(a)
    return mul(a, 1.0/l) if l > 1e-8 else (0.0, 1.0, 0.0)


def basis(t):
    p = track_point(t)
    tangent = norm(sub(track_point(t + 0.001), track_point(t - 0.001)))
    side = norm(cross(tangent, (0.0, 1.0, 0.0)))
    up = norm(cross(side, tangent))
    return p, tangent, side, up


def cylinder_between(a, b, radius, color, slices=9):
    d = sub(b, a)
    h = length(d)
    if h < 1e-5: return
    direction = norm(d)
    zaxis = (0.0, 0.0, 1.0)
    axis = cross(zaxis, direction)
    angle = math.degrees(math.acos(clamp(dot(zaxis, direction), -1.0, 1.0)))
    glPushMatrix()
    glTranslatef(*a)
    if length(axis) > 1e-6:
        glRotatef(angle, *norm(axis))
    glColor3f(*color)
    q = gluNewQuadric()
    gluCylinder(q, radius, radius, h, slices, 1)
    gluDeleteQuadric(q)
    glPopMatrix()


def cube(center, size, color):
    x, y, z = center
    sx, sy, sz = size[0]/2, size[1]/2, size[2]/2
    verts = [
        (x-sx,y-sy,z-sz),(x+sx,y-sy,z-sz),(x+sx,y+sy,z-sz),(x-sx,y+sy,z-sz),
        (x-sx,y-sy,z+sz),(x+sx,y-sy,z+sz),(x+sx,y+sy,z+sz),(x-sx,y+sy,z+sz)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)]
    glColor3f(*color)
    glBegin(GL_QUADS)
    for face in faces:
        for i in face: glVertex3f(*verts[i])
    glEnd()


def sphere(pos, radius, color, slices=16, stacks=12):
    glPushMatrix(); glTranslatef(*pos); glColor3f(*color)
    q = gluNewQuadric(); gluSphere(q, radius, slices, stacks); gluDeleteQuadric(q)
    glPopMatrix()


def draw_ground():
    glColor3f(0.055, 0.12, 0.105)
    glBegin(GL_QUADS)
    glVertex3f(-40, -0.45, -40); glVertex3f(40, -0.45, -40)
    glVertex3f(40, -0.45, 40); glVertex3f(-40, -0.45, 40)
    glEnd()
    # Decorative platform rings
    for r in (12.5, 15.5, 19.0):
        glColor3f(0.10, 0.20, 0.17)
        glBegin(GL_LINE_LOOP)
        for i in range(100):
            a = 2*math.pi*i/100
            glVertex3f(r*math.cos(a), -0.43, r*math.sin(a))
        glEnd()


def draw_track():
    pts = [track_point(2*math.pi*i/TRACK_STEPS) for i in range(TRACK_STEPS+1)]
    # Support structure below the track
    if show_supports:
        for i in range(0, TRACK_STEPS, 7):
            p = pts[i]
            left = add(p, mul(basis(2*math.pi*i/TRACK_STEPS)[2], -0.72))
            right = add(p, mul(basis(2*math.pi*i/TRACK_STEPS)[2], 0.72))
            for foot in (left, right):
                base = (foot[0], -0.35, foot[2])
                cylinder_between(base, foot, 0.075, (0.42, 0.48, 0.50), 7)
            cylinder_between((left[0], left[1]-0.15, left[2]), (right[0], right[1]-0.15, right[2]), 0.055, (0.50,0.55,0.58), 7)
    # Cross ties
    for i in range(0, TRACK_STEPS, 4):
        t = 2*math.pi*i/TRACK_STEPS
        p, tangent, side, up = basis(t)
        a = add(p, mul(side, -0.72)); b = add(p, mul(side, 0.72))
        cylinder_between(a, b, 0.075, (0.30, 0.19, 0.12), 7)
    # Twin steel rails
    for offset in (-0.48, 0.48):
        for i in range(TRACK_STEPS):
            t0 = 2*math.pi*i/TRACK_STEPS
            t1 = 2*math.pi*(i+1)/TRACK_STEPS
            p0, _, s0, _ = basis(t0); p1, _, s1, _ = basis(t1)
            a = add(p0, mul(s0, offset)); b = add(p1, mul(s1, offset))
            cylinder_between(a, b, 0.105, (0.78, 0.82, 0.86), 8)


def draw_train(phase):
    for i in range(CAR_COUNT):
        t = (phase - i*CAR_SPACING) % (2*math.pi)
        p, tangent, side, up = basis(t)
        center = add(p, mul(up, 0.48))
        # Car body aligned to tangent and local up/side basis
        glPushMatrix()
        glTranslatef(*center)
        matrix = [tangent[0], tangent[1], tangent[2], 0,
                  up[0], up[1], up[2], 0,
                  side[0], side[1], side[2], 0,
                  0,0,0,1]
        glMultMatrixf(matrix)
        body_color = (0.88, 0.16, 0.10) if i == 0 else (0.95, 0.48, 0.08)
        cube((0,0,0), (1.45,0.62,0.92), body_color)
        cube((0,0.42,0), (0.92,0.22,0.72), (0.12,0.20,0.28))
        # bright safety bar
        cube((0,0.58,0), (0.78,0.07,0.76), (0.92,0.92,0.88))
        glPopMatrix()
        # wheel hubs beneath each car
        for s in (-0.42, 0.42):
            wheel = add(center, add(mul(side, s), mul(up, -0.34)))
            sphere(wheel, 0.15, (0.08,0.09,0.11), 10, 8)


def draw_scenery():
    # Stylized low-poly trees around the ride perimeter
    for i in range(24):
        a = 2*math.pi*i/24 + 0.13
        x, z = 15.8*math.cos(a), 12.0*math.sin(a)
        cylinder_between((x,-0.35,z),(x,1.05,z),0.16,(0.28,0.16,0.09),8)
        sphere((x,1.55,z),0.85,(0.08,0.32,0.20),12,9)
        sphere((x+0.25,1.95,z),0.52,(0.10,0.40,0.24),10,8)


def draw_axes_lights():
    glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_POSITION, (8.0, 16.0, 10.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.95, 0.95, 0.90, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.30, 0.30, 0.34, 1.0))
    glEnable(GL_DEPTH_TEST)


def set_camera(phase):
    if ride_camera:
        p, tangent, side, up = basis(phase)
        eye = add(p, add(mul(up, 1.35), mul(tangent, -1.4)))
        target = add(p, mul(tangent, 4.5))
        gluLookAt(*eye, *target, *up)
    else:
        yaw, pitch = math.radians(camera_yaw), math.radians(camera_pitch)
        target = (0.0, 1.0, 0.0)
        eye = (camera_distance*math.cos(pitch)*math.sin(yaw),
               target[1]+camera_distance*math.sin(pitch),
               camera_distance*math.cos(pitch)*math.cos(yaw))
        gluLookAt(*eye, *target, 0,1,0)


def draw_hud(window, phase):
    if not show_hud: return
    # Native window title works as a compact live HUD on macOS and Windows.
    mode = "ON-RIDE CAMERA" if ride_camera else "ORBIT CAMERA"
    state = "PAUSED" if paused else "RUNNING"
    glfw.set_window_title(window, f"COASTER 3D  |  {state}  |  {mode}  |  Speed {speed:.2f}  |  Drag: orbit  Scroll: zoom  Space: pause")


def key_callback(window, key, scancode, action, mods):
    global paused, speed, show_supports, show_hud, camera_yaw, camera_pitch, camera_distance, ride_camera
    if action not in (glfw.PRESS, glfw.REPEAT): return
    if key == glfw.KEY_ESCAPE: glfw.set_window_should_close(window, True)
    elif key == glfw.KEY_SPACE: paused = not paused
    elif key in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD): speed = min(0.30, speed+0.01)
    elif key in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT): speed = max(0.01, speed-0.01)
    elif key == glfw.KEY_R:
        camera_yaw, camera_pitch, camera_distance = 38.0, 24.0, 25.0
    elif key == glfw.KEY_S: show_supports = not show_supports
    elif key == glfw.KEY_H: show_hud = not show_hud
    elif key == glfw.KEY_C: ride_camera = not ride_camera
    elif key == glfw.KEY_LEFT: camera_yaw -= 4
    elif key == glfw.KEY_RIGHT: camera_yaw += 4
    elif key == glfw.KEY_UP: camera_pitch = clamp(camera_pitch+3, -5, 75)
    elif key == glfw.KEY_DOWN: camera_pitch = clamp(camera_pitch-3, -5, 75)


def mouse_button_callback(window, button, action, mods):
    global mouse_down, last_mouse
    if button == glfw.MOUSE_BUTTON_LEFT:
        mouse_down = action == glfw.PRESS
        last_mouse = glfw.get_cursor_pos(window) if mouse_down else None


def cursor_callback(window, xpos, ypos):
    global last_mouse, camera_yaw, camera_pitch
    if mouse_down and last_mouse and not ride_camera:
        dx, dy = xpos-last_mouse[0], ypos-last_mouse[1]
        camera_yaw += dx*0.35
        camera_pitch = clamp(camera_pitch-dy*0.25, -5, 75)
    last_mouse = (xpos, ypos)


def scroll_callback(window, xoffset, yoffset):
    global camera_distance
    if not ride_camera: camera_distance = clamp(camera_distance-yoffset*1.2, 12, 45)


def main():
    global WIDTH, HEIGHT
    if not glfw.init():
        print("Could not initialize GLFW. Check that you are running this on your Mac desktop, not in a headless terminal.")
        return 1
    # Request a macOS-compatible legacy OpenGL context.
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.DEPTH_BITS, 24)
    window = glfw.create_window(WIDTH, HEIGHT, "COASTER 3D | Initializing...", None, None)
    if not window:
        glfw.terminate(); print("Could not create an OpenGL window. Try updating macOS and closing other 3D apps.")
        return 1
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glEnable(GL_DEPTH_TEST); glEnable(GL_NORMALIZE); glShadeModel(GL_SMOOTH)
    glClearColor(0.025, 0.045, 0.085, 1.0)
    draw_axes_lights()
    phase = 0.0
    previous = time.perf_counter()
    while not glfw.window_should_close(window):
        now = time.perf_counter(); dt = min(now-previous, 0.05); previous = now
        if not paused: phase = (phase + speed*dt*8.0) % (2*math.pi)
        fbw, fbh = glfw.get_framebuffer_size(window)
        WIDTH, HEIGHT = max(fbw,1), max(fbh,1)
        glViewport(0,0,WIDTH,HEIGHT)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(48.0, WIDTH/float(HEIGHT), 0.1, 150.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity(); set_camera(phase)
        draw_ground(); draw_scenery(); draw_track(); draw_train(phase)
        glDisable(GL_LIGHTING)
        draw_hud(window, phase)
        glfw.swap_buffers(window); glfw.poll_events()
    glfw.terminate()
    return 0

if __name__ == "__main__":
    sys.exit(main())
