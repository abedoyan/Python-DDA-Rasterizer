#!/usr/bin/env python

from PIL import Image
from PIL import ImageColor
import sys
import math
import numpy as np

       

# Viewport transform
def transform(tri, width, height):
    count = 0
    triangle = []

    while (count < len(tri)):
        x_coord = ((tri[count][0]/tri[count][3])+1)*(width/2)
        y_coord = ((tri[count][1]/tri[count][3])+1)*(height/2)
        z_coord = tri[count][2]/tri[count][3]
        w_coord = tri[count][3]

        vertex = (x_coord, y_coord, z_coord, w_coord, tri[count][4], tri[count][5], tri[count][6], tri[count][7])
        triangle.append(vertex)
        count += 1

    return triangle



# Cull
def cullTri(triangle):
    ver_1 = [triangle[0][0], triangle[0][1], triangle[0][2]]
    ver_2 = [triangle[1][0], triangle[1][1], triangle[1][2]]
    ver_3 = [triangle[2][0], triangle[2][1], triangle[2][2]]

    cross_prod = np.cross(ver_1, ver_2)
    ccw = np.cross(cross_prod, ver_3)

    return ccw[0]

    


# sRGB convert to display
def sRGBDisplay(color):
    color = color/255
    
    if (color <= 0.04045):
        color = color / 12.92
    else:
        color = pow((color + 0.055)/1.055, 2.4)
        
    return color



# sRGB convert back to storage
def sRGBStorage(color):
    if (color <= 0.0031308):
        color = 12.92 * color
    else:
        color = 1.055 * pow(color, 1/2.4) - 0.055

    color = color * 255

    return color



# Scanline in X direction for triangles with horizontal edges
def x_scan1(tm_points, tb_points, depth, depth_buffer, sRGB, hyp):
    start = 0

    if (tb_points[start][0] - tm_points[start][0] == 0):
            start += 1

    if (tb_points[start][0] < tm_points[start][0] or tb_points[-1][0] < tm_points[-1][0]):
        temp = tb_points
        tb_points = tm_points
        tm_points = temp

            
    while (start < len(tm_points) and tm_points[start][1] <= tb_points[-1][1]):
        x_int = math.ceil(tm_points[start][0])
        y_int = tm_points[start][1]

        x_offset = x_int - tm_points[start][0]
        x_dist = tb_points[start][0] - tm_points[start][0]

        x_offset_z = (x_offset / x_dist) * (tb_points[start][2] - tm_points[start][2])
        x_step_z = (tb_points[start][2] - tm_points[start][2]) / x_dist

        x_offset_w = (x_offset / x_dist) * (tb_points[start][3] - tm_points[start][3])
        x_step_w = (tb_points[start][3] - tm_points[start][3]) / x_dist

        x_offset_r = (x_offset / x_dist) * (tb_points[start][4] - tm_points[start][4])
        x_step_r = (tb_points[start][4] - tm_points[start][4]) / x_dist

        x_offset_g = (x_offset / x_dist) * (tb_points[start][5] - tm_points[start][5])
        x_step_g = (tb_points[start][5] - tm_points[start][5]) / x_dist

        x_offset_b = (x_offset / x_dist) * (tb_points[start][6] - tm_points[start][6])
        x_step_b = (tb_points[start][6] - tm_points[start][6]) / x_dist

        x_offset_a = (x_offset / x_dist) * (tb_points[start][7] - tm_points[start][7])
        x_step_a = (tb_points[start][7] - tm_points[start][7]) / x_dist

        if (x_int < tb_points[start][0]):
            z = tm_points[start][2] + x_offset_z
            w = tm_points[start][3] + x_offset_w
            r = tm_points[start][4] + x_offset_r
            g = tm_points[start][5] + x_offset_g
            b = tm_points[start][6] + x_offset_b
            a = tm_points[start][7] + x_offset_a

            temp_r = r
            temp_g = g
            temp_b = b
            
            if (hyp == True):
                r = r/w
                g = g/w
                b = b/w

            if (sRGB == True):
                r = sRGBStorage(r)
                g = sRGBStorage(g)
                b = sRGBStorage(b)

            if (depth == True):
                if (z >= -1 and z < depth_buffer[x_int+1][y_int+1]):
                    image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                    x_int += 1
                    depth_buffer[x_int][y_int] = z
                else:
                    x_int += 1
            else:
                image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                x_int += 1

            r = temp_r
            g = temp_g
            b = temp_b


        while (x_int < tb_points[start][0]):
            z += x_step_z
            w += x_step_w
            r += x_step_r
            g += x_step_g
            b += x_step_b
            a += x_step_a

            temp_r = r
            temp_g = g
            temp_b = b

            if (hyp == True):
                r = r/w
                g = g/w
                b = b/w

            if (sRGB == True):
                r = sRGBStorage(r)
                g = sRGBStorage(g)
                b = sRGBStorage(b)

            if (depth == True):
                if (z >= -1 and z < depth_buffer[x_int+1][y_int+1]):
                    image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                    x_int += 1
                    depth_buffer[x_int][y_int] = z
                else:
                    x_int += 1
            else:
                image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                x_int += 1

            r = temp_r
            g = temp_g
            b = temp_b

        start += 1

    return depth_buffer




# Scanline in X direction for all other triangles
def x_scan2(left_point, right_point, depth, depth_buffer, sRGB, hyp):
    
    if (right_point[0] - left_point[0] != 0):            
        x_int = math.ceil(left_point[0])
        y_int = left_point[1]

        x_offset = x_int - left_point[0]
        x_dist = right_point[0] - left_point[0]

        x_offset_z = (x_offset / x_dist) * (right_point[2] - left_point[2])
        x_step_z = (right_point[2] - left_point[2]) / x_dist

        x_offset_w = (x_offset / x_dist) * (right_point[3] - left_point[3])
        x_step_w = (right_point[3] - left_point[3]) / x_dist

        x_offset_r = (x_offset / x_dist) * (right_point[4] - left_point[4])
        x_step_r = (right_point[4] - left_point[4]) / x_dist

        x_offset_g = (x_offset / x_dist) * (right_point[5] - left_point[5])
        x_step_g = (right_point[5] - left_point[5]) / x_dist

        x_offset_b = (x_offset / x_dist) * (right_point[6] - left_point[6])
        x_step_b = (right_point[6] - left_point[6]) / x_dist

        x_offset_a = (x_offset / x_dist) * (right_point[7] - left_point[7])
        x_step_a = (right_point[7] - left_point[7]) / x_dist

        if (x_int < right_point[0]):
            z = left_point[2] + x_offset_z
            w = left_point[3] + x_offset_w
            r = left_point[4] + x_offset_r
            g = left_point[5] + x_offset_g
            b = left_point[6] + x_offset_b
            a = left_point[7] + x_offset_a
            
            temp_r = r
            temp_g = g
            temp_b = b

            if (hyp == True):
                r = r/w
                g = g/w
                b = b/w
            
            if (sRGB == True):
                r = sRGBStorage(r)
                g = sRGBStorage(g)
                b = sRGBStorage(b)

            if (depth == True):
                if (z >= -1 and z < depth_buffer[x_int+1][y_int+1]):
                    image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                    x_int += 1
                    depth_buffer[x_int][y_int] = z
                else:
                    x_int += 1
            else:
                image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                x_int += 1

            r = temp_r
            g = temp_g
            b = temp_b

            
        while (x_int < right_point[0]):
            z += x_step_z
            w += x_step_w
            r += x_step_r
            g += x_step_g
            b += x_step_b
            a += x_step_a

            temp_r = r
            temp_g = g
            temp_b = b

            if (hyp == True):
                r = r/w
                g = g/w
                b = b/w

            if (sRGB == True):
                r = sRGBStorage(r)
                g = sRGBStorage(g)
                b = sRGBStorage(b)

            if (depth == True):
                if (z >= -1 and z < depth_buffer[x_int+1][y_int+1]):
                    image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                    x_int += 1
                    depth_buffer[x_int][y_int] = z
                else:
                    x_int += 1
            else:
                image.im.putpixel((x_int, y_int), (round(r), round(g), round(b), round(a)))
                x_int += 1

            r = temp_r
            g = temp_g
            b = temp_b


    return depth_buffer





# Get the points on the edges of the triangles
def edge_points(top, bot, z_off, w_off, r_off, g_off, b_off, a_off, z_step, w_step, r_step, g_step, b_step, a_step):
    points = []

    if (bot[0]-top[0] == 0):
        slope = 0
    else:
        slope = (bot[1] - top[1])/(bot[0] - top[0])

    b_coord = top[1] - (slope * top[0])

    y_coord = math.ceil(top[1])
    z = top[2] + z_off
    w = top[3] + w_off
    r = top[4] + r_off
    g = top[5] + g_off
    b = top[6] + b_off
    a = top[7] + a_off

    while (y_coord < bot[1]):
        if (slope == 0):
            x_coord = top[0]
        else:
            x_coord = (y_coord - b_coord)/slope

        points.append((x_coord, y_coord, z, w, r, g, b, a))
        y_coord += 1
        z += z_step
        w += w_step
        r += r_step
        g += g_step
        b += b_step
        a += a_step
    
    return points
    



# Scanline in Y direction
def y_scan(top, mid, bot, depth, depth_buffer, sRGB, hyp):    
    tm_dist = mid[1] - top[1]
    tb_dist = bot[1] - top[1]
    mb_dist = bot[1] - mid[1]

    top_offset = math.ceil(top[1]) - top[1]
    mid_offset = math.ceil(mid[1]) - mid[1]


    if (tm_dist != 0):
        tm_offset_z = (top_offset / tm_dist) * (mid[2] - top[2])
        tm_step_z = (mid[2] - top[2]) / tm_dist

        tm_offset_w = (top_offset / tm_dist) * (mid[3] - top[3])
        tm_step_w = (mid[3] - top[3]) / tm_dist
        
        tm_offset_r = (top_offset / tm_dist) * (mid[4] - top[4])
        tm_step_r = (mid[4] - top[4]) / tm_dist

        tm_offset_g = (top_offset / tm_dist) * (mid[5] - top[5])
        tm_step_g = (mid[5] - top[5]) / tm_dist

        tm_offset_b = (top_offset / tm_dist) * (mid[6] - top[6])
        tm_step_b = (mid[6] - top[6]) / tm_dist

        tm_offset_a = (top_offset / tm_dist) * (mid[7] - top[7])
        tm_step_a = (mid[7] - top[7]) / tm_dist
        
        tm_points = edge_points(top, mid, tm_offset_z, tm_offset_w, tm_offset_r, tm_offset_g, tm_offset_b, tm_offset_a, tm_step_z, tm_step_w, tm_step_r, tm_step_g, tm_step_b, tm_step_a)


    if (tb_dist != 0):
        tb_offset_z = (top_offset / tb_dist) * (bot[2] - top[2])
        tb_step_z = (bot[2] - top[2]) / tb_dist

        tb_offset_w = (top_offset / tb_dist) * (bot[3] - top[3])
        tb_step_w = (bot[3] - top[3]) / tb_dist
        
        tb_offset_r = (top_offset / tb_dist) * (bot[4] - top[4])
        tb_step_r = (bot[4] - top[4]) / tb_dist

        tb_offset_g = (top_offset / tb_dist) * (bot[5] - top[5])
        tb_step_g = (bot[5] - top[5]) / tb_dist

        tb_offset_b = (top_offset / tb_dist) * (bot[6] - top[6])
        tb_step_b = (bot[6] - top[6]) / tb_dist

        tb_offset_a = (top_offset / tb_dist) * (bot[7] - top[7])
        tb_step_a = (bot[7] - top[7]) / tb_dist

        tb_points = edge_points(top, bot, tb_offset_z, tb_offset_w, tb_offset_r, tb_offset_g, tb_offset_b, tb_offset_a, tb_step_z, tb_step_w, tb_step_r, tb_step_g, tb_step_b, tb_step_a)


    if (mb_dist != 0):
        mb_offset_z = (mid_offset / mb_dist) * (bot[2] - mid[2])
        mb_step_z = (bot[2] - mid[2]) / mb_dist

        mb_offset_w = (mid_offset / mb_dist) * (bot[3] - mid[3])
        mb_step_w = (bot[3] - mid[3]) / mb_dist
        
        mb_offset_r = (mid_offset / mb_dist) * (bot[4] - mid[4])
        mb_step_r = (bot[4] - mid[4]) / mb_dist

        mb_offset_g = (mid_offset / mb_dist) * (bot[5] - mid[5])
        mb_step_g = (bot[5] - mid[5]) / mb_dist

        mb_offset_b = (mid_offset / mb_dist) * (bot[6] - mid[6])
        mb_step_b = (bot[6] - mid[6]) / mb_dist

        mb_offset_a = (mid_offset / mb_dist) * (bot[7] - mid[7])
        mb_step_a = (bot[7] - mid[7]) / mb_dist

        mb_points = edge_points(mid, bot, mb_offset_z, mb_offset_w, mb_offset_r, mb_offset_g, mb_offset_b, mb_offset_a, mb_step_z, mb_step_w, mb_step_r, mb_step_g, mb_step_b, mb_step_a)



    if (top[1] == mid[1]):
        depth_buffer = x_scan1(tb_points, mb_points, depth, depth_buffer, sRGB, hyp)
    elif (mid[1] == bot[1]):
        depth_buffer = x_scan1(tm_points, tb_points, depth, depth_buffer, sRGB, hyp)
    else:
        start = 0
        while (start < len(tm_points)):
            if (tb_points[start][0] > tm_points[start][0]):
                depth_buffer = x_scan2(tm_points[start], tb_points[start], depth, depth_buffer, sRGB, hyp)
                start += 1
            else:
                depth_buffer = x_scan2(tb_points[start], tm_points[start], depth, depth_buffer, sRGB, hyp)
                start += 1

        new_start = 0
        while (new_start < len(mb_points)):
            if (tb_points[start][0] > mb_points[new_start][0]):
                depth_buffer = x_scan2(mb_points[new_start], tb_points[start], depth, depth_buffer, sRGB, hyp)
                start += 1
                new_start += 1
            else:
                depth_buffer = x_scan2(tb_points[start], mb_points[new_start], depth, depth_buffer, sRGB, hyp)
                start += 1
                new_start += 1
    

    

    
# DDA Algorithm
def algDDA(triangle, depth, depth_buffer, sRGB, hyp):
    points = np.array(triangle)
    sorted_points = points[points[:,1].argsort()]

    top_point = sorted_points[0]
    mid_point = sorted_points[1]
    bot_point = sorted_points[2]

    y_scan(top_point, mid_point, bot_point, depth, depth_buffer, sRGB, hyp) 

    



# draw_line_points
def draw_line_points(start_point, end_point, loc_int, dist, offset, slope, b_coord, x_direction, y_direction):
    points = []
    
    z_off = (offset / dist) * (end_point[2] - start_point[2])
    z_step = (end_point[2] - start_point[2]) / dist
    
    w_off = (offset / dist) * (end_point[3] - start_point[3])
    w_step = (end_point[3] - start_point[3]) / dist

    r_off = (offset / dist) * (end_point[4] - start_point[4])
    r_step = (end_point[4] - start_point[4]) / dist

    g_off = (offset / dist) * (end_point[5] - start_point[5])
    g_step = (end_point[5] - start_point[5]) / dist

    b_off = (offset / dist) * (end_point[6] - start_point[6])
    b_step = (end_point[6] - start_point[6]) / dist

    a_off = (offset / dist) * (end_point[7] - start_point[7])
    a_step = (end_point[7] - start_point[7]) / dist

    
    z = start_point[2] + z_off
    w = start_point[3] + w_off
    r = start_point[4] + r_off
    g = start_point[5] + g_off
    b = start_point[6] + b_off
    a = start_point[7] + a_off

    if (x_direction == True):
        x_coord = loc_int
        
        while (x_coord < end_point[0]):
            y_coord = (slope * x_coord) + b_coord

            points.append((x_coord, y_coord, z, w, r, g, b, a))

            x_coord += 1
            z += z_step
            w += w_step
            r += r_step
            g += g_step
            b += b_step
            a += a_step

    elif (y_direction == True):
        y_coord = loc_int
        
        while (y_coord < end_point[1]):
            if (slope == 0):
                x_coord = start_point[0]
            else:
                x_coord = (y_coord - b_coord)/slope

            points.append((x_coord, y_coord, z, w, r, g, b, a))

            y_coord += 1
            z += z_step
            w += w_step
            r += r_step
            g += g_step
            b += b_step
            a += a_step
        
    return points


    

# Draw Line algorithm for line
def drawLine(line_list):
    points = []
    step_in_x = False
    step_in_y = False
    
    line_np = np.array(line_list)

    if (abs(line_np[0][0] - line_np[1][0]) > abs(line_np[0][1] - line_np[1][1])):
        sorted_line = line_np[line_np[:,0].argsort()]

        start_point = sorted_line[0]
        end_point = sorted_line[1]
        
    else:
        sorted_line = line_np[line_np[:,1].argsort()]

        start_point = sorted_line[0]
        end_point = sorted_line[1]

    x_dist = end_point[0] - start_point[0]
    y_dist = end_point[1] - start_point[1]

    x_offset = math.ceil(start_point[0]) - start_point[0]
    y_offset = math.ceil(start_point[1]) - start_point[1]

    x_int = math.ceil(start_point[0])
    y_int = math.ceil(start_point[1])


    if (round(x_dist) == 0):
        slope = 0
    else:
        slope = y_dist/x_dist


    b_coord = start_point[1] - (slope * start_point[0])
        

    if (abs(x_dist) > abs(y_dist)):
        step_in_x = True
        points = draw_line_points(start_point, end_point, x_int, x_dist, x_offset, slope, b_coord, step_in_x, step_in_y)
    else:
        step_in_y = True
        points = draw_line_points(start_point, end_point, y_int, y_dist, y_offset, slope, b_coord, step_in_x, step_in_y)


    for p in points:
        image.im.putpixel((round(p[0]), round(p[1])), (round(p[4]), round(p[5]), round(p[6]), round(p[7])))

    


    
################ End of Function Definitions ########################    


# declare and initialize variables
width = 1
height = 1
output = 'file.png'

red = 255
green = 255
blue = 255
alpha = 255

vertices = []
triangle = []

sRGB = False
hyp = False
cull = False
depth = False
depth_buffer = np.ones((width+1)*(height+1)).reshape(width+1,height+1)

image = Image.new("RGBA", (width, height), (0,0,0,0))

input_file = sys.argv[-1]


# read in text file
with open(input_file) as file:
    rows = file.readlines()

    # remove whitespace and skip empty lines
    for row in rows:
        row = row.strip()
        if row != '': 
            words = row.split()

            # create blank image of specified width and height
            # get the filename for the output image
            if words[0] == 'png':
                width = int(words[1])
                height = int(words[2])
                output = words[3]
                image = Image.new("RGBA", (width, height), (0,0,0,0))


            # enable a depth buffer
            elif words[0] == 'depth':
                depth_buffer = np.ones((width+1)*(height+1)).reshape(width+1,height+1)
                depth = True


            # sRGB
            elif words[0] == 'sRGB':
                sRGB = True


            # Hyperbolic interpolation
            elif words[0] == 'hyp':
                hyp = True


            # Cull
            elif words[0] == 'cull':
                cull = True


            # add the vertices of the triangles to a list
            elif words[0] == 'xyzw':
                x = float(words[1])
                y = float(words[2])
                z = float(words[3])
                w = float(words[4])
                
                if (cull == True):
                    vertex = (x, y, z, w, red, green, blue, alpha)
                    vertices.append(vertex)

                elif (hyp == True):
                    x_coord = ((x/w)+1)*(width/2)
                    y_coord = ((y/w)+1)*(height/2)
                    z_coord = z/w
                    w_coord = 1/w
                    r = red/w
                    g = green/w
                    b = blue/w
                    a = alpha

                    vertex = (x_coord, y_coord, z_coord, w_coord, r, g, b, a)
                    vertices.append(vertex)
                    
                else:
                    x_coord = ((x/w)+1)*(width/2)
                    y_coord = ((y/w)+1)*(height/2)
                    z_coord = z/w
                    w_coord = w
                    
                    vertex = (x_coord, y_coord, z_coord, w_coord, red, green, blue, alpha)
                    vertices.append(vertex)
                


            # update the RGB colors
            elif words[0] == 'rgb':
                if (sRGB == True):
                    red = sRGBDisplay(float(words[1]))
                    green = sRGBDisplay(float(words[2]))
                    blue = sRGBDisplay(float(words[3]))
                    alpha = 255
                else:
                    red = float(words[1])
                    green = float(words[2])
                    blue = float(words[3])
                    alpha = 255



            # get the triangle vertices
            elif words[0] == 'tri':
                triangle = []
                for num in range(1, 4):
                    if int(words[num]) > 0:
                        vertex = vertices[int(words[num]) - 1]
                    elif int(words[num]) < 0:
                        vertex = vertices[int(words[num])]
                    triangle.append(vertex)

                if (cull == True):
                    if (cullTri(triangle) > 0):
                        triangle = transform(triangle, width, height)
                        algDDA(triangle, depth, depth_buffer, sRGB, hyp)
                        triangle = []
                    else:
                        triangle = []
                else:
                    algDDA(triangle, depth, depth_buffer, sRGB, hyp)
                    triangle = []



            
            # Point
            elif words[0] == 'point':
                triangle = []
                point_size = float(words[1])/2
                point_draw = vertices[int(words[2])]

                if (point_size == 0 ):
                    if (point_draw[2] >= -1 and point_draw[2] < depth_buffer[round(point_draw[0])+1][round(point_draw[1])+1]):
                        image.im.putpixel((round(point_draw[0]), round(point_draw[1])), (round(point_draw[4]), round(point_draw[5]), round(point_draw[6]), round(point_draw[7])))
                        depth_buffer[round(point_draw[0])][round(point_draw[1])] = point_draw[2]

                else:
                    if (point_draw[0] - point_size < 0):
                        left_x = 0
                    else:
                        left_x = point_draw[0] - point_size


                    if (point_draw[0] + point_size > width):
                        right_x = width
                    else:
                        right_x = point_draw[0] + point_size


                    if (point_draw[1] - point_size < 0):
                        top_y = 0
                    else:
                        top_y = point_draw[1] - point_size


                    if (point_draw[1] + point_size > height):
                        bot_y = height
                    else:
                        bot_y = point_draw[1] + point_size


                    point1 = (left_x, top_y, point_draw[2], point_draw[3], point_draw[4], point_draw[5], point_draw[6], point_draw[7])
                    point2 = (right_x, top_y, point_draw[2], point_draw[3], point_draw[4], point_draw[5], point_draw[6], point_draw[7])
                    point3 = (right_x, bot_y, point_draw[2], point_draw[3], point_draw[4], point_draw[5], point_draw[6], point_draw[7])
                    point4 = (left_x, bot_y, point_draw[2], point_draw[3], point_draw[4], point_draw[5], point_draw[6], point_draw[7])

                    triangle.append(point1)
                    triangle.append(point2)
                    triangle.append(point3)

                    algDDA(triangle, depth, depth_buffer, sRGB, hyp)
                    triangle = []
                    
                    triangle.append(point3)
                    triangle.append(point4)
                    triangle.append(point1)

                    algDDA(triangle, depth, depth_buffer, sRGB, hyp)
                    triangle = []
                
            
            
            
            # get the line vertices
            elif words[0] == 'line':
                line_list = []
                for num in range(1, 3):
                    if int(words[num]) > 0:
                        line_point = vertices[int(words[num]) - 1]
                    elif int(words[num]) < 0:
                        line_point = vertices[int(words[num])]
                    line_list.append(line_point)

                drawLine(line_list)
            

        else:
            pass


image.save(output)

