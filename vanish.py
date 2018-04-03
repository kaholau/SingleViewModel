import cv2 
import numpy as np
from numpy import linalg as LA
import scipy.sparse.linalg as sla
import argparse

#specify each line's endpoints e1 and e2 in homogeneous coordinates
#	e1 = (x1_i , y1_i, w)
#	e2 = (x2_i , y2_i, w)
#compute a homogenous coordinate vector representing the line
#   as the cross product of its two endpoints
#      (a_i,b_i,c_i) = e1  X  e2
#   note that this resulting vector is just the parameters of
#   the equation a_i x + b_i y + c_i = 0 of the 2D infinite line
#   passing through the two endpoints
def getLineVector(stpt,endpt, w):
	stpt.append(w)
	endpt.append(w)
	e1 = np.array(stpt, dtype='f')
	e2 = np.array(endpt, dtype='f')
	print(e1,e2)
	return np.cross(e1,e2)


#	a) form the 3x3 "second moment" matrix M as
#
#                [  a_i*a_i   a_i*b_i     a_i*c_i ]
#        M = sum [  a_i*b_i   b_i*b*i     b_i*c_i ]
#                [  a_i*c_i   b_i*c_i     c_i*c_i ]
#
#       where the sum is taken for i = 1 to n.  Note that M is
#       a symmetric matrix
#   b) perform an eigendecomposition of M, using the Jacobi
#      method, from numerical recipes in C, for example.  (Jacobi
#       method is good for finding eigenvalues of a symmetric matrix)
#       [I can supply the Jacobi matrix code from NR in C if you like]
#
#   c) the eigenvector associated with the smallest eigenvalue is
#      the vanishing point vector V

def computeVanishingPoint(imgH,imgW,linePtList):
	l = len(linePtList)
	w = float((imgH + imgW) / 4)
	print(imgH , imgW, 'w :',w)
	lines = []
	if l > 1 :
		for p in linePtList:
			lines.append(getLineVector(p[0], p[1], w))

		sumM = np.zeros((3,3))
		for l in lines:
			T = np.reshape(l, (3, 1))
			M = (T * l)
			print(M)
			sumM += M

		# Perform eigen decomposition and extract the eigen vector with the smallest eigen value. This corresponds to the vanishing point
		eigenValues, eigenVectors = sla.eigs(M, k=1, which='SM')
		eigenVectors = np.transpose(eigenVectors.real)
		# Convert coordinates into homogeneous form
		return (eigenVectors[-1]/eigenVectors[-1,-1])
		
	else:
		print('No enough Line for calculating vanishing point')
		return None 
