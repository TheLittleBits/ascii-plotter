import curses
from plotter import plot, round_to_decimals
import json, os
import sympy as sp
import time
from math import ceil
from decimal import Decimal
import warnings
warnings.filterwarnings("ignore")

def main(display):
    curses.set_escdelay(25)
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)
    curses.start_color()
    curses.use_default_colors()
    # Line colors:
    curses.init_pair(1, -1, -1)
    curses.init_pair(2, 2, -1)
    curses.init_pair(3, 3, -1)
    curses.init_pair(4, 4, -1)
    curses.init_pair(5, 5, -1)
    curses.init_pair(6, 6, -1)
    curses.init_pair(7, 9, -1)
    curses.init_pair(8, 10, -1)
    curses.init_pair(9, 11, -1)
    curses.init_pair(10, 12, -1)
    # Others
    curses.init_pair(12, 240, -1) # gray text
    curses.init_pair(13, 246, -1) # lighter gray text
    curses.init_pair(14, 6, 235) # axis background x
    curses.init_pair(15, 9, 235) # axis background y
    zoomdigit = 0
    precision = 1
    
    ylength = 0
    offsetx = round(display.getmaxyx()[1]/2)
    offsety = round(display.getmaxyx()[0]/2)
    zoom = Decimal(1)
    show_axis = True
    show_grid = True
    show_lines = True

    formulas = []
    notification = None

    while True:
        graph, axisx, axisy = plot(
            formulas,
            (display.getmaxyx()[1]-1, display.getmaxyx()[0]-1),
            offset = (offsetx, offsety),
            zoom=(float(zoom), float(zoom)/2),
            step=(10, 5),
            precision = precision
        )
        # Update window sizes to new axis-y charlength
        ylength = len(axisy.split("\n")[0])
        axis_x = curses.newwin(2, display.getmaxyx()[1]-ylength-1, display.getmaxyx()[0]-2, ylength+1)            
        axis_y = curses.newwin(display.getmaxyx()[0]-1, ylength+1, 0, 0)
        corner = curses.newwin(2, ylength+1, display.getmaxyx()[0]-2, 0)

        if show_grid:
            display.addstr(0, 0, "."*(display.getmaxyx()[1]*display.getmaxyx()[0]-1), curses.color_pair(12))
        else:
            display.erase()

        if show_lines:
            if 0 < offsetx < display.getmaxyx()[1]-1:
                for y in range(display.getmaxyx()[0]):
                    display.addstr(y, offsetx, "|", curses.color_pair(6))
            if 1 < offsety < display.getmaxyx()[0]:
                display.addstr(display.getmaxyx()[0]-offsety-1, 0, "-" * display.getmaxyx()[1], curses.color_pair(7))
            if 0 < offsetx < display.getmaxyx()[1]-1 and 1 < offsety < display.getmaxyx()[0]:
                display.addstr(display.getmaxyx()[0]-offsety-1, offsetx, "+", curses.color_pair(13))
        
        for dot in graph:
            display.addstr(dot[0][1], dot[0][0], dot[1], curses.color_pair(dot[2]))

        if show_axis:
            axis_x.erase()
            axis_x.bkgd(curses.color_pair(14))
            axis_x.addstr(0, 0, axisx.split("\n")[0])
            axis_x.addstr(1, 0, axisx.split("\n")[1])
            axis_y.erase()
            axis_y.bkgd(curses.color_pair(15))
            axis_y.addstr(0, 0, axisy[:((axis_y.getmaxyx()[0]*axis_y.getmaxyx()[1])-ylength-1-1)])
            display.refresh()
            axis_x.refresh()
            axis_y.refresh()
            corner.refresh()
        else:
            display.refresh()
        
        if notification != None:
            notify(display, notification)
            notification = None
            key = display.getch()
            if key == ord("q") or key == 27:
                key = None
        else:
            key = display.getch()
        
        corner.erase()

        if key == ord("l"):
            if "settings.json" in os.listdir():
                file = open("settings.json", "r")
                settings = json.load(file)
                zoom = Decimal(settings["zoom"])
                file.close()
                offsetx = settings["offsetx"]
                offsety = settings["offsety"]
                formulas = settings["formulas"]
                show_axis = settings["axis"]
                show_lines = settings["lines"]
                show_grid = settings["grid"]
                notification = ("Loaded state from file", 2)
            else:
                notification = ("No state to load", 7)
        if key == ord("s"):
            settings = {"zoom": float(zoom), "offsetx": offsetx, "offsety": offsety, "formulas": formulas, "axis": show_axis, "lines": show_lines, "grid":show_grid}
            file = open("settings.json", "w")
            json.dump(settings, file)
            file.close()
            notification = ("Saved current state.", 2)
        if key == curses.KEY_DOWN:
            offsety -= round(display.getmaxyx()[0]/16)
        if key == curses.KEY_UP:
            offsety += round(display.getmaxyx()[0]/16)
        if key == curses.KEY_RIGHT:
            offsetx += round(display.getmaxyx()[1]/16)
        if key == curses.KEY_LEFT:
            offsetx -= round(display.getmaxyx()[1]/16)
        if key == ord(";"):
            precision /= 1.5
        if key == ord("'"):
            precision *= 1.5
        if key == ord("."):
            zoom = zoomin(zoom)
        if key == ord(","):
            zoom = zoomout(zoom)
        if key == ord("r"):
            offsetx = round(display.getmaxyx()[1]/2)
            offsety = round(display.getmaxyx()[0]/2)
            zoom = Decimal(1)
        if key == ord("f"):
            formulas = request_formula(display, formulas)
        if key == ord("a"):
            show_lines = not show_lines
            if show_lines:
                notification = ("Showing axes", 2)
            else:
                notification = ("Hiding axes", 2)
        if key == ord("t"):
            show_axis = not show_axis
            if not show_axis:
                axis_y.bkgd(curses.color_pair(0))
                axis_x.bkgd(curses.color_pair(0))
                axis_x.refresh()
                axis_y.refresh()
            if show_axis:
                notification = ("Showing X/Y values", 2)
            else:
                notification = ("Hiding X/Y values", 2)
        if key == ord("g"):
            show_grid = not show_grid
            if show_grid:
                notification = ("Showing grid", 2)
            else:
                notification = ("Hiding grid", 2)
        if key == ord("1"):
            zoom = Decimal(10)
        if key == ord("2"):
            zoom = Decimal(100)
        if key == ord("3"):
            zoom = Decimal(1000)
        if key == ord("4"):
            zoom = Decimal(10000)
        if key == ord("5"):
            zoom = Decimal(100000)
        if key == ord("6"):
            zoom = Decimal(1) / Decimal(10)
        if key == ord("7"):
            zoom = Decimal(1) / Decimal(100)
        if key == ord("8"):
            zoom = Decimal(1) / Decimal(1000)
        if key == ord("9"):
            zoom = Decimal(1) / Decimal(10000)
        if key == ord("0"):
            zoom = Decimal(1) / Decimal(100000)
        if key == curses.KEY_MOUSE:
            _, x, y, _, bstate = curses.getmouse()
            if bstate == 2097152:
                zoom = zoomout(zoom)
            if bstate == 65536:
                zoom = zoomin(zoom)
            if bstate == 2:
                mouse_start = (x, y)
            if bstate == 1:
                mouse_end = (x, y)
                offsetx -= mouse_start[0]-mouse_end[0]
                offsety += mouse_start[1]-mouse_end[1]
                if mouse_start == mouse_end:
                    notification = ("X: {}   Y: {}".format(round_to_decimals((x-offsetx)/zoom, 3), round_to_decimals((display.getmaxyx()[0]-y-offsety-1)/(zoom/2), 3)), -1)
        if key == ord("q") or key == 27:
            exit()

def request_formula(display, formulas):
    prompt = curses.newwin(len(formulas) + 5, round(display.getmaxyx()[1]/2), round((display.getmaxyx()[0]/2)-((len(formulas) + 5)/2)), round(display.getmaxyx()[1]/4))

    y = round(prompt.getmaxyx()[0]/2)

    key = 0
    selected = 0
    addnew = 1
    
    while True:
        for formula in formulas:
            if len(formula.strip()) == 0:
                formulas.remove(formula)
        addnew = 1 if len(formulas) < 10 else 0
        prompt.erase()
        if len(formulas) > 0:
            for index, formula in enumerate(formulas):
                if index == selected:
                    prompt.addstr(index+1, 1, str(index+1) + ":  f: " + formula, curses.A_REVERSE)
                else:
                    prompt.addstr(index+1, 1, str(index+1), curses.color_pair(index + 1))
                    prompt.addstr(index+1, 1 + len(str(index+1)), ":  f: " + formula)
            index += 1
        else:
            index = 0
            selected = 0
        if addnew:
            if index == selected:
                prompt.addstr(index+1, 1, "Add new", curses.A_REVERSE)
            else:
                prompt.addstr(index+1, 1, "Add new")
        prompt.box()
        prompt.addstr(0, round(prompt.getmaxyx()[1]/2)-7, "Add/Edit Formula")
        if prompt.getmaxyx()[1] - 50 > 0:
            prompt.addstr(prompt.getmaxyx()[0]-2, prompt.getmaxyx()[1] - 50, "ARROWS: move, ENTER: edit, DEL: delete, ESC: quit")
        prompt.refresh()
        key = display.getch()
        if key == curses.KEY_DOWN:
            selected += 1
            if selected >= len(formulas) + addnew:
                selected = 0
        elif key == curses.KEY_UP:
            selected -= 1
            if selected < 0:
                selected = len(formulas) - 1 + addnew
        if key == ord("\n"):
            key2 = 0
            prompt.erase()
            prompt.addstr(y, 1, "f: ")
            if selected < len(formulas):
                formula = formulas[selected]
                prompt.addstr(y, 4, formula)
                prompt.addstr(y, 4+len(formula), " ", curses.A_REVERSE)
            else:
                formula = ""
            cursor = len(formula)
            prompt.box()
            prompt.addstr(0, round(prompt.getmaxyx()[1]/2)-9, "Enter new formula")
            prompt.addstr(prompt.getmaxyx()[0]-2, prompt.getmaxyx()[1] - 10, "ESC: quit")
            prompt.refresh()
            while True:
                key2 = display.getch()
                prompt.erase()
                if key2 == 27:
                    prompt.erase()
                    prompt.refresh()
                    break
                if key2 == ord("\n"):
                    formula = formula.replace("^", "**")
                    try:
                        x_sym, y_sym = sp.symbols("x y", real = True)
                        formula_test = formula.strip()
                        left, right = formula_test.split("=")
                        left = sp.sympify(left)
                        right = sp.sympify(right)
                        eq = left - right
                        f = sp.lambdify((x_sym, y_sym), eq, "numpy")
                    except Exception as ex:
                        formula = ""
                        prompt.erase()
                        prompt.addstr(round(prompt.getmaxyx()[0]/2), round((prompt.getmaxyx()[1]/2)-7), "Invalid Formula")
                        if len(str(ex)) < prompt.getmaxyx()[1]-4:
                            prompt.addstr(round(prompt.getmaxyx()[0]/2)+1, 1, "\"" + str(ex) + "\"")
                        prompt.box()
                        prompt.refresh()
                        display.getch()
                        prompt.erase()
                        break
                    
                    if selected < len(formulas):
                        formulas[selected] = formula
                    else:
                        formulas.append(formula)
                    break
                elif key2 == 263: # Backspace
                    if formula == "":
                        pass
                    elif cursor == len(formula):
                        formula = list(formula)
                        formula.pop()
                        formula = "".join(formula)
                        cursor -= 1
                    elif cursor > 0:
                        formula = list(formula)
                        formula.pop(cursor - 1)
                        formula = "".join(formula)
                        cursor -= 1
                elif key2 == 330: # Delete
                    if cursor < len(formula):
                        formula = list(formula)
                        formula.pop(cursor)
                        formula = "".join(formula)
                elif key2 == curses.KEY_UP:
                    pass
                elif key2 == curses.KEY_DOWN:
                    pass
                elif key2 == curses.KEY_LEFT:
                    if cursor > 0:
                        cursor -= 1
                elif key2 == curses.KEY_RIGHT:
                    if cursor < len(formula):
                        cursor += 1
                else:
                    if len(formula) < prompt.getmaxyx()[1] - 4: # 4 for "f: " and border
                        if cursor != len(formula):
                            formula = list(formula)
                            formula.insert(cursor, chr(key2))
                            formula = "".join(formula)
                        else:
                            formula += chr(key2)
                        if cursor < len(formula):
                            cursor += 1
                
                prompt.addstr(y, 1, "f: ")
                prompt.addstr(y, 4, formula)
                if cursor < len(formula):
                    prompt.addstr(y, 4 + cursor, formula[cursor], curses.A_REVERSE)
                else:
                    prompt.addstr(y, 4 + cursor, " ", curses.A_REVERSE)
                prompt.box()
                prompt.addstr(0, round(prompt.getmaxyx()[1]/2)-9, "Enter new formula")
                prompt.addstr(prompt.getmaxyx()[0]-2, prompt.getmaxyx()[1] - 10, "ESC: quit")
                prompt.refresh()
        if key == 330:
            if selected != len(formulas):
                formulas.pop(selected)
        elif key == ord("q") or key == 27 or key == ord("f"):
            prompt.erase()
            prompt.refresh()
            break

    # if selected == len(formulas):
    #     formulas.append("")
    return formulas

def notify(display, message):
    popup = curses.newwin(3, len(message[0])+2, 0, display.getmaxyx()[1]-(len(message[0])+2))
    popup.box()
    if message[1] != -1:
        popup.addstr(1, 1, message[0], curses.color_pair(message[1]))
    else:
        msgX, msgY = message[0].split("   ")
        popup.addstr(1, 1, msgX, curses.color_pair(7))
        popup.addstr(1, len(msgX)+4, msgY, curses.color_pair(6))
    popup.refresh()
        

def stepzoom(zoom, treshold):
    step = zoom
    if step < treshold:
        step = treshold
    while step > treshold:
        step /= 2
    return ceil(step)
    
def zoomin(zoom):
    if 'E' not in str(zoom):
        zoomdigit = str(zoom).replace("0", "").replace(".", "")
    else:
        zoomdigit = str(zoom)[0]
    if zoomdigit == "1":
        zoom *= Decimal(2)
    if zoomdigit == "2":
        zoom *= Decimal(2.5)
    if zoomdigit == "5":
        zoom *= Decimal(2)
    return zoom

def zoomout(zoom):
    if 'E' not in str(zoom):
        zoomdigit = str(zoom).replace("0", "").replace(".", "")
    else:
        zoomdigit = str(zoom)[0]
    if zoomdigit == "1":
        zoom /= Decimal(2)
    if zoomdigit == "2":
        zoom /= Decimal(2)
    if zoomdigit == "5":
        zoom /= Decimal(2.5)
    return zoom

curses.wrapper(main)
