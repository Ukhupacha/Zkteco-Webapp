import locale

import numpy as np
import matplotlib.pyplot as plt
import july
from july.utils import date_range
import datetime
locale.setlocale(locale.LC_TIME, 'es_PE')

dates = date_range("2020-01-01", "2020-02-24")
data = np.random.randint(0, 14, len(dates))
# GitHub Activity like plot (for someone with consistently random work patterns).

stuff = july.heatmap(dates, data, title='Github Activity', cmap="github")
d = datetime.datetime.now()
print(d.strftime("%a %d.%m.%Y"))

plt.axes(stuff)
plt.show()