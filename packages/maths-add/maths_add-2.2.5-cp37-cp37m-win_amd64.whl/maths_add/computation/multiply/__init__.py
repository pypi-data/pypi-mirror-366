#encoding:utf-8
from maths_add.except_error import decorate

@decorate()
def multiplyTion(*args):
	product=1
	for i in args:
		product*=i
	return product
