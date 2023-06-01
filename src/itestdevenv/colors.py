from math import sqrt

def vector_sum(a, b):
	return tuple(x+y for x,y in zip(a,b))

def dot_product(a, b):
    return sum(x*y for x,y in zip(a,b))

def cross_product(a, b):
	assert len(a) == 3
	assert len(b) == 3
	result = (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])
	assert dot_product(result, a) < 0.00001
	assert dot_product(result, b) < 0.00001
	return result

def difference(a, b):
	return tuple(x-y for x,y in zip(a,b))

def magnitude(vector):
	return sqrt(dot_product(vector, vector))

def multiply_vector_scalar(vector, scalar):
	return tuple(x*scalar for x in vector)

# A component of b that is parallel to a
def tangent_component(a, b):
	return multiply_vector_scalar(a, dot_product(a, b) / (magnitude(a) ** 2 ) )

# A component of b that is normal to a
def normal_component(a, b):
	return difference(b, tangent_component(a, b))

# Given two vectors a and compute a magnitude of projection of c - a on b - a, normalized over length of b - a
def tangential_ratio(a, b, c):
	return magnitude(tangent_component(difference(c, a), difference(b, a))) / magnitude(difference(b, a))

# Given two vectors a and compute a magnitude of normal of c - a on b - a, normalized over length of b - a
def normal_ratio(a, b, c):
	return magnitude(normal_component(difference(c, a), difference(b, a))) / magnitude(difference(b, a))

foreground = (0, 0, 0)
background = (255, 255, 255)
highglight_background = (213, 235, 255)

foreground_axis = difference(foreground, background)
background_correction = difference(highglight_background, background)

print ("Foreground axis:", foreground_axis)
print("Background correction:", background_correction)

t = tangent_component(foreground_axis, background_correction)
n = normal_component(foreground_axis, background_correction)
print("Tangent component:", t, ", Normal component:", n)
restored = vector_sum(t, n)
print("Restored:", restored)
delta = difference(background_correction, restored)

print ("Check:", delta)




tangential_ratio = tangential_ratio(background, foreground, highglight_background)
print('Tangential ratio', tangential_ratio)

normal_ratio = normal_ratio(background, foreground, highglight_background)
print('Normal ratio', normal_ratio)


print ('Normalized length:', sqrt(tangential_ratio ** 2 + normal_ratio ** 2))
print ('Expected normalized length:', magnitude(difference(highglight_background, background)) / magnitude(difference(foreground, background)))
