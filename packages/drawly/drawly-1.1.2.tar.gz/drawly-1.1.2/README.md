# Drawly

A simple Python drawing package designed for educational use at Utah State University in CS 1400 - Introduction to Computer Science. Drawly provides an easy-to-use API for creating graphical applications and learning fundamental programming concepts through visual programming.

Drawly offers a gentle introduction to:

- Function calls and parameters
- Control structures (loops, conditionals)
- User input and output
- Basic geometry and mathematics
- Event-driven programming concepts

Drawly is designed to help students learn programming concepts through visual feedback:

1. **Immediate Results:** Students see their code's effects instantly
2. **Mathematical Concepts:** Coordinates, angles, and geometry become tangible
3. **Problem Solving:** Students can create visual solutions to programming challenges
4. **Creativity:** Encourages experimentation and artistic expression through code
5. **Debugging:** Visual output makes it easier to understand program flow

Drawly abstracts away the complexity of graphics programming while providing immediate visual feedback, making it ideal for students who are new to programming. By introducing core programming concepts through a simplified interface, Drawly prepares students for a smooth transition to more advanced programming with Pygame later in the semester.

## Support

For questions or issues related to CS1400 at Utah State University, please contact your instructor or teaching assistant.

### Installation

Drawly requires Python 3.10 or higher and depends on Pygame for graphics rendering.

```bash
pip install drawly
```

**Note:** Pygame will be automatically installed as a dependency when you install Drawly.

### Quick Start

```python
import drawly

# Initialize the drawing window with a title and a light blue background
drawly.start("My First Drawing", background="light blue")
drawly.set_speed(6)

# Some circles
drawly.set_color("green")
drawly.circle(200, 200, 50)
drawly.draw()

drawly.set_color("red")
drawly.circle(400, 200, 75)
drawly.draw()

# A triangle
drawly.set_color("yellow")
drawly.polygon_begin()
drawly.add_poly_point(300, 240)
drawly.add_poly_point(250, 340)
drawly.add_poly_point(350, 340)
drawly.polygon_end()
drawly.draw()

# A rectangle
drawly.set_color("orange")
drawly.rectangle(180, 375, 250, 65)
drawly.draw()

# And some text
drawly.set_color("darkblue")
drawly.text(150, 60, "Hello from Drawly!", 30)
drawly.draw()

# Keep the window open
drawly.done()
```

## Core Features

### Window Management

- Create customizable drawing windows
- Set background colors
- Optional terminal area for text input/output

### Drawing Primitives

- **Circles:** Filled or outlined circles
- **Rectangles:** With optional rotation and rotation points
- **Lines:** Between two points or as vectors with angle/length
- **Polygons:** Custom shapes built point by point
- **Ellipses and Arcs:** Curved shapes
- **Text:** Customizable font, size, and color

### Interactive Features

- Terminal input/output within the drawing window
- Speed control for animation effects
- Color management
- Background drawing for persistent elements


## API Reference

### Window Management
- `start(title, dimensions, background, terminal, terminal_lines, terminal_line_height)` - Initialize the drawing window
- `done()` - Keep the window open until user closes it

### Drawing Control
- `set_speed(speed)` - Set drawing speed (1-10)
- `set_color(color)` - Set drawing color
- `draw()` - Display all shapes since last draw
- `redraw()` - Clear screen and redraw everything

### Shapes
- `circle(x, y, radius, stroke)` - Draw a circle
- `rectdegrees(x, y, width, height, stroke, rotation_angle, rotation_point)` - Draw a rectangle
- `line(x1, y1, x2, y2, stroke)` - Draw a line between points
- `vector(x, y, length, angle, stroke)` - Draw a line with angle
- `ellipse(x, y, width, height, stroke)` - Draw an ellipse
- `arc(x, y, width, height, start_angle, end_angle, stroke)` - Draw an arc

### Polygons
- `polygon_begin(stroke)` - Start creating a polygon
- `add_poly_point(x, y)` - Add a point to the polygon
- `polygon_end()` - Complete and draw the polygon

### Text and Terminal
- `text(x, y, text, size, font)` - Draw text
- `terminal_output(*message)` - Display message in terminal
- `terminal_input(*prompt)` - Get user input from terminal
- `terminal_clear()` - Clear terminal area

### Background Drawing
- `background_begin()` - Start drawing background elements
- `background_end()` - End background drawing


## Comprehensive Example

Here's a larger demonstration showing more of Drawly's capabilities:

```python
from drawly import *

# Initialize with terminal enabled
start("Drawly Demo", background="lightblue", terminal=True)
set_speed(5)  # Medium drawing speed

# Welcome message
terminal_output("A Drawly Demo")

# Draw some circles
circle(200, 200, 50)  # Filled circle
set_color("red")
circle(400, 200, 75)
draw()

# Draw outlined circles
set_color("black")
circle(400, 200, 75, 5)  # stroke=5 for outline
draw()

# Draw rectangles
set_color("blue")
rectangle(100, 100, 150, 100)  # x, y, width, height
draw()

# Draw rotated rectangle
set_color("green")
rectangle(500, 100, 120, 80, stroke=3,
         rotation_angle=45, rotation_point=RotationPoint.CENTER)
draw()

# Get user input and draw based on it
count = int(terminal_input("How many circles? "))
for i in range(count):
    set_color("purple")
    circle(100 + i * 50, 400, 25)
    draw()

# Draw lines
set_color("orange")
line(50, 50, 200, 150, 3)  # Thick line
draw()

# Draw vectors (lines with angle)
set_color("brown")
vector(300, 300, 100, 45)  # length=100, angle=45 degrees
draw()

# Create a polygon
polygon_begin()
add_poly_point(600, 100)
add_poly_point(700, 200)
add_poly_point(650, 300)
add_poly_point(550, 250)
polygon_end()
draw()

# Draw text
set_color("darkblue")
text(50, 500, "Hello from Drawly!", 30)
draw()

# Get user input for custom text
message = terminal_input("Enter a message: ")
set_color("red")
text(50, 550, message, 25)
draw()

# Keep window open
done()
```

## Requirements

- Python 3.10 or higher
- Pygame 2.5 or higher (automatically installed)

## License

MIT License - See LICENSE file for details.
