STUB_DATA_FILE_MAPPING: dict[str, list[str]] = {
    "feedline_discovery": [f"QM/Tuna-5/feedline_discovery/{n}.json" for n in range(1, 7)],
    "resonator_mapping": [f"QM/Tuna-5/resonator_mapping/{n}.json" for n in range(1, 17)],
    "resonator_spectroscopy": ["QM/Tuna-5/resonator_spectroscopy.json"],
    "resonator_spectroscopy_by_power": ["QM/Tuna-5/resonator_spectroscopy_by_power.json"],
    "resonator_spectroscopy_by_bias": ["QM/Tuna-5/resonator_spectroscopy_by_bias.json"],
    "ramsey": ["QM/Tuna-5/ramsey.json"],
    "power_rabi": ["QM/Tuna-5/power_rabi.json"],
}
