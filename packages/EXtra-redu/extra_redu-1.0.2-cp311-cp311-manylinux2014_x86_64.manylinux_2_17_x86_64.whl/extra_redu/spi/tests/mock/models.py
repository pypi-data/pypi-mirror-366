import numpy as np


def gas_scattering(geom, ambient=0.02, shape=4e-5):
    # fenomenological, dirty
    # ambient - uniform term
    # decay - gaussian sigma
    return np.exp(-0.5 * geom.r * geom.r / shape) + ambient


def pulse_intensities(num_pulses, mean_energy=1.8, rmsd=0.01):
    # mean_energy (mJ)
    # rmsd (mJ)
    return np.random.normal(loc=mean_energy, scale=rmsd, size=num_pulses)


def ball_scattering(geom, R=35, L=1.7, photon_en=6.0):
    # geom - detector geometry
    # R - ball diameter (nm)
    # L - distance to camera (m)
    # photon_en - photon energy (keV)
    hc_e = 1.2398419843320028  # 1e6 * h * c / e
    lmd = hc_e / photon_en  # nm
    cos2T = L / np.sqrt(L * L + geom.r * geom.r)
    q = np.sqrt(2 - 2 * cos2T) / lmd

    pi_q_R = np.pi * q * R
    j1 = 3 * (np.sin(pi_q_R) / pi_q_R - np.cos(pi_q_R)) / pi_q_R
    ball = j1 * j1  # (r_e pi R^3 n / 6)^2
    return ball


def interaction_point_intensity(num_pulses, beam_size=1.5, flow_size=25):
    # beam_size - FWHM of beam profile
    # flow_size - particle flow width
    sigma = beam_size / 2.355

    pos = np.random.uniform(
        -flow_size / 2, flow_size / 2, size=(num_pulses, 2))
    displacement = np.sqrt(np.sum(pos * pos, 1))

    a = displacement / sigma
    return np.exp(-0.5 * a * a) / (2 * np.pi * sigma * sigma)


def agipd_noise(image, termal=1.0 / 6.0):
    photons = np.random.poisson(image)
    return photons + termal * np.random.normal(scale=1.0 + photons,
                                               size=photons.shape)


def spi_ball_scattering(
    geom,
    num_pulses,
    photon_en,
    L,
    R,
    flow_size,
    beam_size,
    pulse_energy,
    pulse_energy_rmsd,
    gas_ambient,
    gas_shape,
):
    ndim = len(geom.shape)
    pulse_inten = pulse_intensities(
        num_pulses, pulse_energy, pulse_energy_rmsd
    ).reshape(-1, *[1] * ndim)
    ball_inten = interaction_point_intensity(
        num_pulses, beam_size, flow_size
    ).reshape(-1, *[1] * ndim)

    ball = 100 * ball_scattering(geom, R, L, photon_en=photon_en)[None, ...]
    gas = gas_scattering(geom, gas_ambient, gas_shape)[None, ...]

    return agipd_noise(pulse_inten * (gas + ball_inten * ball),
                       1.0 / photon_en)
