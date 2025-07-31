# Mechanical Vibration Tools

## Introduction
The idea for this project originated in a Machine Dynamics
course, where the goal was to visualize the frequency-response
functions of single-degree-of-freedom systems. 
Having already implemented several utility routines, I decided to package and share them.

This library is organized into two main modules—one for single-degree-of-freedom
(1-DOF) systems and another for multi-degree-of-freedom 
(n-DOF) systems. It ranges from simple functions such as:

- `get_natural_frequency(mass, stiffness)`: accepts two parameters and returns the natural frequency of a 1-DOF system,

to more advanced routines like:

- `get_natural_modes_of_vibration(mode_shapes, natural_frequencies, coefficients, phases)`: accepts four parameters and returns the time-dependent contribution of each mode in an n-DOF system’s response.

This README is organized as follows:  
1. **Installation** – how to install the package.  
2. **Technologies Used** – an overview of the key libraries and tools.  
3. **Modules** – detailed explanations of `n_dof_calc.py` and `one_dof_calc.py`.  
4. **Examples** – showcase of various usages with Matplotlib. 
5. **License** - Details of the license 
6. **Disclaimer & Author** – a disclaimer and my author information.  
---

## 1. **Installation**

You can install the package directly from [PyPI](https://pypi.org/project/mec-vibrations-calcs/) using **pip**:

```bash
pip install mec_vibrations_calcs
```
---
## 2. **Technologies Used**

An overview of the key libraries and tools that make this project possible:

- [Python](https://www.python.org/) >= 3.8  
- [NumPy](https://numpy.org/) – efficient numerical computations  
- [SciPy](https://scipy.org/) – advanced scientific computing and linear algebra tools 
- [Matplotlib](https://matplotlib.org/) – data visualization and plotting  
- [Hatchling](https://hatch.pypa.io/) – build system for packaging  
- [Twine](https://twine.readthedocs.io/) – uploading distributions to PyPI

---
## 3. **Modules**

## `one_dof_calc.py`


This module provides a collection of functions to analyze the dynamic behavior of **single-degree-of-freedom (1-DOF) systems** in vibration mechanics.  
It includes methods for calculating natural frequencies, damping ratios, frequency response functions, and time-domain responses.

---

###  Functions Overview

####  Frequency and Time Properties
- `get_natural_frequency(keq, meq)` → Returns the natural frequency of the system.
- `get_period(natural_frequency)` → Returns the natural period of vibration.

####  Damping and Resonance
- `get_dumping_ratio(ceq, meq, w_n)` → Computes the damping ratio.
- `get_log_decrement(dumping_ratio)` → Returns the logarithmic decrement.
- `get_resonance_frequency(w_natural, epsilon)` → Computes the resonance frequency.

####  Frequency Response Functions
- `get_recept(meq, ceq, keq, omega)` → Returns the receptance.
- `get_real_recept(meq, ceq, keq, omega)` → Real part of the receptance.
- `get_imaginary_recept(meq, ceq, keq, omega)` → Imaginary part of the receptance.
- `get_mobility(meq, ceq, keq, omega)` → Returns the mobility.
- `get_real_mobility(meq, ceq, keq, omega)` → Real part of the mobility.
- `get_imaginary_mobility(meq, ceq, keq, omega)` → Imaginary part of the mobility.
- `get_acelerance(meq, ceq, keq, omega)` → Returns the accelerance.
- `get_real_acelerance(meq, ceq, keq, omega)` → Real part of the accelerance.
- `get_imaginary_acelerance(meq, ceq, keq, omega)` → Imaginary part of the accelerance.

###  Time Response
- `get_natural_response(natural_frequency, dumping_ratio, init_deloc, init_vel, time)`  
  Returns the **free vibration response** depending on damping ratio (underdamped, critically damped, overdamped).

- `get_transitory_response_HE(...)` → Transient response under harmonic excitation.
- `get_permanent_response_HE(...)` → Steady-state response under harmonic excitation.
- `get_total_response_HE(...)` → Total response (transient + permanent).

###  Harmonic Excitation Analysis
- `get_amplitute_factor_HE(natural_frequency, dumping_ratio, omega)` → Amplitude factor for harmonic excitation.
- `get_force_transmissibility_HE(natural_frequency, dumping_ratio, omega)` → Force transmissibility.

---

###  Example Usage

```python
import matplotlib.pyplot as plt
from mec_vibrations_calcs.one_dof_calc import *

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

```
---

---

## `n_dof_calc.py` 

This module provides functions to perform **modal analysis** of mechanical vibration systems with **n degrees of freedom (n-DOF)**.  
It allows the calculation of natural frequencies, mode shapes, normalized modal vectors, modal coefficients, phases, and time responses.

---

### Functions Overview

####  `get_natural_frequencies(K, M)`
Computes the natural frequencies of the system.  
- **Input:** stiffness matrix `K`, mass matrix `M`  
- **Output:** sorted array of natural frequencies  



####  `get_modes_shapes(K, M)`
Computes the mode shapes of the system.  
- **Input:** stiffness matrix `K`, mass matrix `M`  
- **Output:** mode shapes matrix (columns = modes, normalized to first element = 1)  



####  `get_normal_modal_vectors(modeShapes, M)`
Computes normalized modal vectors considering the mass matrix.  
- **Input:** mode shapes, mass matrix  
- **Output:** normalized modal vectors  



#### `get_coef_resp_natural(normal_modal_vectors, natural_frequencies, M, desloc_init, vel_init)`
Computes modal coefficients (amplitudes) from initial displacement and velocity.  
- **Input:** modal vectors, natural frequencies, mass matrix, initial displacement, initial velocity  
- **Output:** coefficients `c[i]` for each mode  



####  `get_modal_phases(normal_modal_vectors, natural_frequencies, M, desloc_init, vel_init)`
Computes the phase of each mode.  
- **Input:** same as above  
- **Output:** phase angles (radians)  



#### `get_natural_modes_of_vibration(normal_modal_vectors, natural_frequencies, coef, phase)`
Generates the **modal response in time** for each mode.  
- Returns a function `x_of_t(time)` that computes the displacement of each mode at given times.  
- **Supports:**  
  - `time` as a scalar (float) → instantaneous response  
  - `time` as a numpy array → full time history  
  - **Output format:**  
The returned response is a matrix where:  
    - Each **row** corresponds to one **degree of freedom (DOF)**  
    - Each **column** corresponds to one **natural mode of vibration**  



#### `get_total_natural_response(natural_modes_in_time)`
Computes the **total system response** by summing all modal contributions.  
- **Input:** modal responses in time (2D or 3D array)  
- **Output:** total displacement response  
 
  The returned response is a matrix where:  
    - Each **row** corresponds to one **degree of freedom (DOF)**  
    - Each **column** corresponds to one **natural mode of vibration** 
---

##  Example Usage

```python
import matplotlib.pyplot as plt
from mec_vibrations_calcs.n_dof_calc import *

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

print('---------------------------------------')

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

```


## 4. Possibilities

### 1. Amplitude Factor for Harmonic Excitation  
![Amplitude Factor](tests/images/Amplitude%20factor%20for%20harmonic%20excitation.png)  

### 2. Permanent Response Example  
![Permanent Response](tests/images/Example%20of%20Permanent%20Response.png)  

### 3. Real Part of Receptance  
![Real Part of Receptance](tests/images/Example%20of%20real%20Parte%20of%20receptance.png)  

### 4. Receptance Curve  
![Receptance](tests/images/Example_receptance.png)  

### 5. Force Transmissibility  
![Force Transmissibility](tests/images/Force%20Transmissibility%20for%20harmonic%20excitation.png)  

### 6. Natural Response – 2 DOF  
![1 DOF](tests/images/N%20degree%20of%20freedom,%201%20degree.png)  

### 7. Natural Response – 2 DOF  
![2 DOF](tests/images/N%20degree%20of%20freedom,%202%20degree.png)  

### 8. Natural Response Example – Two Dumpings  
![Two Dumpings](tests/images/Natural%20Response%20Example%20for%20two%20dumpings.png)  

### 9. Natural Response Example – Two Dumpings (Variation)  
![Two Dumpings 2](tests/images/Natural%20Response%20Example%20for%20two%20dumpings_2.png)  



------------------------------------------------

## 5. **License**

This project is licensed under the [MIT License](LICENSE).  
You are free to use, modify, and distribute this project in accordance with the terms of the license.
 
---



## 6. **Disclaimer & Author**

This module was developed for academic and study purposes.  
I have performed some tests to validate the functions, but **there is no guarantee that all results are 100% correct or suitable for every practical application**.  
Users are encouraged to review the calculations and validate the results before applying them to critical engineering problems.  

If you are reading this and have ideas for improvements or suggestions, please feel free to contact me.  

**Author:** Igor Michalawiski Machado  
Email: immachad752@gmail.com  
LinkedIn: [Igor Machado](https://www.linkedin.com/in/igor-machado-eng/)
