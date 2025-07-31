from src import drawly

# This function always needs to be called first
drawly.start("My Cool Drawing", background="grey", terminal=True)

# Optionally set the speed (0-10) at which drawing happens
# Default is 5 if you do not call this
drawly.set_speed(6)

# print a terminal message
drawly.terminal_output("Welcome")

# Draw a circle
drawly.circle(300, 500, 100)
drawly.set_color("red")
drawly.circle(800, 300, 150)
drawly.redraw() # Call this to actually draw everything since the last time it was called

# Draw an unfilled circle
drawly.set_color("black")
drawly.circle(800, 300, 150, 10)
drawly.redraw()

# Draw a filled rectangle
drawly.set_color("blue")
drawly.rectangle(300, 400, 200, 100)
drawly.draw()

# Draw a rectangle outline
drawly.set_color("brown")
drawly.rectangle(1000, 200, 250, 75, stroke=5)
drawly.draw()

# Get input from the user
result = drawly.terminal_input("\tEnter a number: ")
for i in range(int(result)):
    drawly.set_color("red")
    drawly.circle(100 + 100 * i, 400, 100, 5)
    drawly.draw()

# Draw a rotated rectangle with outline
# Hover over RotationPoint to see options. Default is CENTER
drawly.set_color("brown")
drawly.rectangle(1000, 600, 250, 75, stroke=5, rotation_angle=45, rotation_point=drawly.RotationPoint.TOP_LEFT)
drawly.draw()

# Draw a line between two points
drawly.set_color("orange")
drawly.line(200, 200, 500, 450)
drawly.line(300, 300, 600, 550, 5) # last optional parameter is line thickness
drawly.draw()

# Draw a word given by user
word = drawly.terminal_input("Enter a word: ")
drawly.set_color("green")
drawly.text(400, 400, word, 50)
drawly.draw()

# Draw a vector. This is a line with a starting point, length, and angle
drawly.vector(1200, 50, 200, -120)
drawly.set_color("pink")
drawly.vector(700, 300, 250, -120, 10) # last optional parameter is stroke thickness
drawly.redraw()

# Draw a polygon
drawly.polygon_begin() # no parameter is fill. Add a number for a stroke size
drawly.add_poly_point(10, 10)
drawly.add_poly_point(150, 150)
drawly.add_poly_point(150, 80)
drawly.polygon_end()
drawly.draw()

# Draw an ellipse. Define a rectangle the elipse will fit in
drawly.set_color("purple")
drawly.ellipse(200, 200, 300, 100, 20) # last parameter is optional stroke size. filled otherwise
drawly.draw()

# Draw an arc. Define a rectangle that an ellipse will fit inside
# The start and end are the degree points between which the arc will be drawn
drawly.arc(500, 500, 150, 200, 45, 135, 5)
drawly.draw()

# Write some text. Position is the top left corner of text
drawly.set_color("red")
drawly.text(0, 0, "Hello there")
drawly.text(100, 100, "Goodbye", 50) # optional font size
drawly.draw()

drawly.done()
