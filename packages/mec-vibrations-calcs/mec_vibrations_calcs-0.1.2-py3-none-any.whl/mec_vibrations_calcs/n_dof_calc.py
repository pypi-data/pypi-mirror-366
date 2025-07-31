import numpy
import numpy as np
from scipy.linalg import eigvals


def get_natural_frequencies(k, m):
    """
        Calculate the natural frequencies of a multi-degree-of-freedom (MDOF) system.

        This function solves the generalized eigenvalue problem for undamped free vibration
        to find the natural frequencies of the system. The eigenvalues represent the squares
        of the natural frequencies.

        Args:
            k (numpy.ndarray): Stiffness matrix [N/m] - shape (n, n)
            m (numpy.ndarray): Mass matrix [kg] - shape (n, n)

        Returns:
            numpy.ndarray: Natural frequencies sorted in ascending order [rad/s]

        Mathematical Background:
            The eigenvalue problem: det(K - λM) = 0
            Where λ = ω² (square of natural frequency)

        Note:
            - The function uses M⁻¹K formulation for computational efficiency
            - Results are sorted from lowest to highest frequency
            - Complex eigenvalues are converted to real if within tolerance
    """
    m_inv_k = np.linalg.inv(m) @ k
    lambda_ = eigvals(m_inv_k)
    lambda_ = lambda_
    natural_frequencies = lambda_ ** (1 / 2)
    natural_frequencies_real = np.real_if_close(natural_frequencies, tol=1)
    natural_frequencies_real.sort()
    return natural_frequencies_real


def get_modes_shapes(k, m):
    """
        Calculate the mode shapes (eigenvectors) of a multi-DOF system.

        Mode shapes represent the characteristic deformation patterns of the system
        at each natural frequency. Each mode shape is normalized so that the first
        element equals 1, providing a consistent reference for comparison.

        Args:
            k (numpy.ndarray): Stiffness matrix [N/m] - shape (n, n)
            m (numpy.ndarray): Mass matrix [kg] - shape (n, n)

        Returns:
            numpy.ndarray: Mode shapes matrix - shape (n, n)
                          Each column represents one mode shape

        Mathematical Background:
            From eigenvalue problem: (K - λᵢM)φᵢ = 0
            Where φᵢ is the i-th mode shape vector

        Normalization:
            Each mode shape is normalized so that φᵢ[0] = 1
            This provides a consistent reference for mode shape interpretation

        Note:
            - Mode shapes are sorted according to corresponding natural frequencies
            - The relative amplitudes between DOFs are more important than absolute values
            - Sign of mode shapes can be arbitrary (depends on eigenvector solver)
        """
    # Cálculo da matriz M⁻¹K
    m_inv_k = np.linalg.inv(m) @ k
    eigenvals, mode_shapes = np.linalg.eig(m_inv_k)

    # Ordena pelo menor autovalor (freq²)
    idx = np.argsort(eigenvals)
    mode_shapes_sorted = mode_shapes[:, idx]
    for j in range(mode_shapes_sorted.shape[1]):
        aux = mode_shapes_sorted[0, j]
        for i in range(mode_shapes.shape[0]):
            mode_shapes_sorted[i, j] = mode_shapes_sorted[i, j] / aux
    return mode_shapes_sorted


def get_normal_modal_vectors(modeShapes, m):
    """
        Calculate the mass-normalized modal vectors (normal modes).

        Normal modal vectors are mode shapes normalized with respect to the mass matrix
        such that φᵢᵀMφᵢ = 1. This normalization is essential for modal analysis
        as it simplifies the equations of motion in modal coordinates.

        Args:
            modeShapes (numpy.ndarray): Mode shapes matrix - shape (n, n)
            m (numpy.ndarray): Mass matrix [kg] - shape (n, n)

        Returns:
            numpy.ndarray: Mass-normalized modal vectors - shape (n, n)
                          Each column is a normal mode

        Mathematical Background:
            Normal mode: ψᵢ = φᵢ / √(φᵢᵀMφᵢ)
            Where: ψᵢᵀMψᵢ = 1 (mass orthogonality condition)
                   ψᵢᵀKψⱼ = ωᵢ²δᵢⱼ (stiffness orthogonality condition)

        Applications:
            - Modal analysis and modal superposition
            - Decoupling of equations of motion
            - Response calculation using normal coordinates

        Note:
            Normal modes satisfy both mass and stiffness orthogonality conditions,
            which allows the transformation to independent modal coordinates.
    """
    normal_modal_vector = np.zeros(modeShapes.shape)
    for i in range(modeShapes.shape[0]):  # itera sobre o numero de linhas que tem na matriz
        vector_aux1 = modeShapes[:, i].T
        vector_aux2 = vector_aux1 @ m @ modeShapes[:, i]
        normal_modal_vector[:, i] = modeShapes[:, i] / np.sqrt(vector_aux2)

    return normal_modal_vector


def get_coef_resp_natural(normal_modal_vectors, natural_frequencies, m, desloc_init, vel_init):
    """
        Calculate the modal response coefficients for free vibration analysis.

        These coefficients determine the amplitude of each mode's contribution
        to the total response based on initial conditions. They are essential
        for constructing the complete free vibration response.

        Args:
            normal_modal_vectors (numpy.ndarray): Mass-normalized modal vectors - shape (n, n)
            natural_frequencies (numpy.ndarray): Natural frequencies [rad/s] - shape (n,)
            m (numpy.ndarray): Mass matrix [kg] - shape (n, n)
            desloc_init (numpy.ndarray): Initial displacement vector [m] - shape (n,)
            vel_init (numpy.ndarray): Initial velocity vector [m/s] - shape (n,)

        Returns:
            numpy.ndarray: Modal amplitude coefficients [m] - shape (n,)

        Mathematical Background:
            For undamped free vibration: x(t) = Σᵢ Aᵢ cos(ωᵢt + φᵢ)
            Where: Aᵢ = √(a₁ᵢ² + (a₂ᵢ/ωᵢ)²)
                   a₁ᵢ = ψᵢᵀMx₀ (displacement contribution)
                   a₂ᵢ = ψᵢᵀMẋ₀ (velocity contribution)

        Physical Interpretation:
            - Higher coefficients indicate modes that are more excited by initial conditions
            - Coefficients depend on how well initial conditions match mode shapes
            - Zero coefficient means the mode is not excited

        Applications:
            - Free vibration response calculation
            - Mode participation factor analysis
            - Understanding which modes dominate the response
    """
    coef1 = np.zeros(normal_modal_vectors.shape[0])
    coef2 = np.zeros(normal_modal_vectors.shape[0])
    a = np.zeros(normal_modal_vectors.shape[0])
    for i in range(normal_modal_vectors.shape[0]):
        aux1 = normal_modal_vectors[:, i].T
        coef1[i] = aux1 @ m @ desloc_init
        coef2[i] = aux1 @ m @ vel_init
        a[i] = np.sqrt(coef1[i] ** 2 + (coef2[i] / natural_frequencies[i]) ** 2)

    return a


def get_modal_phases(normal_modal_vectors, natural_frequencies, m, desloc_init, vel_init):
    """
        Calculate the modal phase angles for free vibration analysis.

        Phase angles determine the time shift of each mode's oscillation relative
        to a cosine function. They are determined by the ratio of initial velocity
        to initial displacement contributions for each mode.

        Args:
            normal_modal_vectors (numpy.ndarray): Mass-normalized modal vectors - shape (n, n)
            natural_frequencies (numpy.ndarray): Natural frequencies [rad/s] - shape (n,)
            m (numpy.ndarray): Mass matrix [kg] - shape (n, n)
            desloc_init (numpy.ndarray): Initial displacement vector [m] - shape (n,)
            vel_init (numpy.ndarray): Initial velocity vector [m/s] - shape (n,)

        Returns:
            numpy.ndarray: Modal phase angles [rad] - shape (n,)

        Mathematical Background:
            For each mode: qᵢ(t) = Aᵢ cos(ωᵢt + φᵢ)
            Phase angle: φᵢ = arctan(-a₂ᵢ/(ωᵢ·a₁ᵢ))
            Where: a₁ᵢ = ψᵢᵀMx₀ (displacement coefficient)
                   a₂ᵢ = ψᵢᵀMẋ₀ (velocity coefficient)

        Physical Interpretation:
            - φᵢ = 0: Mode starts at maximum displacement
            - φᵢ = π/2: Mode starts at zero displacement, maximum velocity
            - φᵢ = π: Mode starts at minimum displacement
            - φᵢ = 3π/2: Mode starts at zero displacement, minimum velocity

        Note:
            Phase angles are relative to cosine function and depend on
            the relationship between initial displacement and velocity.
    """
    coef1 = np.zeros(normal_modal_vectors.shape[0])
    coef2 = np.zeros(normal_modal_vectors.shape[0])
    phase = np.zeros(normal_modal_vectors.shape[0])
    for i in range(normal_modal_vectors.shape[0]):
        aux1 = normal_modal_vectors[:, i].T
        coef1[i] = aux1 @ m @ desloc_init
        coef2[i] = aux1 @ m @ vel_init
        phase[i] = np.arctan(-(coef2[i] / (natural_frequencies[i] * coef1[i])))

    return phase


def get_natural_modes_of_vibration(normal_modal_vectors, natural_frequencies, coef, phase):
    """
        Generate a function to calculate individual modal responses in time.

        This function returns a callable that computes the contribution of each mode
        to the total response at any given time(s). Each mode oscillates at its
        natural frequency with its characteristic amplitude and phase.

        Args:
            normal_modal_vectors (numpy.ndarray): Mass-normalized modal vectors - shape (n, n)
            natural_frequencies (numpy.ndarray): Natural frequencies [rad/s] - shape (n,)
            coef (numpy.ndarray): Modal amplitude coefficients [m] - shape (n,)
            phase (numpy.ndarray): Modal phase angles [rad] - shape (n,)

        Returns:
            callable: Function x_of_t(time) that calculates modal responses

            The returned function accepts:
                time (float or numpy.ndarray): Time value(s) [s]

            And returns:
                For time as float: numpy.ndarray - shape (n, n_modes)
                For time as array: numpy.ndarray - shape (n, n_modes, n_times)

        Mathematical Background:
            Each modal response: xᵢ(t) = Aᵢψᵢ cos(ωᵢt + φᵢ)
            Where: Aᵢ = amplitude coefficient
                   ψᵢ = normal mode shape
                   ωᵢ = natural frequency
                   φᵢ = phase angle

        Applications:
            - Analyzing individual mode contributions
            - Understanding modal participation over time
            - Visualizing mode shapes in motion
            - Educational purposes to show modal superposition

        Usage Example:
            modal_response_func = get_natural_modes_of_vibration(...)
            t = np.linspace(0, 10, 1000)
            individual_modes = modal_response_func(t)
        """

    def x_of_t(time):
        n_dof = normal_modal_vectors.shape[0]
        n_modes = normal_modal_vectors.shape[1]
        if isinstance(time, np.ndarray):
            n_times = len(time)
            result = np.zeros((n_dof, n_modes, n_times))
            for i in range(n_modes):
                result[:, i, :] = (
                        coef[i] * normal_modal_vectors[:, i][:, np.newaxis]
                        * np.cos(natural_frequencies[i] * time + phase[i])
                )
            return result


        elif isinstance(time, float):
            result = np.zeros((n_dof, n_modes))
            for i in range(n_modes):
                result[:, i] = coef[i] * normal_modal_vectors[:, i] * np.cos(natural_frequencies[i] * time +
                                                                             phase[i])
            return result

    return x_of_t


def get_total_natural_response(natural_modes_in_time):
    """
        Calculate the total system response by summing all modal contributions.

        This function implements modal superposition to obtain the complete
        system response. The total response is the sum of all individual
        modal responses at each time instant and degree of freedom.

        Args:
            natural_modes_in_time (numpy.ndarray): Individual modal responses
                                                  Shape options:
                                                  - (n_dof, n_modes, n_times) for time series
                                                  - (n_dof, n_modes) for single time point

        Returns:
            numpy.ndarray: Total system response
                          Shape options:
                          - (n_dof, n_times) for time series input
                          - (n_dof,) for single time point input

        Mathematical Background:
            Modal superposition principle: x(t) = Σᵢ xᵢ(t)
            Where: x(t) = total response vector
                   xᵢ(t) = i-th modal response

            This is valid for linear systems where the principle of
            superposition applies.

        Physical Interpretation:
            - Each DOF's total displacement is the sum of contributions from all modes
            - Some modes may contribute more than others depending on excitation
            - The total response preserves all dynamic characteristics of the system

        Applications:
            - Free vibration analysis
            - Modal analysis validation
            - Response reconstruction from modal data
            - Dynamic system simulation

        Note:
            This function automatically handles both single time point and
            time series inputs based on the input array dimensions.
        """

    if natural_modes_in_time.ndim == 3:
        n_dof, n_modes, n_times = natural_modes_in_time.shape
        total_response = np.zeros((n_dof, n_times))

        for i in range(n_modes):
            total_response += natural_modes_in_time[:, i, :]

        return total_response

    elif natural_modes_in_time.ndim == 2:
        n_dof, n_modes = natural_modes_in_time.shape
        total_response = np.zeros(n_dof)

        for i in range(n_modes):
            total_response += natural_modes_in_time[:, i]

        return total_response
