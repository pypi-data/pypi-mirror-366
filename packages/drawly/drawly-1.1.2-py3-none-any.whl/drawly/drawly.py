import pygame
import re
import sys
from enum import Enum
from functools import partial
from math import cos, sin, radians


__version__ = "1.1.2"
CLOCK_TICK = 30


def print_drawly_fonts():
    """
    Utility to get a list of possible fonts that can be used
    """
    print("Fonts Available to Use in Your Program")
    print("Note: This lists fonts on the system, which may not be available on all systems")
    print(pygame.font.get_fonts())


class Data:
    """ A global object to hold all state data
    """
    def __init__(self):
        self.ms = 1000
        self.color = "black"
        self.text_color = "black"
        self.screen = None
        self.background = "white"
        self.poly_width = 0
        self.poly_points = []
        self.draw_list = []
        self.background_list = []
        self.draw_background = False
        self.dimensions = None
        self.terminal = None
        self.terminal_lines = None
        self.terminal_line_height = None
        self.terminal_msg = []
        self.clock = pygame.time.Clock()
        self.first_draw = True # don't delay on first time drawing


# Global object to store state
data = Data()


class RotationPoint(Enum):
    """
    Rotation points specifies the point about which an object will be rotated

    Attributes:
        BOTTOM_LEFT - Rotate about the bottom left corner
        BOTTOM_RIGHT - Rotate about the bottom right corner
        TOP_LEFT - Rotate about the top right corner
        TOP_RIGHT - Rotate about the top left corner
        CENTER - Rotate about the center
    """
    BOTTOM_LEFT = 0
    BOTTOM_RIGHT = 1
    TOP_RIGHT = 2
    TOP_LEFT = 3
    CENTER = 4


def start(title="Welcome to Drawly", dimensions=(1280, 720), background="white", terminal=False, terminal_lines=8, terminal_line_height=25):
    """
    Create the graphical Drawly window.  This function must be called prior to any other Drawly functions.

    The 'dimensions' argument defines the size of the drawing canvas.
    When the terminal is enabled, its size is ADDED TO the overall dimensions of the screen.
    In other words, the Drawly window will be larger than your specified dimensions if a terminal is present.

    Args:
        title (str): (Optional) Title of the Drawly window
        dimensions ((int, int)): (Optional) Tuple of the dimensions of the window. 1280x720 default
        background (str): (Optional) Background color of the window. White by default
        terminal (bool): (Optional) Determins if the terminal window should be shown or not. False by default
        terminal_lines (int): (Optional) Number of lines for the terminal for input and output at the bottom of the window. 8 by default
        terminal_line_height (int): (Optional) Height of a single line in the terminal. 25 by default
    """
    data.terminal = terminal
    if not terminal:
        data.terminal_lines = 0
    else:
        data.terminal_lines = terminal_lines
    data.terminal_line_height = terminal_line_height
    data.dimensions = (dimensions[0], dimensions[1] + data.terminal_lines * data.terminal_line_height)
    data.background = background
    pygame.init()
    data.screen = pygame.display.set_mode(data.dimensions)
    data.screen.fill(background)
    pygame.display.set_caption(title)
    draw_terminal()


def set_speed(speed):
    """
    Set the speed for drawing. Each time draw() or redraw() is called there will be a delay based on
        the speed value.  1 is slow, approximately 1 frame every 2 seconds.
        10 is approximately 30 frames per second
    Args:
        speed (int): Rate at which drawings are rendered on the screen
    """
    if speed < 1:
        speed = 1
    elif speed > 10:
        speed = 10
    data.ms = 33 + 197 * (10 - speed)


def set_color(new_color):
    """
    Change the color that will be used in the next drawing operations.

    An exception is raised when an invalid color is provided.

    Args:
        new_color (str): Color to use
    """
    if new_color in pygame.colordict.THECOLORS or re.match(r'^#[0-9A-Fa-f]{6}$', new_color):
        data.color = new_color
    else:
        raise Exception(f"'{new_color}' is not a valid Drawly color")


def draw():
    """
    Draw all items that have been created since the last call to draw()
    """
    _do_draw(False)


def redraw():
    """
    Erase all items on the canvas, then draw new items that have been created since the last call to draw()
    """
    _do_draw(True)


def _do_draw(refresh):
    """
    Helper function used by draw() and redraw()
    """
    # See if the user closed the window
    for event in pygame.event.get():
        _check_exit_event(event)

    if not data.first_draw: # Don't pause on first draw
        pygame.time.wait(data.ms)
    else:
        data.first_draw = False

    # Clear the screen and draw the background on a redraw
    if refresh:
        data.screen.fill(data.background)
        for i in data.background_list:
            i()

    # Draw the current list of items since last draw
    for i in data.draw_list:
        i()
    data.draw_list.clear()

    # Draw the terminal on top of the rest of the screen
    draw_terminal()


def draw_terminal():
    """
    Render the terminal at the bottom of the window (if it's enabled).

    This function always flips the Pygame buffer, regardless of whether the terminal is active.
    """
    if data.terminal:
        pygame.draw.rect(data.screen, "black",
                         pygame.Rect(0, data.dimensions[1] - data.terminal_lines * data.terminal_line_height,
                                     data.dimensions[0], data.terminal_lines * data.terminal_line_height))

        for i in range(data.terminal_lines):
            if i < len(data.terminal_msg):
                text_font = pygame.font.SysFont("courier", data.terminal_line_height - 4).render(data.terminal_msg[i],
                                                                                                 True, "white")
                data.screen.blit(text_font, (10, data.dimensions[1] - (1 + i) * data.terminal_line_height))

    # Call this here because draw_terminal() is always called last
    pygame.display.flip()


def circle(x_pos, y_pos, radius, stroke=0):
    """
    Creates a circle to be drawn on the screen. The circle will appear the next time draw() is called.

    Args:
        x_pos (int): X-coordinate of the center of the circle
        y_pos (int): Y-coordinate of the center of the circle
        radius (int): Radius of the circle
        stroke (int): (Optional) Default is 0, which is a filled circle. Otherwise is the size of outline stroke
    """
    add_draw_item(partial(pygame.draw.circle, data.screen, data.color, [x_pos, y_pos], radius, width=stroke))


#    I borrowed some of this code from online and will credit if I ever find the place again. :)
#    - rotation_degrees: in degree
#    - rotation_offset_center: moving the center of the rotation: (-100,0) will turn the rectangle around a point 100 above center of the rectangle,
#                                         if (0,0) the rotation is at the center of the rectangle
#    - nRenderRatio: set 1 for no antialising, 2/4/8 for better aliasing


def rectangle(x_pos, y_pos, width, height, stroke=0, rotation_degrees=0, rotation_point=RotationPoint.CENTER):
    """
    Draws a rectangle on the screen with an optional rotation angle and rotation point.

    Args:
        x_pos (int): X-coordinate of the top left of the unrotated rectangle
        y_pos (int): Y-coordinate of the top left of the unrotated rectangle
        width (int): Width of the unrotated rectangle (x-direction)
        height (int): Height of the unrotated rectangle (y-direction)
        stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
        rotation_degrees (int): Degrees to rotate the rectangle. Default is 0
        rotation_point: (RotationPoint): Point to rotate the rectangle about
    """
    nRenderRatio = 8

    # the rotation point is relative to the center of the rectangle
    if rotation_point == RotationPoint.CENTER:
        rotation_offset_center = (0, 0)
    elif rotation_point == RotationPoint.BOTTOM_LEFT:
        rotation_offset_center = (-width // 2, height // 2)
    elif rotation_point == RotationPoint.BOTTOM_RIGHT:
        rotation_offset_center = (width // 2, height // 2)
    elif rotation_point == RotationPoint.TOP_RIGHT:
        rotation_offset_center = (width // 2, -height // 2)
    elif rotation_point == RotationPoint.TOP_LEFT:
        rotation_offset_center = (-width // 2, -height // 2)
    else:  # manually enter a point as a tuple
        x_pt, y_pt = rotation_point
        rotation_offset_center = (x_pt - x_pos - width // 2, y_pt - y_pos - height // 2)

    sw = width + abs(rotation_offset_center[0]) * 2
    sh = height + abs(rotation_offset_center[1]) * 2

    surfcenterx = sw // 2
    surfcentery = sh // 2
    s = pygame.Surface((sw * nRenderRatio, sh * nRenderRatio))
    s = s.convert_alpha()
    s.fill((0, 0, 0, 0))

    rw2 = width // 2  # halfwidth of rectangle
    rh2 = height // 2

    pygame.draw.rect(s, data.color, ((surfcenterx - rw2 - rotation_offset_center[0]) * nRenderRatio,
                                     (surfcentery - rh2 - rotation_offset_center[1]) * nRenderRatio,
                                     width * nRenderRatio,
                                     height * nRenderRatio), stroke * nRenderRatio)
    s = pygame.transform.rotate(s, rotation_degrees)
    if nRenderRatio != 1: s = pygame.transform.smoothscale(s, (
        s.get_width() // nRenderRatio, s.get_height() // nRenderRatio))
    incfromrotw = (s.get_width() - sw) // 2
    incfromroth = (s.get_height() - sh) // 2
    add_draw_item(partial(data.screen.blit, s, (x_pos - surfcenterx + rotation_offset_center[0] + rw2 - incfromrotw,
                                                y_pos - surfcentery + rotation_offset_center[1] + rh2 - incfromroth)))


def vector(x_pos, y_pos, length, degrees=0, stroke=1):
    """
    Draws a line based on a starting point, length, angle, and stroke size (width of line)

    Args:
        x_pos (int): X-coordinate of the start of the line
        y_pos (int): Y-coordinate of the start of the line
        length (int): Length of the line to draw
        degrees(int): (Optional) Angle of line. 0 degrees is horizontal to the right. Default is 0
        stroke (int): (Optional) Width of the line drawn. Default is 1
    """
    end_x = x_pos + length * cos(radians(-degrees))  # use negative to match with unit circle
    end_y = y_pos + length * sin(radians(-degrees))
    add_draw_item(partial(pygame.draw.line, data.screen, data.color, (x_pos, y_pos), (end_x, end_y), stroke))


def line(x_pos1, y_pos1, x_pos2, y_pos2, stroke=1):
    """
    Draws a line based on a starting point, end point, and stroke size (width of line)

    Args:
        x_pos1 (int): X-coordinate of the start of the line
        y_pos1 (int): Y-coordinate of the start of the line
        x_pos2(int): X-coordinate of the end of the line
        y_pos2 (int): Y-coordinate of the end of the line
        stroke (int): (Optional) Width of the line drawn. Default is 1
    """
    add_draw_item(partial(pygame.draw.line, data.screen, data.color, (x_pos1, y_pos1), (x_pos2, y_pos2), stroke))


def polygon_begin(stroke=0):
    """
    Call to begin creating a polygon. Call add_poly_points() to create the polygon point-by-point.

    Args:
        stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
    """
    data.poly_width = stroke
    data.poly_points.clear()


def add_poly_point(x_pos, y_pos):
    """
    Add a point to the current polygon.
    This function must be called AFTER polygon_begin() and BEFORE polygon_end()

    Args:
        x_pos (int): X-position of the point to add
        y_pos (int): Y-position of the point to add
    """
    data.poly_points.append([x_pos, y_pos])


def polygon_end():
    """
    Call to finalize the current polygon.
    """
    add_draw_item(partial(pygame.draw.polygon, data.screen, data.color, data.poly_points.copy(), data.poly_width))


# Define a rectangle that an ellipse will fit in.
def ellipse(x_pos, y_pos, width, height, stroke=0):
    """
   Draws an ellipse inside of the defined rectangle

   Args:
        x_pos (int): X-coordinate of the top left
        y_pos (int): Y-coordinate of the top left
        width (int): Width of the rectangle (x-direction)
        height (int): Height of the rectangle (y-direction)
        stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
    """
    add_draw_item(partial(pygame.draw.ellipse, data.screen, data.color, (x_pos, y_pos, width, height), stroke))


# Define a rectangle that an ellipse will fit in. Start and end are the degree points where the line will be drawn
def arc(x_pos, y_pos, width, height, start, end, stroke=1):
    """
       Draws an ellipse arc inside of the defined rectangle

       Args:
            x_pos (int): X-coordinate of the top left
            y_pos (int): Y-coordinate of the top left
            width (int): Width of the rectangle (x-direction)
            height (int): Height of the rectangle (y-direction)
            start (int): Degree point on arc to begin drawing
            end (int): Degree point on arc to end drawing
            stroke (int): 0 for a filled rectangle. > 0 is  the width of the line drawn. Default is 0.
    """
    add_draw_item(
        partial(pygame.draw.arc, data.screen, data.color, (x_pos, y_pos, width, height), radians(start), radians(end),
    stroke))


# Write some text.
def text(x_pos, y_pos, text, size=20, font="courier"):
    """
       Draws text on the screen.

       Args:
            x_pos (int): X-coordinate of the top left of the text
            y_pos (int): Y-coordinate of the top left of the text
            text (str): Text to write
            size (int): (Optional) Font size. Default is 20
    """
    text_font = pygame.font.SysFont(font, size).render(text, True, data.color)
    add_draw_item(partial(data.screen.blit, text_font, (x_pos, y_pos)))


# Call when adding items to the background image
def background_begin():
    data.draw_background = True


# Call when done adding items to the background image
def background_end():
    data.draw_background = False


# Add a drawing function to the appropriate list
def add_draw_item(draw_function):
    if data.draw_background:
        data.background_list.append(draw_function)
    data.draw_list.append(draw_function)


def terminal_output(*messages):
    """
    Prints a single line of output in the terminal.  An exception is raised if the terminal was not initialized.

    Args:
        (Optional) messages: Items to print.
                             With no parameters a blank like is printed.
                             A space is inserted between multiple parameters.
    """
    if not data.terminal:
        raise Exception("Drawly: Terminal is not enabled")

    tmp_msg = ""
    for msg in messages:
        if tmp_msg != "":
            tmp_msg += " "
        tmp_msg += str(msg).replace("\t", "    ")

    data.terminal_msg.insert(0, tmp_msg)
    draw_terminal()


# Display the prompt and wait for the user to enter a string and hit return
# Terminal variable in Data object must be true for this to work
def terminal_input(*prompts):
    """
    Prompts user for a line of input in the terminal.
    The event loop is pumped while waiting for the user to press Enter.
    An exception is raised if the terminal was not initialized.

    Args:
        (Optional) prompts: Items to print before prompting for user input.
                            With no parameters a blank like is printed.
                            A space is inserted between multiple parameters.
    """
    if not data.terminal:
        raise Exception("Drawly: Terminal is not enabled")

    data.terminal_msg.insert(0, "")
    draw()
    tmp_prompt = ""
    for prompt in prompts:
        if tmp_prompt != "":
            tmp_prompt += " "
        tmp_prompt += str(prompt).replace("\t", "    ")

    msg = ""
    cursor_cnt = 0
    cursor = "|"
    active = True
    while active:
        cursor_cnt += 1
        for event in pygame.event.get():
            _check_exit_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    if len(msg) > 0:
                        msg = msg[:-1]
                else:
                    msg += event.unicode

        if cursor_cnt // 10 % 2 == 0:
            cursor = ""
        else:
            cursor = "|"

        # Just drawing the line that accepts input
        pygame.draw.rect(data.screen, "black", pygame.Rect(0, data.dimensions[1] - data.terminal_line_height, data.dimensions[0], data.terminal_line_height))
        text_font = pygame.font.SysFont("courier", data.terminal_line_height - 4).render(tmp_prompt + msg + cursor, True, "white")
        data.screen.blit(text_font, (10, data.dimensions[1] - data.terminal_line_height))
        pygame.display.flip()
        data.clock.tick(CLOCK_TICK)

    data.terminal_msg[0] = tmp_prompt + msg
    data.first_draw = True  # Remove delay on next draw after input
    return msg


def terminal_clear():
    """
    Clears the terminal window
    """
    if not data.terminal:
        print("Terminal Error: Terminal is not enabled")
        return

    data.terminal_msg = []
    draw_terminal()


# Call when done so window doesn't close. Click on X to close
def done():
    """
    Invoke this function at the end of the program to keep the Drawly window open until the user closes it.
    """
    while True:
        # Keep polling until an exit event happens
        event = pygame.event.wait()  # Non-busy wait
        _check_exit_event(event)


def _check_exit_event(event):
    """
    Close the Drawly window on an appropriate event:
      * Closing the window from the window manager
      * Pressing Escape
      * Pressing Ctrl-C
    """
    close = False
    if event.type == pygame.QUIT:
        # User clicks window close button
        close = True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            # User presses the escape key
            close = True
        if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # User hits Ctrl+C
            close = True

    if close:
        pygame.quit()
        sys.exit()
