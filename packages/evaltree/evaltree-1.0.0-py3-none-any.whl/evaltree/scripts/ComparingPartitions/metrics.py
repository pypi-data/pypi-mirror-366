#!/usr/bin/env	python3

"""
Functions of comparing_partitions.py (May 2021)
original github repository: https://github.com/jacarrico/ComparingPartitions
For research purposes, this script was modified in order to comprise additional metrics

By Veronica Mixao 
@INSA
"""


import numpy as np
import math
from sklearn.metrics.cluster import adjusted_rand_score


# Original Metrics code by Peter Kruczkiewicz (https://github.com/peterk87)
# National Microbiology Laboratory at Lethbridge, Public Health Agency of Canada, Lethbridge, Alberta, Canada. 
# https://gist.github.com/jacarrico/82c32d05e90f43dec2b446cdb1ed46c6


def getContTable(ar1, ar2):
	cont = {}
	for i in range(0, len(ar1)):
		keyAr1 = ar1[i]
		keyAr2 = ar2[i]
		if keyAr1 in cont:
			if keyAr2 in cont[keyAr1]:
				cont[keyAr1][keyAr2] += 1
			else:
				cont[keyAr1][keyAr2] = 1
		else:
			cont[keyAr1] = {keyAr2: 1}
	return cont


def getContTableTotals(cont, ar1, ar2):
	sumRow = {}
	sumCol = {}
	h1 = set(ar1)
	h2 = set(ar2)
	for x in h2:
		sumRow[x] = 0
		for y in h1:
			if y in cont:
				if x in cont[y]:
					val = cont[y][x]
					sumRow[x] += val
					if y in sumCol:
						sumCol[y] += val
					else:
						sumCol[y] = val
	total = 0
	for x in h1:
		total += sumCol[x]
	return (sumRow, sumCol, total)


def getMismatchMatrix(cont, ar1, ar2):
	totals = getContTableTotals(cont, ar1, ar2)
	# print(totals)
	n = totals[2]
	h1 = set(ar1)
	h2 = set(ar2)
	a = 0
	for x in h1:
		for y in h2:
			if x in cont:
				if y in cont[x]:
					val = cont[x][y]
					a += (val * (val - 1)) / 2
	a1 = 0
	sumCol = totals[1]
	for x in sumCol:
		val = sumCol[x]
		a1 += (val * (val - 1)) / 2

	b = a1 - a

	a2 = 0
	sumRow = totals[0]
	for x in sumRow:
		val = sumRow[x]
	a2 += (val * (val - 1)) / 2
	c = a2 - a
	d = float((n * (n - 1)) / 2) - a1 - c
	return (a, b, c, d, n)


def getRand(a, b, c, d):
	rand = (a + d) / float(a + b + c + d)
	return rand


def	getAdjRand(a,b):
	adj_rand = adjusted_rand_score(a,b)
	return adj_rand


def getWallace(a, b, c):
	w1 = float(0)
	w2 = float(0)
	if (a + b) > 0:
		w1 = a / float(a + b)
	if (a + c) > 0:
		w2 = a / float(a + c)
	return (w1, w2)


def getSimpsons(ar):
	n = len(ar)
	d = {}
	for x in ar:
		if x in d:
			d[x] += 1
		else:
			d[x] = 1

	sumTotal = 0
	sumFc2 = 0
	sumFc3 = 0
	for x in d:
		val = d[x]
		sumTotal += val * (val - 1)
		sumFc2 += (val / float(n)) ** 2.0
		sumFc3 += (val / float(n)) ** 3.0

	sid = 1.0
	if n * (n - 1) > 0:
		sid = 1.0 - (sumTotal / float(n * (n - 1)))

	sqSumFc2 = sumFc2 ** 2.0
	s2 = (4.0 / float(n)) * float(sumFc3 - sqSumFc2)
	
	if s2 <= 0:
		sidLow = "-"
		sidHigh = "-"
	else:
		sidLow = sid - 2 * math.sqrt(s2)
		sidHigh = sid + 2 * math.sqrt(s2)

	return (sid, sidLow, sidHigh, len(d))


def getAdjustedWallace(cont, ar1, ar2):
	sumCol, sumRow, totals = getContTableTotals(cont, ar1, ar2)
	rSumW1 = 0
	rSumW2 = 0
	# For Rows
	for i in cont:
		rSum = sumRow[i]
		rsumFc2 = 0
		rsumFc3 = 0
		for j in cont[i]:
			val = cont[i][j]
			#print('i',i,'j',j,'val',val)
			cSum = sumCol[j]
			rsumFc2 += (val / float(rSum)) ** 2.0
			rsumFc3 += (val / float(rSum)) ** 3.0

		rsqrsumFc2 = rsumFc2 ** 2.0
		rvarSID = 0.0
		if rSum > 1:
			rvarSID = float(4.0 * rSum * (rSum - 1.0) * (rSum - 2.0) * rsumFc3 + 2.0 * rSum * (rSum - 1.0) * rsumFc2 - 2.0 * rSum * (rSum - 1.0) * (2.0 * rSum - 3.0) * rsqrsumFc2) / float((rSum * (rSum - 1.0)) ** 2.0)
		rSumW1 += float((rSum * (rSum - 1.0)) ** 2.0) * rvarSID
		rSumW2 += rSum * (rSum - 1.0)

	varW1 = 0.0
	if rSumW2 > 0:
		varW1 = float(rSumW1 / float(float(rSumW2) ** 2.0))

	csumw1 = 0
	csumW2 = 0
  

	a, b, c, d, n = getMismatchMatrix(cont, ar1, ar2)
	w1, w2 = getWallace(a, b, c)

	sid1 = getSimpsons(ar1)
	sid2 = getSimpsons(ar2)

	wi1 = 1 - sid1[0]
	wi2 = 1 - sid2[0]
	
	if float(1 - wi2) > 0:
		aw1 = float(w1 - wi2) / float(1 - wi2)
		aw1CI = 2.0 * (1.0 / float(1.0 - wi2)) * math.sqrt(varW1)
		aw1Low = aw1 - aw1CI
		aw1High = aw1 + aw1CI
		return (aw1, aw1Low, aw1High)
	else:
		return (0, 0, 0)
