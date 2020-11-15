from sympy import Symbol, solve, cos, sin, atan

'''
This code will do the math to turn the accelerometer reading into a
measurement of the centrifugal force
'''

#e1 points down
#e2 points in the radial direction
#e3 points tangent to the radial direction

def findforce(accelArray,accelArray0, mass):

    e1 = accelArray[2]  #z
    e2 = accelArray[1]  #y
    e3 = accelArray[0]  #x

    e10 = accelArray0[2]  #z0
    e20 = accelArray0[1]  #y0
    e30 = accelArray0[0]  #x0

    theta = atan(e10/e20)
    
    a_c = abs(e1*cos(theta)-e2*sin(theta))

    f_c = 9.8 * a_c * mass /1000

    return f_c
