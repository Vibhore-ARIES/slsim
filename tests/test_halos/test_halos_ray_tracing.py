import pytest
import numpy as np
from astropy.cosmology import FlatLambdaCDM
from astropy.table import Table
from slsim.Halos.halos_lens_base import HalosLensBase
from slsim.Halos.halos_ray_tracing import HalosRayTracing
import matplotlib


@pytest.fixture
def setup_halos_hrt():
    z = [0.5, 0.6, 0.7]

    mass = [2058751081954.2866, 1320146153348.6448, 850000000000.0]

    halos = Table([z, mass], names=("z", "mass"))

    z_correction = [0.5]
    kappa_ext_correction = [-0.1]
    mass_sheet_correction = Table(
        [z_correction, kappa_ext_correction], names=("z", "kappa")
    )
    cosmo = FlatLambdaCDM(H0=70, Om0=0.3, Ob0=0.05)
    HL = HalosLensBase(
        halos_list=halos,
        mass_correction_list=mass_sheet_correction,
        sky_area=0.0001,
        cosmo=cosmo,
        mass_sheet=True,
    )
    zd = 0.5
    zs = 1.0
    kwargs_lens = HL.get_halos_lens_kwargs()
    lens_model = HL.param_lens_model
    return HalosRayTracing(kwargs_lens, lens_model), HL.get_lens_data_by_redshift(
        zd, zs
    )


def test_get_convergence_shear(setup_halos_hrt):
    hrt, _ = setup_halos_hrt

    # Testing without gamma12
    kappa, gamma = hrt.get_convergence_shear()
    assert isinstance(kappa, float)
    assert isinstance(gamma, float)

    # Testing with gamma12
    kappa, gamma1, gamma2 = hrt.get_convergence_shear(gamma12=True)
    assert isinstance(kappa, float)
    assert isinstance(gamma1, float)
    assert isinstance(gamma2, float)


def test_nonlinear_correction_kappa_gamma_values(setup_halos_hrt):
    hrt, lens_data = setup_halos_hrt
    (
        kappa_od,
        kappa_os,
        gamma_od1,
        gamma_od2,
        gamma_os1,
        gamma_os2,
        kappa_ds,
        gamma_ds1,
        gamma_ds2,
    ) = hrt.nonlinear_correction_kappa_gamma_values(lens_data, 0.5, 1.0)
    assert isinstance(kappa_od, float)
    assert isinstance(kappa_os, float)
    assert isinstance(gamma_od1, float)
    assert isinstance(gamma_od2, float)
    assert isinstance(gamma_os1, float)
    assert isinstance(gamma_os2, float)
    assert isinstance(kappa_ds, float)
    assert isinstance(gamma_ds1, float)
    assert isinstance(gamma_ds2, float)


def test_get_kext_gext_values(setup_halos_hrt):
    hrt, lens_data = setup_halos_hrt
    zd = 0.5
    zs = 1.0
    kext, gext = hrt.get_kext_gext_values(lens_data, zd, zs)

    assert isinstance(kext, float)
    assert isinstance(gext, float)
    assert -1 <= kext <= 2
    assert 0 <= gext


def test_various_halos_data(setup_halos_hrt):
    hrt, lens_data = setup_halos_hrt
    zd = 0.5
    zs = 1.0
    (
        kappa_od,
        kappa_os,
        gamma_od1,
        gamma_od2,
        gamma_os1,
        gamma_os2,
        kappa_ds,
        gamma_ds1,
        gamma_ds2,
        kappa_os2,
        gamma_os12,
        gamma_os22,
        kext,
        gext,
    ), (kwargs_lens_os, lens_model_os) = hrt.various_halos_data(lens_data, zd, zs)
    assert isinstance(kappa_od, float)
    assert isinstance(kappa_os, float)
    assert isinstance(gamma_od1, float)
    assert isinstance(gamma_od2, float)
    assert isinstance(gamma_os1, float)
    assert isinstance(gamma_os2, float)
    assert isinstance(kappa_ds, float)
    assert isinstance(gamma_ds1, float)
    assert isinstance(gamma_ds2, float)
    assert isinstance(kwargs_lens_os, list)


def test_compute_kappa(setup_halos_hrt):
    hrt, lens_data = setup_halos_hrt

    kappa_image, kappa_values = hrt.compute_kappa(sky_area=0.0001 * np.pi**2)

    assert isinstance(kappa_image, np.ndarray)
    assert isinstance(kappa_values, np.ndarray)


@pytest.fixture(autouse=True)
def set_matplotlib_backend():
    original_backend = matplotlib.get_backend()
    matplotlib.use("Agg")
    yield
    matplotlib.use(original_backend)


def test_plot_convergence(setup_halos_hrt):
    hrt, _ = setup_halos_hrt
    try:
        hrt.plot_convergence(sky_area=0.0001 * np.pi**2)
    except Exception as e:
        pytest.fail(f"plot_convergence failed with an exception: {e}")
