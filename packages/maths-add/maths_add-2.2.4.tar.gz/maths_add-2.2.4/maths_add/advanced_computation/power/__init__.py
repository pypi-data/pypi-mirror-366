#encoding:utf-8
from maths_add.except_error import decorate

@decorate()
def powerTion(*args):
	power=args[0]
	if power==1:
		return 1
	args=list(args)
	args.remove(power)
	for i in args:
		power=power**i
	return power


