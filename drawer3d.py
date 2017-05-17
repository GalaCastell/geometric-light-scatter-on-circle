#/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import math
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d import art3d
from pygameVector import Vec3d
from funcs3d import *
from intersectionElements import Sphere, Light


COLORS = ['#FF0033', '#FF6600', '#FFFF33', '#33FF33',
          '#00FFFF', '#006666', '#CC00CC', '#000000', '#CCCCCC']    # red, orange, yellow, green, blue, navy, purple, black, silver


def generate_sphere_cordinates(radius, longitude, latitude):
    longitude = complex(0, longitude)
    latitude = complex(0, latitude)
    u, v = np.mgrid[0:2*np.pi:longitude, 0:np.pi:latitude]
    x = radius * np.cos(u)*np.sin(v)
    y = radius * np.sin(u)*np.sin(v)
    z = radius * np.cos(v)
    return (x, y, z)


def generate_skeleton(radius, horizon_or_vertical):
    theta = np.linspace(-np.pi, np.pi, 100)
    if 'h' == horizon_or_vertical:
        x = radius * np.sin(theta)
        y = radius * np.cos(theta)
        z = np.linspace(0, 0, 100)
    elif 'v' == horizon_or_vertical:
        z = radius * np.sin(theta)
        x = radius * np.cos(theta)
        y = np.linspace(0, 0, 100)
    else:
        y = radius * np.sin(theta)
        z = radius * np.cos(theta)
        x = np.linspace(0, 0, 100)
    return (x, y, z)


def generate_centerline(radius):
    vertical_line = draw_line((0, 0, -radius), (0, 0, radius), 'solid', 'b')
    horizon_line = draw_line((-radius, 0, 0), (radius, 0, 0), 'solid', 'b')
    plain_line = draw_line((0, -radius, 0), (0, radius, 0), 'solid', 'b')
    return [vertical_line, horizon_line, plain_line]


def draw_line(s, e, linestyle='dashed', color='b'):
    l = art3d.Line3D((s[0], e[0]), (s[1], e[1]), (s[2], e[2]), color=color)
    l.set_linestyle(linestyle)
    return l


def draw_line_outside(start, vector, length, linestyle='dashed', color='b'):
    s = start
    vector = vector.normalized() * length
    e = start + vector
    return draw_line(s, e, linestyle, color)


def drawer(sphere, incident_light, refraction_index, start_point, intersection_time=1):

    radius = sphere.radius

    points = []
    lines = []

    time_of_intersection = 1
    points.append(start_point)
    first_intersection_point = calculate_intersection_on_sphere(sphere, incident_light, start_point)[0]
    points.append(first_intersection_point)
    lines.append(draw_line(start_point, first_intersection_point, 'solid'))

    reflection_light = reflection(sphere, incident_light, first_intersection_point)
    refraction_light = refraction(sphere, incident_light, first_intersection_point, refraction_index)

    first_reflection_line = draw_line_outside(first_intersection_point, reflection_light.direction, 2*radius, 'solid')
    second_intersection_point = calculate_intersection_on_sphere(sphere, refraction_light, first_intersection_point)[0]
    points.append(second_intersection_point)
    first_refraction_line = draw_line(first_intersection_point, second_intersection_point)
    lines.append(first_reflection_line)
    lines.append(first_refraction_line)

    if 1 == intersection_time:
        return dict(points=points,
                    lines=lines)
    else:
        incident_light = refraction_light
        intersection_point = second_intersection_point
        while time_of_intersection < intersection_time:
            time_of_intersection += 1
            reflection_light = reflection(sphere, incident_light, intersection_point)
            refraction_light = refraction(sphere, incident_light, intersection_point, 1)

            refraction_line = draw_line_outside(intersection_point, refraction_light.direction, 2*radius, 'solid')

            next_intersection_point = calculate_intersection_on_sphere(sphere, reflection_light, intersection_point)[0]
            points.append(next_intersection_point)
            reflection_line = draw_line(intersection_point, next_intersection_point)
            lines.append(reflection_line)
            lines.append(refraction_line)
            incident_light = reflection_light
            intersection_point = next_intersection_point
        return dict(points=points,
                    lines=lines)


def generate_multi_start_points(radius, num, set_x=None, set_y=None, set_z=None):
    # 绘制片状光与面状光
    def combine(iterable, _set):
        for i in iterable:
            yield (i, _set)

    coordinates = [[], [], []]   # 初始化三个坐标容器
    x, y, z = [], [], []
    step = 2*radius/(num-1)
    scope = [-radius+step*i for i in range(num)]
    for i, _setting in enumerate((set_x, set_y, set_z)):
        if _setting is None:
            _co = scope
        else:
            _co = [_setting]
        coordinates[i] = _co
    start_point_list = list(product(coordinates[0], coordinates[1], coordinates[2]))
    return start_point_list


def multi_line_drawer(sphere, incident_light, refraction_index, start_point_list, intersection_time):
    # 绘制多个起点的散射情况
    radius = sphere.radius
    
    points = []
    reflection_lines = []
    refraction_lines = []
    lines = {'reflection_lines': reflection_lines,
             'refraction_lines': refraction_lines}

    points.append(start_point_list)
    time_of_intersection = 1
    color_offset = 0
    # 第一次作用
    first_intersection_point_list = [calculate_intersection_on_sphere(sphere, incident_light, p) for p in start_point_list]

    incident_line = [draw_line(s, e[0], 'solid', COLORS[color_offset]) for (s, e) in zip(start_point_list, first_intersection_point_list) if e]
    lines['incident_line'] = [incident_line, ]

    first_intersection_point_list = [p[0] for p in first_intersection_point_list if p] # 清除无效点
    points.append(first_intersection_point_list)

    first_reflection_lights = [reflection(sphere, incident_light, p) for p in first_intersection_point_list]
    first_refraction_lights = [refraction(sphere, incident_light, p, refraction_index) for p in first_intersection_point_list]

    first_reflection_lines = [draw_line_outside(s, light.direction, 2*radius, 'solid', COLORS[color_offset])
                                for (light, s) in zip(first_reflection_lights, first_intersection_point_list)]
    # [0] 指(end, start) 是与球的第二个交点end, 起点是start
    second_intersection_point_list = [calculate_intersection_on_sphere(sphere, light, p)[0] 
                                for (light, p) in zip(first_refraction_lights, first_intersection_point_list)]
    first_refraction_lines = [draw_line(s, e, color=COLORS[color_offset]) for (s, e) in zip(first_intersection_point_list, second_intersection_point_list)]

    reflection_lines.append(first_reflection_lines)
    refraction_lines.append(first_refraction_lines)


    if 1 < intersection_time:
        # 作用次数大于1
        incident_lights = first_refraction_lights
        intersection_point_list = second_intersection_point_list
        while time_of_intersection < intersection_time:
            time_of_intersection += 1
            # 选择颜色
            color_offset = (-1)*(time_of_intersection+1)//2 - 1 if (time_of_intersection+1)%2 else (time_of_intersection+1)//2 
            # 球内反射光
            reflection_lights = [reflection(sphere, light, p) 
                                    for (light, p) in zip(incident_lights, intersection_point_list)]
            # 折射光，出射
            refraction_lights = [refraction(sphere, light, p, refraction_index)
                                    for (light, p) in zip(incident_lights, intersection_point_list)]

            # 折射 出射线段
            refraction_lines = [draw_line_outside(s, light.direction, 2*radius, 'solid', COLORS[color_offset])
                                    for (light, s) in zip(refraction_lights, intersection_point_list)]
            lines['refraction_lines'].append(refraction_lines)

            # 作用点（下次）
            next_intersection_point_list = [calculate_intersection_on_sphere(sphere, light, p)[0]
                                                for (light, p) in zip(reflection_lights, intersection_point_list)]
            points.append(next_intersection_point_list)
            # 反射光线段
            reflection_lines = [draw_line(s, e, color=COLORS[color_offset]) for (s, e) in zip(intersection_point_list, next_intersection_point_list)]
            lines['reflection_lines'].append(reflection_lines)
            incident_lights = reflection_lights
            intersection_point_list = next_intersection_point_list
    points = [(x, y, z) for times_points in points for (x, y, z) in times_points]
    points = tuple(zip(*points))
    return dict(points=points,
                lines=lines)



def main():

    radius = 10
    sphere = Sphere(radius, (0, 0, 0))

    v = Vec3d(0, 1, 0)
    light = Light(532, v, 1, unit='nm')
    refraction_index = 1.335

    x = 0
    y = -15
    z = 6
    start_point = (x, y, z)
    start_point_list1 = generate_multi_start_points(radius, 5, set_y=-15, set_z=6)
    start_point_list2 = generate_multi_start_points(radius, 5, set_y=-15)

    intersection_time = 3
    points_and_lines = multi_line_drawer(sphere, light, refraction_index, start_point_list2, intersection_time)
    points = points_and_lines['points']

    lines = points_and_lines['lines'].values()
    lines = [p_line for type_lines in lines for time_lines in type_lines for p_line in time_lines]


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(*points)

    for line in lines:
        ax.add_line(line)

    x, y, z = generate_sphere_cordinates(radius, 100, 100)
    alpha = 0.1
    ax.plot_surface(x, y, z, color='b', alpha=alpha)
    horizon_skeleton = generate_skeleton(radius, 'h')
    vertical_skeleton = generate_skeleton(radius, 'v')
    plain_skeleton = generate_skeleton(radius, 'p')
    ax.plot(*horizon_skeleton, color='b')
    ax.plot(*vertical_skeleton, color='b')
    ax.plot(*plain_skeleton, color='b')
    for line in generate_centerline(radius):
        ax.add_line(line)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()


if __name__ == '__main__':
    main()
    
