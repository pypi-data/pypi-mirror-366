from extra_data.exceptions import PropertyNameError, SourceNameError

SASE_BY_INSTRUMENT = {
    'SPB': 'SA1', 'FXE': 'SA1',
    'MID': 'SA2', 'HED': 'SA2',
    'SQS': 'SA3', 'SCS': 'SA3',
}


def get_xgm_sources(sources, inst=None):
    if inst is None:
        def filter_xgm(src):
            return src.endswith('XGM') or src.endswith('XGMD')
    elif inst in ['SA1', 'SA2', 'SA3']:
        def filter_xgm(src):
            return ((src.endswith('XGM') or src.endswith('XGMD')) and
                    src.startswith(inst))
    else:
        sase = SASE_BY_INSTRUMENT[inst]

        def filter_xgm(src):
            return ((src.endswith('XGM') or src.endswith('XGMD')) and
                    (src.startswith(inst) or src.startswith(sase)))

    return [src for src in sources if filter_xgm(src.partition('/')[0])]


def get_wavelenght(dc, xgm_sources, keV=False):
    nbadsrc = 0
    lmd = None
    for xgm in xgm_sources:
        try:
            wavelength_data = dc[xgm, 'pulseEnergy.wavelengthUsed']
            lmd = wavelength_data.as_single_value(rtol=1e-2)
            break
        except (SourceNameError, PropertyNameError):
            nbadsrc += 1
        except ValueError:
            pass

    if nbadsrc == len(xgm_sources):
        raise SourceNameError('No one source is found.')
    elif lmd is None:
        raise ValueError("Photon energy varies greater than 1 percent")

    # Eph = hc / lmd / e
    return 1.2398419843320025 / lmd if keV else lmd
