import numpy as np
import matplotlib.pyplot as plt

value_max = 1500

ray_values = [2, 395, 0, 0, 5, 244, 0, 0, 211, 7, 430, 0, 10, 0, 1, 0, 0]
raa_values = [1, 305, 3, 4, 79, 1345, 7, 8, 334, 132, 699, 126, 87, 14, 19, 16, 1]
# values = np.sort(values)
ray_values = ray_values[::-1]
raa_values = raa_values[::-1]

# MCD12Q1 labels
lc_labels = ['Water', 'Evergreen Needleleaf Forest', 'Evergreen Broadleaf Forest', 'Deciduous Needleleaf Forest', 'Deciduous Broadleaf Forest', 'Mixed Forests', 'Closed Shrublands', 'Open Shrublands', 'Woody Savannas', 'Savannas', 'Grasslands', 'Permanent Wetlands', 'Croplands', 'Urban and Built-Up', 'Cropland/Natual Vegation', 'Snow and Ice', 'Barren']
# colormap
lc_colormap = ['#82D3FE', '#4B9347', '#5CD250', '#A0D353', '#9AFF97', '#84B480', '#F897D0', '#F4DEB9', '#EFE784', '#BBA337', '#EEAA59', '#649FDD', '#FBF271', '#FF3334', '#9B7140', '#FFFFFF', '#BFBFBF']

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
for v_idx in range(len(ray_values)):
   # y-grid line
   ax.plot(np.arange(0, 2*np.pi*3/4, 0.01), np.ones((len(np.arange(0, 2*np.pi*3/4, 0.01)),))*(v_idx+1), linestyle=(5, (10, 3)), linewidth=1, alpha=0.5, color=lc_colormap[v_idx])
   # ray-value
   value = ray_values[v_idx]
   line_angle = (value/value_max)*(2*np.pi*3/4)
   theta = np.arange(0, line_angle, 0.01)
   r = np.ones((len(np.arange(0, line_angle, 0.01)),))*(v_idx+1)
   ax.plot(theta, r, color=lc_colormap[v_idx], linewidth=12)
   # raa-value
   value = raa_values[v_idx]
   line_angle = (value/value_max)*(2*np.pi*3/4)
   theta = np.arange(0, line_angle, 0.01)
   r = np.ones((len(np.arange(0, line_angle, 0.01)),))*(v_idx+1)
   ax.plot(theta, r, color=lc_colormap[v_idx], alpha=0.7, linewidth=12)

ax.set_theta_offset(np.pi/2)
x_major_locator = plt.MultipleLocator(0.125*np.pi)
y1_major_locator = plt.MultipleLocator(value_max)
ax.xaxis.set_major_locator(x_major_locator)
ax.yaxis.set_major_locator(y1_major_locator)
ax.set_thetamax(3/4*360)
ax.grid(linestyle='--', linewidth=0.6, axis='x')

ax.set_title("A line plot on a polar axis", va='bottom')
plt.show()