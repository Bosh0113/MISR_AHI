import math
import numpy as np
import matplotlib.pyplot as plt


ray_values = [2, 395, 0, 0, 5, 244, 0, 0, 211, 7, 430, 0, 10, 0, 1, 0, 0]
raa_values = [1, 305, 3, 4, 79, 1345, 7, 8, 334, 132, 699, 126, 87, 14, 19, 16, 1]
# values = np.sort(values)
# ray_values = ray_values[::-1]
# raa_values = raa_values[::-1]

# MCD12Q1 labels
lc_labels = [
    'Water', 'Evergreen Needleleaf Forest', 'Evergreen Broadleaf Forest', 'Deciduous Needleleaf Forest', 'Deciduous Broadleaf Forest', 'Mixed Forests', 'Closed Shrublands', 'Open Shrublands', 'Woody Savannas', 'Savannas', 'Grasslands',
    'Permanent Wetlands', 'Croplands', 'Urban and Built-Up', 'Cropland/Natual Vegation', 'Snow and Ice', 'Barren'
]
# colormap
lc_colormap = ['#82D3FE', '#4B9347', '#5CD250', '#A0D353', '#9AFF97', '#84B480', '#F897D0', '#F4DEB9', '#EFE784', '#BBA337', '#EEAA59', '#649FDD', '#FBF271', '#FF3334', '#9B7140', '#CCFFFF', '#BFBFBF']

value_max = 1500

theta_internal = 0.01
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
fig.set_size_inches(6, 4)
fig.set_dpi(100)

for v_idx in range(len(ray_values)):
    # y-grid line
    ax.plot(np.arange(0, 2 * np.pi * 3 / 4, theta_internal), np.ones((len(np.arange(0, 2 * np.pi * 3 / 4, theta_internal)), )) * (v_idx + 1), linestyle=(5, (10, 3)), linewidth=1, alpha=0.5, color=lc_colormap[v_idx])
    # ray-value
    value = ray_values[v_idx]
    line_angle = (value / value_max) * (2 * np.pi * 3 / 4)
    theta = np.arange(0, line_angle, theta_internal)
    r = np.ones((len(np.arange(0, line_angle, theta_internal)), )) * (v_idx + 1)
    ax.plot(theta, r, color=lc_colormap[v_idx], linewidth=12)
    # raa-value
    value = raa_values[v_idx]
    line_angle = (value / value_max) * (2 * np.pi * 3 / 4)
    theta = np.arange(0, line_angle, theta_internal)
    r = np.ones((len(np.arange(0, line_angle, theta_internal)), )) * (v_idx + 1)
    ax.plot(theta, r, color=lc_colormap[v_idx], alpha=0.7, linewidth=12)

ax.set_theta_offset(np.pi / 2)
x_major_locator = plt.MultipleLocator(1/6 * np.pi)
y1_major_locator = plt.MultipleLocator(value_max)
ax.xaxis.set_major_locator(x_major_locator)
ax.tick_params(axis="x", which='major', length=5, labelsize=10)
ax.yaxis.set_major_locator(y1_major_locator)
ax.set_thetamax(3 / 4 * 360)
theta_array = np.arange(0, (2 * np.pi * 3 / 4) + 1/7 * np.pi, 1/6 * np.pi)
theta_maj_labels = np.arange(0, value_max + value_max/3, value_max/3)
label90 = r'$' + str(round(int(theta_maj_labels[1])/math.pow(10, len(str(int(theta_maj_labels[1])))-1), 2)) + 'x10^' + str(len(str(int(theta_maj_labels[1])))-1) + '$'
label180 = r'$' + str(round(int(theta_maj_labels[2])/math.pow(10, len(str(int(theta_maj_labels[2])))-1), 2)) + 'x10^' + str(len(str(int(theta_maj_labels[2])))-1) + '$'
label270 = r'$' + str(round(int(theta_maj_labels[3])/math.pow(10, len(str(int(theta_maj_labels[3])))-1), 2)) + 'x10^' + str(len(str(int(theta_maj_labels[3])))-1) + '$'
theta_labels = ['Count of Pixels: 0', '', '', label90, '', '', label180, '', '', label270]
ax.set_xticks(theta_array, theta_labels)

labels = []
angles = [0, 0, 0, -90, 0, 0, 0, 0, 0, 0]
offset_idx = -1
offset_x = [0.25, 0, 0, 0, 0, 0, 0, 0, 0, -0.05]
offset_y = [0.04, 0, 0, 0.06, 0, 0, 0.06, 0, 0, 0.1]
for label, angle in zip(ax.get_xticklabels(), angles):
    offset_idx += 1
    x, y = label.get_position()
    lab = ax.text(x + offset_x[offset_idx], y + offset_y[offset_idx], label.get_text(), transform=label.get_transform(), ha=label.get_ha(), va=label.get_va())
    lab.set_rotation(angle)
    labels.append(lab)
ax.set_xticklabels([])
ax.spines["polar"].set_visible(False)

ax.set_rticks(np.arange(1, 18, 1), lc_labels)
ax.set_rlabel_position(0)

ax.grid(linestyle='--', linewidth=0.6, axis='x')
ax.yaxis.grid(False)

plt.show()