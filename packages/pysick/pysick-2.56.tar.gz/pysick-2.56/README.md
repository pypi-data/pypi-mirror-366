# PySick - Getting Started

PySick is a simple graphics library built on top of Tkinter.  
It makes creating shapes, windows, input handling, and basic games super easy!

---

## Getting Started

Here’s how to open a window, draw a rectangle, and start the main loop.

```python
import pysick

# Create a window (800 x 600 pixels)
pysick.ingine.init(800, 600)

# Create a rectangle shape
rect = pysick.graphics.Rect(
    x=100,
    y=100,
    width=200,
    height=100,
    fill=(255, 0, 0)  # Red color
)

# Fill the entire screen with dark gray
pysick.graphics.fill_screen((30, 30, 30))

# Draw the rectangle shape
pysick.graphics.draw(rect)

# Start the main loop
pysick.ingine.run()
```

---

## Running Without mainloop()

PySick can also work in a `while` loop for more game-like programs:

```python
import pysick

pysick.ingine.init(800, 600)

rect = pysick.graphics.Rect(100, 100, 200, 100, fill=(0, 255, 0))

while not pysick.QUIT:
    pysick.graphics.fill_screen((0, 0, 0))
    pysick.graphics.draw(rect)
    pysick.ingine.slap()
```

---

## Colors

You can use:

- Named colors, like `"red"`
- RGB tuples, like `(255, 0, 0)`
- RGBA tuples (alpha is ignored in Tkinter)

Example:

```python
rect = pysick.graphics.Rect(
    x=50,
    y=50,
    width=100,
    height=50,
    fill="blue"
)
```

Or with RGB:

```python
rect = pysick.graphics.Rect(
    x=50,
    y=50,
    width=100,
    height=50,
    fill=(0, 128, 255)
)
```

---

## Shapes

PySick supports:

- Rectangle
- Oval
- Circle
- Line
- Polygon
- Text

Example:

```python
oval = pysick.graphics.Oval(200, 150, 80, 40, fill="purple")
pysick.graphics.draw(oval)

line = pysick.graphics.Line(50, 50, 200, 200, fill=(255, 255, 0))
pysick.graphics.draw(line)

polygon_points = [(50, 50), (100, 150), (150, 50)]
pysick.graphics.draw_polygon(polygon_points, fill=(0, 255, 255))

text = "Hello, PySick!"
pysick.graphics.draw_text(300, 300, text, fill=(255, 255, 255))
```

---

## Input Handling

### Keyboard

```python
pysick.keys.init()

if pysick.keys.is_pressed(pysick.keys.KEY_LEFT):
    print("Left arrow is held!")

if pysick.keys.was_pressed(pysick.keys.KEY_SPACE):
    print("Space was pressed!")
```

---

### Mouse

```python
pysick.mouse.init()

if pysick.mouse.is_pressed(pysick.mouse.LEFT):
    print("Left mouse button pressed.")

x, y = pysick.mouse.get_pos()
print(f"Mouse is at {x},{y}")
```

---

## GUI Widgets

```python
pysick.gui.add_label("Hello!", 100, 100)
pysick.gui.add_button("Click Me", 200, 200, lambda: print("Clicked!"))
entry = pysick.gui.add_entry(300, 300)

# Checkbuttons and radiobuttons:
check, var = pysick.gui.add_checkbutton("Enable", 400, 400)
radio_var = tk.StringVar()
radio = pysick.gui.add_radiobutton("Option A", 500, 500, radio_var, value="A")
```

---

## Videos and Images

Show an image:

```python
pysick.image.show(pysick.ingine, "my_picture.png")
```

Play a video:

```python
pysick.image.play("my_video.mp4")
```

---

## Ticking

Replace time.sleep() with pysick’s tick helper:

```python
pysick.tick(16)   # wait ~16ms
```

---

## QUIT Flag

Inside your while-loop game:

```python
while not pysick.QUIT:
    # game logic
    pysick.ingine.slap()
```

---
##  Entity & Player System (`ep.py`)

PySick includes a powerful, modular Entity-Player system (`ep.py`) that allows you to create full interactive characters and shapes using just 1 to 10 lines of code. It's ideal for beginners, prototypes, or even advanced game logic.

###  Quick Example

```python
import pysick
from pysick.ep import epBasePlayerController

pysick.ingine.init(800, 600)
player = epBasePlayerController()
player.change_sprite(100, 100, 50, 50)
player.change_speed(5)

player.loop(30)  # runs the movement and draw loop
```

---

###  Available Classes

####  `epBasePlayerController`
- 2D rectangular player
- Arrow key (or WASD) movement
- Infinite loop built-in
- Easy color, speed, and position control

####  `epAdvancedPlayerController`
- Adds physics-like gravity, jumping, velocity
- Jumping only when on ground
- Movement clamped to screen size
- Customizable key mappings

####  `epBaseTwoPlayerController`
- 2 players, independent controls
- Draws both player sprites
- Designed for local multiplayer

####  `epBaseTwoPlayerShooter`
- Two-player shooting battle
- Shoots bullets, checks collision, tracks score
- Auto updates GUI labels for score

####  `epBaseSpaceShooter`
- Classic arcade-style top-down shooter
- Bullets, enemy spawning, collisions
- Auto score tracking and Game Over message

---

###  Drawing System

####  Base Shape Classes
Each has a `.draw()` method that you call per frame:

- `epBaseRect` (internal)
- `epBaseOval`
- `epBaseCircle`
- `epBasePolygon`
- `epBaseArc`
- `epBaseLine`
- `epBaseText`

You can use them as reusable objects, such as:

```python
arc = epBaseArc(200, 100, 80, 80, start=45, extent=270)
arc.set_color((255, 0, 255))
arc.draw()
```



###  `epBaseTerrain` - 2D Platform Terrain

A gravity-based terrain system in 2D using the `graphics` system.

```python
from pysick.ep import epBaseTerrain

terrain = epBaseTerrain()
terrain.loop()
```

- Auto player movement (WASD + Space for jump)
- Rectangular platforms
- Built-in collision
- Simple gravity + jump physics

---

###  `epAdvancedCube` and `epAdvancedCuboid`

Draws a cube or cuboid in 3D using OpenGL:

```python
from pysick.ep import epAdvancedCube, epAdvancedCuboid

cube = epAdvancedCube(x=0, y=0, z=0, size=5, color=(1, 1, 1))
cuboid = epAdvancedCuboid(x=10, y=5, z=10, width=5, height=10, depth=3)

cube.draw()
cuboid.draw()
```

- `color`: values between 0.0 - 1.0 (RGB)
- `rotation`: degrees (x, y, z)

---

###  `epAdvancedTerrain` - 3D Block Terrain

```python
from pysick.ep import epAdvancedTerrain

terrain = epAdvancedTerrain()
terrain.loop()
```

- Random block heights
- 3D cube-style terrain
- Gravity-enabled player physics

---

###  Enabling OpenGL

To enable advanced OpenGL rendering:

```python
from pysick.ep import epEnable

epEnable(epAdvanced)
```

To disable:

```python
epDisable(epAdvanced)
```

---

###  `epAdvancedWindowInit` & `epAdvancedRun`

For running OpenGL-based 3D games:

```python
from pysick.ep import epAdvancedWindowInit, epAdvancedRun
from pysick.OpenGL.GL import *
from pysick.OpenGL.GLUT import *
epAdvancedWindowInit(800, 600)

def render_loop():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    terrain.loop()  # or your custom draw code
    glutSwapBuffers()

epAdvancedRun(render_loop)
```

- Uses GLUT backend (`PyOpenGL`)
- Handles depth and perspective
- Calls your loop as display and idle function



---

###  Full Integration Example

```python
from pysick.ep import *
from OpenGL.GL import *
from OpenGL.GLUT import *

terrain = epAdvancedTerrain()
epEnable(epAdvanced)
epAdvancedWindowInit()

def main_loop():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    terrain.loop()
    glutSwapBuffers()

epAdvancedRun(main_loop)
```



---

>  This system brings 2D & 3D development to PySick with physics, terrain, camera, OpenGL, and ECS logic.
```


---

###  Main Game Loop

All `ep` controllers come with a built-in infinite loop, but you can also run PySick in your own while-loop:

```python
while not pysick.QUIT:
    pysick.graphics.fill_screen((20, 20, 20))
    player.update()  # call custom or controller update
    pysick.ingine.slap()
    pysick.clock.tick(30)
```

---

> To stop a loop or quit the game, use `pysick.ingine.quit()` or handle `pysick.QUIT`.

---

###  Summary

| Class                        | Purpose                          | Key Features                     |
|-----------------------------|----------------------------------|----------------------------------|
| `epBasePlayerController`     | Basic player                     | 2D movement                      |
| `epAdvancedPlayerController` | Physics-based player             | Gravity, jump, ground logic      |
| `epBaseTwoPlayerController`  | 2-player local control           | Custom controls                  |
| `epBaseTwoPlayerShooter`     | 2-player shooter                 | Bullets, scoring, hit detection  |
| `epBaseSpaceShooter`         | Space shooter                    | Enemies, bullets, collisions     |
| `epBaseArc`, `Circle`, etc.  | Reusable shape objects           | Clean `.draw()` usage            |
| `epAdvancedCube`             | Experimental 3D cube             | Rotation, projection             |

Explore the `pysick.ep` module to accelerate your game development with powerful, beginner-friendly systems!
At core, ep provides you easy functions of 50 lines of code to 2 - 5 lines of code, how simple is it?

---
## About

```python
pysick.about()
```

Displays PySick version info.

---

That’s it — you’re ready to build cool stuff!


