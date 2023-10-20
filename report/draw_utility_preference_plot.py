import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(9, 3))

fig.suptitle('Utility Preference Functions')

cost_preference_df = pd.DataFrame(
    [[0, 1], [10, 1], [10.01, 0.9], [20, 0.9], [20.01, 0.7], [30, 0.7], [30.01, 0.3], [80, 0.3], [80.01, 0], [90, 0]],
    columns=['Monthly Cost/USD', 'Utility Preference']
)
ax1 = sns.lineplot(data=cost_preference_df, x='Monthly Cost/USD', y='Utility Preference',
                   linewidth=2.5, ax=ax1)
ax1.grid()
ax1.set_xticks(ticks=range(0, 90, 10))
ax1.set_yticks(ticks=np.arange(0, 1.1, 0.1))
ax1.set_ylim(0, 1.05)
ax1.set_xlim(0, 85)

latency_preference_df = pd.DataFrame(
    [[0, 1], [100, 1], [100.01, 0.8], [200, 0.8], [200.01, 0.1], [300, 0.1], [300.01, 0], [400, 0]],
    columns=['latency/ms', 'Utility Preference']
)
ax2 = sns.lineplot(data=latency_preference_df, x='latency/ms', y='Utility Preference',
                   linewidth=2.5, ax=ax2)
ax2.grid()
ax2.set_xticks(ticks=range(0, 325, 100))
ax2.set_yticks(ticks=np.arange(0, 1.1, 0.1))
ax2.set_ylim(0, 1.05)
ax2.set_xlim(0, 325)


latency_preference_df = pd.DataFrame(
    [[100, 1], [99.9, 1], [99.899, 0.1], [99.5, 0.1], [99.499, 0], [99.4, 0]],
    columns=['success rate %', 'Utility Preference']
)
ax3 = sns.lineplot(data=latency_preference_df, x='success rate %', y='Utility Preference',
                   linewidth=2.5, ax=ax3)
ax3.grid()
ax3.set_xticks(ticks=np.arange(99.4, 100.1, 0.1))
ax3.set_yticks(ticks=np.arange(0, 1.1, 0.1))
ax3.set_ylim(0, 1.05)
ax3.set_xlim(99.4, 100)

fig.tight_layout()
plt.show()
