import math
import numpy as np
from typing import Union


def get_natural_frequency(keq, meq):
    """
        Calculate the natural frequency of an vibration system.

        The natural frequency is a fundamental property of the system that determines
        the oscillation frequency when there is no damping or external forces.

        Args:
            keq (float): Equivalent stiffness of the system [N/m]
            meq (float): Equivalent mass of the system [kg]

        Returns:
            float: Natural frequency of the system [rad/s]

        Formula:
            ωn = √(k/m)
        """
    w_natural = np.sqrt(keq / meq)
    return w_natural


def get_dumping_ratio(ceq, meq, w_n):
    """
        Calculate the damping ratio of the system.

        The damping ratio determines the system's response behavior:
        - ζ < 1: Underdamped system (oscillates with decreasing amplitude)
        - ζ = 1: Critically damped system (no oscillation, returns quickly)
        - ζ > 1: Overdamped system (no oscillation, returns slowly)

        Args:
            ceq (float): Equivalent damping coefficient [N·s/m]
            meq (float): Equivalent mass of the system [kg]
            w_n (float): Natural frequency of the system [rad/s]

        Returns:
            float: Damping ratio [dimensionless]

        Formula:
            ζ = c/(2·m·ωn)
        """
    epsilon = ceq / (2 * meq * w_n)
    return epsilon


def get_resonance_frequency(w_natural, epslon):
    """
        Calculate the resonance frequency of a damped system.

        The resonance frequency is slightly lower than the natural frequency
        due to the damping effect. It's the frequency where maximum amplitude
        response occurs in forced vibration.

        Args:
            w_natural (float): Natural frequency of the system [rad/s]
            epslon (float): Damping ratio [dimensionless]

        Returns:
            float: Resonance frequency [rad/s]

        Formula:
            ωr = ωn·√(1 - 2ζ²)

        Note:
            Valid only for ζ < 1/√2 ≈ 0.707
        """
    w_resonance = w_natural * np.sqrt(1 - 2 * epslon ** 2)
    return w_resonance


def get_recept(meq, ceq, keq, omega):
    """
        Calculate the receptance (frequency response function) of the system.

        Receptance relates the output displacement to the input force
        in the frequency domain. It's a complex function containing
        amplitude and phase information of the response.

        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            complex: Complex receptance [m/N]

        Formula:
            α(ω) = 1/(-mω² + k + jωc)
        """
    alpha = 1 / ((keq - meq * omega ** 2) + 1j * omega * ceq)
    return alpha


def get_real_recept(meq, ceq, keq, omega):
    """
        Calculate the real part of the receptance.


        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            float: Real part of receptance [m/N]
        """
    real_part = (keq - meq * (omega ** 2)) / ((keq - meq * (omega ** 2)) ** 2 + (omega * ceq) ** 2)
    return real_part


def get_imaginary_recept(meq, ceq, keq, omega):
    """
        Calculate the imaginary part of the receptance.


        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            float: Imaginary part of receptance [m/N]
        """
    imaginaria_part = -(omega * ceq) / ((keq - meq * omega ** 2) ** 2 + (omega * ceq) ** 2)
    return imaginaria_part


def get_mobility(meq, ceq, keq, omega):
    """
        Calculate the mobility (velocity response function) of the system.

        Mobility relates the output velocity to the input force.

        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            complex: Complex mobility [m/s/N]

        Formula:
            Y(ω) = jω/(-mω² + k + jωc)
        """
    mob = (1j * omega) / ((keq - (omega ** 2) * meq) + 1j * omega * ceq)
    return mob


def get_real_mobility(meq, ceq, keq, omega):
    """
    Calculate the real part of mobility.

    Args:
        meq (float): Equivalent mass [kg]
        ceq (float): Equivalent damping [N·s/m]
        keq (float): Equivalent stiffness [N/m]
        omega (float): Excitation frequency [rad/s]

    Returns:
        float: Real part of mobility [m/s/N]
    """
    real_part = ((omega ** 2) * ceq) / (((keq - (omega ** 2) * meq) ** 2) + (omega * ceq) ** 2)
    return real_part


def get_imaginary_mobility(meq, ceq, keq, omega):
    """
        Calculate the imaginary part of mobility.

        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            float: Imaginary part of mobility [m/s/N]
        """
    imaginary = (omega * (keq - meq * (omega ** 2))) / (((keq - meq * (omega ** 2)) ** 2) + (omega * ceq) ** 2)
    return imaginary


def get_acelerance(meq, ceq, keq, omega):
    """
        Calculate the accelerance (acceleration response function) of the system.

        Accelerance relates the output acceleration to the input force.
        It's particularly useful in experimental measurements with accelerometers.

        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            complex: Complex accelerance [m/s²/N]

        Formula:
            A(ω) = -ω²/(-mω² + k + jωc)
        """
    acel = - (omega ** 2) / ((keq - meq * (omega ** 2)) + 1j * omega * ceq)
    return acel


def get_real_acelerance(meq, ceq, keq, omega):
    """
        Calculate the real part of accelerance.

        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            float: Real part of accelerance [m/s²/N]
        """
    real = - ((omega ** 2) * (keq - meq * (omega ** 2))) / (((keq - meq * (omega ** 2)) ** 2) + (omega * ceq) ** 2)
    return real


def get_imaginary_acelerance(meq, ceq, keq, omega):
    """
        Calculate the imaginary part of accelerance.

        Args:
            meq (float): Equivalent mass [kg]
            ceq (float): Equivalent damping [N·s/m]
            keq (float): Equivalent stiffness [N/m]
            omega (float): Excitation frequency [rad/s]

        Returns:
            float: Imaginary part of accelerance [m/s²/N]
        """
    imag = omega ** 3 * ceq / (((keq - meq * (omega ** 2)) ** 2) + (omega * ceq) ** 2)
    return imag


def get_period(natual_frequency):
    """
        Calculate the natural period of oscillation of the system.

        The period is the time required to complete one full oscillation cycle.

        Args:
            natual_frequency (float): Natural frequency [rad/s]

        Returns:
            float: Natural period [s]

        Formula:
            T = 2π/ωn
        """
    periodo = (2 * np.pi / natual_frequency)
    return periodo


def get_natural_response(
        natural_frequency: float,
        dumping_ratio: float,
        init_deloc: float,
        init_vel: float,
        time: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Calculate the natural (free) response of the system for different damping conditions.

    This function implements the analytical solutions of the differential equation
    of motion for free vibration with different types of damping.

    Args:
        natural_frequency (float): Natural frequency [rad/s]
        dumping_ratio (float): Damping ratio [dimensionless]
        init_deloc (float): Initial displacement [m]
        init_vel (float): Initial velocity [m/s]
        time (Union[float, np.ndarray]): Time value or time vector [s]

    Returns:
        Union[float, np.ndarray]: System response in time [m]
                                 Returns float if time is float, array if time is array

    Implemented cases:
        - ζ = 0: Undamped system (harmonic oscillation)
        - 0 < ζ < 1: Underdamped system (oscillation with exponential decay)
        - ζ = 1: Critically damped system
        - ζ > 1: Overdamped system
    """
    if dumping_ratio == 0:
        # Undamped system - simple harmonic oscillation
        a1 = init_deloc
        a2 = (init_vel / natural_frequency)
        a = math.sqrt((a1 ** 2) + (a2 ** 2))
        phi = math.atan(a2 / a1)
        response = a * np.cos(natural_frequency * time - phi)
        return response

    if 0 < dumping_ratio < 1:
        # Underdamped system - oscillation with exponential decay
        a1 = init_deloc
        a2 = (init_vel + dumping_ratio * natural_frequency * init_deloc) / (
                natural_frequency * math.sqrt(1 - dumping_ratio ** 2))
        a = np.sqrt((a1 ** 2) + (a2 ** 2))
        natural_dumped_frequency = natural_frequency * math.sqrt(1 - dumping_ratio ** 2)
        phi = np.atan(a2 / a1)
        response = a * np.exp(-dumping_ratio * natural_frequency * time) * np.cos(
            natural_dumped_frequency * time - phi)
        return response

    if dumping_ratio == 1:
        # Critically damped system
        response = (init_deloc + (init_vel + natural_frequency * init_deloc) * time) * np.exp(
            -natural_frequency * time)
        return response

    if dumping_ratio > 1:
        # Overdamped system - no oscillation
        a1 = init_deloc
        a2 = (init_vel + dumping_ratio * natural_frequency * init_deloc) / (
                natural_frequency * np.sqrt(dumping_ratio ** 2 - 1))
        part1 = np.cosh(natural_frequency * (np.sqrt((dumping_ratio ** 2)) - 1) * time)
        part2 = np.sinh(natural_frequency * (np.sqrt((dumping_ratio ** 2)) - 1) * time)
        response = np.exp(-dumping_ratio * natural_frequency * time) * (a1 * part1 + a2 * part2)
        return response


def get_log_decrement(dumping_ratio):
    """
       Calculate the logarithmic decrement of the system.

       The logarithmic decrement is an experimental measure of damping,
       calculated as the natural logarithm of the ratio between two
       successive oscillation amplitudes.

       Args:
           dumping_ratio (float): Damping ratio [dimensionless]

       Returns:
           float: Logarithmic decrement [dimensionless]

       Formula:
           δ = 2πζ/√(1-ζ²)

       Note:
           Valid only for underdamped systems (ζ < 1)
       """
    decrement = (2 * np.pi * dumping_ratio) / (np.sqrt(1 - dumping_ratio ** 2))
    return decrement


def get_transitory_response_HE(natural_frequency: float,
                               dumping_ratio: float,
                               init_deloc: float,
                               init_vel: float,
                               time: Union[float, np.ndarray[np.float64]]
                               ) -> np.ndarray[np.float64]:
    """
        Calculate the transient response for harmonic excitation.

        The transient response is the part of the solution that decays with time
        and depends on the initial conditions of the system.

        Args:
            natural_frequency (float): Natural frequency [rad/s]
            dumping_ratio (float): Damping ratio [dimensionless]
            init_deloc (float): Initial displacement [m]
            init_vel (float): Initial velocity [m/s]
            time (array): Time vector [s]

        Returns:
            array: Transient response [m]
    """
    return get_natural_response(natural_frequency, dumping_ratio, init_deloc, init_vel, time)


def get_permanent_response_HE(natural_frequency: float,
                              k: float,
                              f_ext: float,
                              dumping_ratio: float,
                              omega: float,
                              time: Union[float, np.ndarray[np.float64]]
                              ) -> np.ndarray[np.float64]:
    """
        Calculate the steady-state response for harmonic excitation.

        The steady-state response is the solution in steady state that persists
        after the transient response has decayed. It has the same frequency
        as the excitation force, but with different amplitude and phase.

        Args:
            natural_frequency (float): Natural frequency [rad/s]
            k (float): System stiffness [N/m]
            f_ext (float): External force amplitude [N]
            dumping_ratio (float): Damping ratio [dimensionless]
            omega (float): Excitation frequency [rad/s]
            time (array): Time vector [s]

        Returns:
            array: Steady-state response [m]

        Formula:
            x(t) = (F₀/k) · H(ω) · cos(ωt - φ)
            where H(ω) is the dynamic magnification factor
    """
    x_s = f_ext / k
    beta = omega / natural_frequency
    part1 = np.sqrt((1 - beta ** 2) ** 2 + (2 * dumping_ratio * beta) ** 2)
    part2 = x_s / part1
    phase = np.atan((2 * dumping_ratio * beta) / (1 - beta ** 2))
    response = part2 * np.cos(omega * time - phase)
    return response


def get_total_response_HE(
        natural_frequency: float,
        k: float,
        f_ext: float,
        dumping_ratio: float,
        omega: float,
        time: Union[float, np.ndarray[np.float64]],
        init_deloc: float,
        init_vel: float
) -> np.ndarray[np.float64]:
    """
        Calculate the total response for harmonic excitation.

        The total response is the sum of the transient response (which decays with time)
        and the steady-state response (which persists in steady state).

        Args:
            natural_frequency (float): Natural frequency [rad/s]
            k (float): System stiffness [N/m]
            f_ext (float): External force amplitude [N]
            dumping_ratio (float): Damping ratio [dimensionless]
            omega (float): Excitation frequency [rad/s]
            time (array): Time vector [s]
            init_deloc (float): Initial displacement [m]
            init_vel (float): Initial velocity [m/s]

        Returns:
            array: Total system response [m]

        Formula:
            x_total(t) = x_transient(t) + x_steady_state(t)
    """
    return get_transitory_response_HE(natural_frequency, dumping_ratio, init_deloc, init_vel,
                                      time) + get_permanent_response_HE(
        natural_frequency, k, f_ext, dumping_ratio, omega, time)


def get_amplitute_factor_HE(natural_frequency, dumping_ratio, omega):
    """
        Calculate the dynamic magnification factor (Dynamic Amplification Factor).

        The magnification factor indicates how many times the dynamic response
        amplitude is greater than the static displacement. It's fundamental for
        resonance analysis and vibratory system design.

        Args:
            natural_frequency (float): Natural frequency [rad/s]
            dumping_ratio (float): Damping ratio [dimensionless]
            omega (float): Excitation frequency [rad/s]

        Returns:
            float: Dynamic magnification factor [dimensionless]

        Formula:
            H(ω) = 1/√[(1-β²)² + (2ζβ)²]
            where β = ω/ωn is the frequency ratio
    """
    beta = omega / natural_frequency
    part1 = (1 - beta ** 2) ** 2
    part2 = (2 * beta * dumping_ratio) ** 2
    result = 1 / (np.sqrt(part1 + part2))
    return result


def get_force_transmissibility_HE(natural_frequency, dumping_ratio, omega):
    """
        Calculate the force transmissibility for harmonic excitation.

        Force transmissibility is the ratio of the force transmitted to the foundation
        to the applied force. It's crucial for vibration isolation design and
        evaluating the effectiveness of isolation systems.

        Args:
            natural_frequency (float): Natural frequency [rad/s]
            dumping_ratio (float): Damping ratio [dimensionless]
            omega (float): Excitation frequency [rad/s]

        Returns:
            float: Force transmissibility [dimensionless]

        Formula:
            TR = √[1 + (2ζβ)²]/√[(1-β²)² + (2ζβ)²]
            where β = ω/ωn is the frequency ratio

        Note:
            TR > 1: Amplification (poor isolation)
            TR < 1: Attenuation (good isolation)
            TR = 1: No isolation effect
    """
    beta = omega / natural_frequency
    part1 = np.sqrt(1 + (2 * beta * dumping_ratio) ** 2)
    part2 = np.sqrt((1 - beta ** 2) ** 2 + (2 * beta * dumping_ratio) ** 2)
    tr = part1 / part2
    return tr
