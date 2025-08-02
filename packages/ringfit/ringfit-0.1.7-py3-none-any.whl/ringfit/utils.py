import numpy as np
import itertools

def geometric_centroid(points):
    return points[:,0].mean(), points[:,1].mean()

def flux_center(data):
    h, w = data.shape
    yy, xx = np.indices((h, w))
    total = data.sum()
    return (xx*data).sum()/total, (yy*data).sum()/total

def threshold_center(data, q=25):
    thresh = np.percentile(data, q)
    mask = data >= thresh
    yy, xx = np.indices(data.shape)
    total = mask.sum()
    return xx[mask].sum()/total, yy[mask].sum()/total
