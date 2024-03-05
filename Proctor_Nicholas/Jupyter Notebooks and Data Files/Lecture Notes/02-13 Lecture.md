This was a plot of the data we collected in class with error bars and theoretical results given by the following code block. As shown below, uncertainty and statistics can deceptive as the perceived uncertainty given by data is unlikely to match completely with the actual uncertainty. A consistent trend in uncertainty may often be a result of systematic uncertainty as opposed to random uncertainty.

![[Pasted image 20240213120723.png]]
```
# Plot data with error bars
height, time, height_err, time_err  = np.loadtxt('DataPhys.csv', delimiter = ',', skiprows = 1, usecols = (0, 1, 2, 3), unpack = True)
fig, ax = plt.subplots(figsize=(7, 4))
ax.errorbar(height, time, xerr=height_err, yerr=time_err, marker='o', markersize=4, linestyle='none')

height_t = np.linspace(0, 2.5, 100)  #Feel free to change these numbers
g = 9.81 #Don't include units in Python - it will cause an error
time_t = np.sqrt(2/g*height_t)

fig, ax = plt.subplots(figsize=(7, 4))
ax.errorbar(height, time, xerr=height_err, yerr=time_err, marker='o', markersize=3, linestyle='none')
ax.plot(height_t, time_t, '-')
plt.show()
```