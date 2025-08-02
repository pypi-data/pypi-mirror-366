from pysimmods.base.types import ModelInitVals, ModelParams


def windsys_preset(
    pn_max_kw: float,
    wind_profile: str = "hellmann",
    temperature_profile: str = "linear_gradient",
    air_density_profile: str = "barometric",
    power_method: str = "power_curve",
    turbine_type: str | None = None,
    cos_phi: float = 0.9,
    q_control: str = "prioritize_p",
    inverter_mode: str = "inductive",
    randomize_params: bool = False,
    seed: int | None = None,
    **kwargs,
) -> tuple[ModelParams, ModelInitVals]:
    from pysimmods.generator.windsim.presets import wind_preset

    wparams, winit = wind_preset(
        pn_max_kw,
        wind_profile,
        temperature_profile,
        air_density_profile,
        power_method,
        turbine_type,
        randomize_params,
        seed,
        **kwargs,
    )

    params: ModelParams = {
        "wind": wparams,
        "inverter": {
            "sn_kva": pn_max_kw / cos_phi,
            "q_control": q_control,
            "cos_phi": cos_phi,
            "inverter_mode": inverter_mode,
        },
        "sign_convention": "active",
    }

    inits: ModelInitVals = {"wind": winit, "inverter": {}}

    return params, inits
