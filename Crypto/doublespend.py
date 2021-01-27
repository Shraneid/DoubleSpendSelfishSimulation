import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import random


coinbase_reward = 6.25  # actual BTC reward


def doublespendfun(q_values, n, z, A, k, v):
    out = []
    for q in q_values:
        double_spend_strategy_winnings = 0
        honest_winnings = 0

        for i in range(n):
            main_chain = 0
            hidden_chain = k
            while hidden_chain - main_chain > -A and not (hidden_chain > main_chain >= z):
                if random.random() < q:
                    hidden_chain += 1
                if random.random() < 1 - q:
                    main_chain += 1

            if hidden_chain > main_chain:
                double_spend_strategy_winnings += v + hidden_chain * coinbase_reward

            honest_winnings += (main_chain + hidden_chain) * coinbase_reward * q

        out.append((double_spend_strategy_winnings / n) / (honest_winnings/n))

    return out


fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.35)

n = 100  # 100->10 000 nb of attack cycles
z = 8  # 1->20 number of blocks to validate tx
A = 1  # 1->10 maximum delay
k = 1  # 0->5 premined blocks
v = 1  # 0->5 value in coinbase

x = np.arange(0.0, 0.5, 0.02)
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

sn = Slider(axn, 'n', 100, 1000, valinit=500, valstep=1)
sz = Slider(axz, 'z', 1, 20, valinit=8, valstep=1)
sA = Slider(axA, 'A', 1, 10, valinit=5, valstep=1)
sk = Slider(axk, 'k', 0, 10, valinit=1, valstep=1)
sv = Slider(axv, 'v', 1.0, 50.0, valinit=6.25, valstep=0.5)


def update(val):
    n = int(sn.val)
    z = int(sz.val)
    A = int(sA.val)
    k = int(sk.val)
    v = float(sv.val)

    l.set_ydata(doublespendfun(x, n, z, A, k, v))

    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()


sn.on_changed(update)
sz.on_changed(update)
sA.on_changed(update)
sk.on_changed(update)
sv.on_changed(update)

plt.show()
