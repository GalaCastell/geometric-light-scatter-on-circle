#/usr/bin/env python
# -*- coding=utf-8 -*-

from __future__ import division
import math
from numpy import matrix
from pygameVector import Vec2d
from intersectionElements import Circle, Line, Light

__all__ = ['intersection', 'reflection', 'refraction']


BASIC_X_AXIS_VECTOR = Vec2d(1, 0)
BASIC_Y_AXIS_VECTOR = Vec2d(0, 1)


def intersection(circle, vector, start_point):
    # get circle attributes
    center = Vec2d(circle.center)
    radius = circle.radius

    start_point = Vec2d(start_point)
    # the params for calculating t 
    a = vector.dot(vector)
    b = 2 * (vector.dot(start_point - center))
    c = start_point.dot(start_point) + center.dot(center) - 2*start_point.dot(center) - pow(radius, 2)
    # judge if there's intersection
    disc = b*b - 4*a*c
    if disc < 0:
        return None
    sqrt_disc = math.sqrt(disc)
    t1 = (-b - sqrt_disc) / (2*a)
    t2 = (-b + sqrt_disc) / (2*a)
    multi_factor = [x for x in (t1, t2) if abs(x) > 1e-6]   # filt the start point
    intersection = [start_point + t*vector for t in multi_factor]
    # left point & right point vector
    intersection_one = intersection[0]
    if len(intersection) > 1:
        intersection_two = intersection[1]
    else:
        # start point is one of the intersection point
        intersection_two = start_point
    return ((intersection_one.x, intersection_one.y), (intersection_two.x, intersection_two.y))


def start_point(circle, vector):

    def boarder_intersection_point(circle, vector):
        vertical_vector = vector.rotate(90)
        center = circle.center
        boarder_intersection_point = intersection(circle, vector, center)
        return boarder_intersection_point




def compute_direction_on_intersection(circle, incident_light, start_point):
    # calculate the C matrix and the K factor of the incident ray

    def convert_to_rectangular_coordinate(vertical, tangen):
        # compute the transform factor
        m11 = BASIC_X_AXIS_VECTOR.dot(vertical)
        m12 = BASIC_X_AXIS_VECTOR.dot(tangen)
        m21 = BASIC_Y_AXIS_VECTOR.dot(vertical)
        m22 = BASIC_Y_AXIS_VECTOR.dot(tangen)
        C = matrix([[m11, m12], [m21, m22]])
        return C

    center = circle.center
    radius = circle.radius
    incident_vector = incident_light.k * incident_light.direction    # vector that represent the light direction

    angle = math.pi - math.asin((start_point[1]-center[1])/radius)     # take the left point; angle to calculate the vector of interfac
    vertical_direction = Vec2d(math.cos(angle), math.sin(angle))
    tangen_direction = Vec2d((-1)*math.sin(angle), math.cos(angle))
    # the components of the incident ray
    incident_k_vertical = incident_vector.dot(vertical_direction)
    incident_k_tangen = incident_vector.dot(tangen_direction)
    incident_k_matrix = matrix([[incident_k_vertical], [incident_k_tangen]])
    # factor that determine the relection ray and refraction ray
    transform_factor = convert_to_rectangular_coordinate(vertical_direction, tangen_direction)

    return dict(c=transform_factor, k=incident_k_matrix, tangen=tangen_direction, vertical=vertical_direction)


def reflection(circle, incident_light, start_point):
    # attributes of the incident_light
    wavelength =  incident_light.wavelength
    refraction_index = incident_light.refraction_index
    
    factors = compute_direction_on_intersection(circle, incident_light, start_point)
    # light direction
    # formula to calculate the K factor
    factors['k'][0] = (-1) * factors['k'][0]
    matrix_vector = factors['c'] * factors['k']
    vector_x = matrix_vector.A1[0]
    vector_y = matrix_vector.A1[1]
    vector = Vec2d(vector_x, vector_y)
    return Light(wavelength, vector, refraction_index)


def refraction(circle, incident_light, start_point, refraction_index):
    # attributes of the incident_light
    wavelength = incident_light.wavelength
    
    factors = compute_direction_on_intersection(circle, incident_light, start_point)
    # refraction light direction
    # formula
    wavenum = Light.wavenum(wavelength, refraction_index)
    K = factors['k']
    incident_k_vertical = K.A1[0]
    incident_k_tangen = K.A1[1]
    K.A1[0] = int(incident_k_vertical/abs(incident_k_vertical)) \
         * math.sqrt(wavenum*wavenum - incident_k_tangen*incident_k_tangen)
    matrix_vector = factors['c'] * K
    vector_x = matrix_vector.A1[0]
    vector_y = matrix_vector.A1[1]
    vector = Vec2d(vector_x, vector_y).normalized()
    return Light(wavelength, vector, refraction_index)


def main():
    circle = Circle(10, (3, 4))
    point_a = (-12, 6)
    point_b = (20, 6)
    vector = Vec2d(point_b) - Vec2d(point_a)
    line = Line(point_a, point_b)

    # test the intersection point correction
    a, b = intersection(circle, vector, point_a)
    # print ('Left point:{0}, Right point:{1}'.format(a, b))
    # print ('points on the circle:  Left:{0}, Right:{1}'.format(circle.on_circle(a), circle.on_circle(b)))
    # print ('points on the line:  Left:{0}, Right:{1}'.format(line.on_line(a), line.on_line(b)))

    # test reflection light and refraction light
    incident_light = Light(256, vector.normalized(), 1, unit='nm')
    
    reflection_light = reflection(circle, incident_light, point_a)
    # print ('reflection direction:{0}, wavelength:{1}, refraction_index:{2}, k:{3}'.format(reflection_light.direction,\
    #         reflection_light.wavelength, reflection_light.refraction_index, reflection_light.k))

    refraction_light = refraction(circle, incident_light, point_a, 1.334)
    intersection_point = intersection(circle, refraction_light.direction, a)
    # print (intersection_point[0], intersection_point[1])
    # print ('refraction direction:{0}, wavelength:{1}, refraction_index:{2}, k:{3}'.format(refraction_light.direction, \
    #         refraction_light.wavelength, refraction_light.refraction_index, refraction_light.k))

    # test the boarder
    vector = Vec2d(2, 4)
    boarder = intersection_boarder(circle, vector)
    print (boarder)




if __name__ == '__main__':
    main()
