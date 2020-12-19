import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import math
from scipy.stats import poisson

def C(q,z):
    if z<0 or q>=0.5:
        prob = 1
    else:
        prob = (q/(1-q)) ** (z+1)
    return prob

def P_N(q,m,n):
    return poisson.pmf(n, m*q/(1-q))

def DS_N(q,K):
    return 1-sum(P_N(q,K,n)*(1-C(q,K-n-1)) for n in range(0,K+1))

def doublespendfun(x, n, z, A, k, v):
    out = [v*DS_N(float(q_value), k) for q_value in x]
        
    return out

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.35)

n = 1 # 1->10 000
z = 1 # 1->20
A = 5 # 1->10
k = 1 # 0->5
v = 1 # 0->5

x = np.arange(0.0, 1.0, 0.01)
y = doublespendfun(x, n, z, A, k, v)

l, = plt.plot(x, y, lw=2)
ax.margins(x=0)

axn = plt.axes([0.25, 0.25, 0.65, 0.03])
axz = plt.axes([0.25, 0.20, 0.65, 0.03])
axA = plt.axes([0.25, 0.15, 0.65, 0.03])
axk = plt.axes([0.25, 0.10, 0.65, 0.03])
axv = plt.axes([0.25, 0.05, 0.65, 0.03])


"""
n = 1 # 1->10 000
q = 0.5 # 0->1
z = 1 # 1->20
A = 5 # 1->10
k = 1 # 0->5
v = 1 # 0.1->1
"""

sn = Slider(axn, 'n', 1, 100, valinit=1, valstep=1)
sz = Slider(axz, 'z', 1, 20, valinit=1, valstep=1)
sA = Slider(axA, 'A', 1, 10, valinit=5, valstep=1)
sk = Slider(axk, 'k', 0, 5, valinit=1, valstep=1)
sv = Slider(axv, 'v', 0.1, 1.0, valinit=0.2, valstep=0.1)


def update(val):
    n = sn.val
    z = sz.val
    A = sA.val
    k = sk.val
    v = sv.val

    x = np.arange(0.0, 1.0, 0.01)
    l.set_ydata(doublespendfun(x, n, z, A, k, v))
    
    fig.canvas.draw_idle()


sn.on_changed(update)
sz.on_changed(update)
sA.on_changed(update)
sk.on_changed(update)
sv.on_changed(update)


plt.show()
