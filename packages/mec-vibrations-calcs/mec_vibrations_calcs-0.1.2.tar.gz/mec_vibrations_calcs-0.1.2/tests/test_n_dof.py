import matplotlib.pyplot as plt
from src.mec_vibrations_calcs.n_dof_calc import *

k = np.array([
    [1000, 0],
    [0, 5000 * 0.5 ** 2],
])
m = np.array([
    [4, 0.5],
    [0.5, 1.5 * 0.5 ** 2]
])

# Initial conditions
desloc_init = np.array([0.01, 0])
vel_init = np.array([0, 0])

# time definition for grafics
time = np.linspace(0, 3, 100000)
# time = 0.5
# print(type(time))

natural_freq = get_natural_frequencies(k, m)
# print(natural_freq)

modeShapes = get_modes_shapes(k, m)
# print(modeShapes)

normal_modeShapes_vect = get_normal_modal_vectors(modeShapes, m)
# print(normal_modeShapes_vect)

coef = get_coef_resp_natural(normal_modeShapes_vect, natural_freq, m, desloc_init, vel_init)
# print(coef.shape)

phases = get_modal_phases(normal_modeShapes_vect, natural_freq, m, desloc_init, vel_init)
# print(phases)

modeShapes_in_time = get_natural_modes_of_vibration(normal_modeShapes_vect, natural_freq, coef, phases)
# print(modeShapes_in_time(time).shape)


total_natural_response = get_total_natural_response(modeShapes_in_time(time))


plt.figure(figsize=(10, 6))
plt.plot(time, modeShapes_in_time(time)[0][0], label=f'Effect of First mode of Vibration', color='blue', alpha=0.6,
         linestyle='--')
plt.plot(time, modeShapes_in_time(time)[1][0], label=f'Effect of Second mode of Vibration', color='red', alpha=0.6,
         linestyle='--')
plt.plot(time, total_natural_response[0], label=f'Total natural response of the system', color='green', alpha=0.8,
         linewidth=2)
plt.xlabel('$t$')
plt.ylabel('$x_{1}(t)$')
plt.title('First degree of freedom')
plt.grid(True)
plt.axhline(0, color='gray', linewidth=0.5)
plt.axvline(0, color='gray', linewidth=0.5)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(time, modeShapes_in_time(time)[1][0], label=f'Effect of First mode of Vibration', color='blue', alpha=0.8,
         linestyle='--')
plt.plot(time, modeShapes_in_time(time)[1][1], label=f'Effect of Second mode of Vibration', color='red', alpha=0.6,
         linestyle='--')
plt.plot(time, total_natural_response[1], label=f'Total natural response of the system', color='green',
         linewidth=2, alpha=0.8)
plt.xlabel('$t$')
plt.ylabel('$x_{1}(t)$')
plt.title('Second degree of freedom')
plt.grid(True)
plt.axhline(0, color='gray', linewidth=0.5)
plt.axvline(0, color='gray', linewidth=0.5)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()
