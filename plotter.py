from math import *
import time
import sympy as sp
import numpy as np
import numbers

def plot(   formulas = [],
            plotsize = [50, 50],
            step = (5, 5),
            zoom = (1, 1),
            offset = (0, 0),
            dot_density = 1,
            precision = 1):

    AXIS_BRIGHTNESS = 40#40
    GRID_BRIGHTNESS = 70
    DECIMAL_PRECISION = 3
    offsetx, offsety = offset
    zoom_x, zoom_y = zoom
    step_x, step_y = step

    axis_y_charlength = find_axis_y_charlength(plotsize[1] - 2, offsety-1, zoom_y, DECIMAL_PRECISION) # Auto set charlength y

    graphs = []

    axis_y = ""

    if formulas != None:
        if type(formulas) != list:
            raise ValueError("Expected list, got {0}: {1}".format(type(formulas).__name__, repr(formulas)))
        for style, formula in enumerate(formulas, 1):
            graph = []

            x_sym, y_sym = sp.symbols("x y", real = True)
            formula = formula.strip()
            left, right = formula.split("=")

            left = sp.sympify(left)
            right = sp.sympify(right)

            eq = left - right
            f = sp.lambdify((x_sym, y_sym), eq)
            
            for x in range(plotsize[0]):
                for y in range(plotsize[1]):
                    try:
                        value = f((x-offsetx)/zoom_x, ((plotsize[1]-y)-offsety)/zoom_y)*zoom_x
                    except Exception:
                        continue
                    if np.iscomplex(value):
                        continue
                    if isnan(value):
                        continue
                    if abs(value) < precision:
                        graph.append([[x, y], "*", style])
                                
            graphs.append(graph)

    graph = []
    for i in graphs:
        for dot in i:
            graph.append(dot)
    
    axis_y = ""
    for i in range(plotsize[1] - 1):
        if (plotsize[1] - (i + offsety)) % step_y == 0:
            axis_y += "{0: >{1}}".format(str(round_to_decimals((plotsize[1] - (i + offsety)) / zoom_y, DECIMAL_PRECISION)), axis_y_charlength).upper() + "\n"
        else:
            axis_y += (" " * axis_y_charlength) + "\n"
    
    axis_x_lines = ""
    for i in range(plotsize[0]):
        if len(axis_x_lines) + axis_y_charlength + 1 + len(str(round_to_decimals((plotsize[0] - offsetx + axis_y_charlength + 1) / zoom_x, DECIMAL_PRECISION))) < plotsize[0]:
            if (i - offsetx + axis_y_charlength + 1) % step_x == 0:
                axis_x_lines += "|"
            else:
                axis_x_lines += " "
        else:
            break
            

    axis_x_numbers = ""
    i = 0
    while i < len(axis_x_lines):
        if axis_x_lines[i] != " ":
            axis_x_numbers += str(round_to_decimals((i - offsetx + axis_y_charlength + 1) / zoom_x, DECIMAL_PRECISION)).upper()
            i += len(str(round_to_decimals((i - offsetx + axis_y_charlength + 1) / zoom_x, DECIMAL_PRECISION)))
        else:
            i += 1
            axis_x_numbers += " "

    axis_x = axis_x_lines + "\n" + axis_x_numbers
    return graph, axis_x, axis_y
    
def rotate(dataset):
    buffer = []
    output = [dataset[0], []]
    for x in range(len(dataset[1][0])):
        for y in dataset[1]:
            buffer.append(y[x])
        output[1].insert(0, buffer)
        buffer = []
    return output

def round_to_decimals(number, sig = 1):
    if number == 0:
        return 0
    number = round(number, -int(floor(log10(abs(number)))) - 1 + sig)
    if number % 1 == 0:
        return int(number)
    return number

def find_axis_y_charlength(plotsize_y, offsety, zoom_y, decimal_precision):
    largest = 0
    current = 0
    for index in range(plotsize_y):
        current = len(
                    str(
                        round_to_decimals(
                            (plotsize_y - (index + offsety + 1))/zoom_y,
                            decimal_precision
                        )
                    )
                )
        if current > largest:
            largest = current
    return largest
