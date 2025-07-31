import matplotlib.pyplot as plt
from src.mec_vibrations_calcs.one_dof_calc import *

# Values for time
omega = np.linspace(0.1, 10, 100000)

# Sistem Parameters
m = 15  # mass
k = 15000  # stiffness constant
c1 = 9.48  # Dumping for system 1
c2 = 0  # # Dumping for system 2

# Natural Frequency
wn = get_natural_frequency(k, m)

# Dumping ratio System 1
eps1 = get_dumping_ratio(c1, m, wn)

# Dumping ratio System 2
eps2 = get_dumping_ratio(c2, m, wn)

# System response 1
nat_resp1 = get_natural_response(wn, eps1, 0.0001, 5, omega)

# System response 1
nat_resp2 = get_natural_response(wn, eps2, 0.5, 0, omega)

# Graphics

plt.figure(figsize=(10, 6))
plt.plot(omega, nat_resp1, label=f'Natural Response for system with dumping ratio = {eps1}', color='blue', alpha=0.8)
plt.plot(omega, nat_resp2, label=f'Natural Response for system with dumping ratio = {eps2}', color='green', alpha=0.6)
plt.xlabel('$t$')
plt.ylabel('$x(t)$')
plt.title('Natural response for vibration systems')
plt.grid(True)
plt.axhline(0, color='gray', linewidth=0.5)
plt.axvline(0, color='gray', linewidth=0.5)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()
