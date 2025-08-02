from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from dataclasses_json import config, dataclass_json
import pandas as pd
import typing as t
from .io import read_pvsyst_file
from .solar_resource import psm_column_map
from warnings import warn

from tyba_client.utils import string_enum


class ValidationError(ValueError):
    pass


def opt_field():
    return field(default=None, metadata=config(exclude=lambda x: x is None))


@dataclass_json
@dataclass
class FixedTilt(object):
    tilt: float


@dataclass_json
@dataclass
class SingleAxisTracking(object):
    rotation_limit: float = 45.0
    backtrack: bool = True


@dataclass_json
@dataclass
class BaseSystemDesign(object):
    dc_capacity: float
    ac_capacity: float
    poi_limit: float


@dataclass_json
@dataclass
class SystemDesign(BaseSystemDesign):
    gcr: float
    tracking: t.Union[FixedTilt, SingleAxisTracking]
    modules_per_string: t.Optional[int] = opt_field()
    strings_in_parallel: t.Optional[int] = opt_field()
    azimuth: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class BaseInverter(object):
    mppt_low: float
    mppt_high: float
    paco: float
    vdco: float
    pnt: float


@dataclass_json
@dataclass
class ONDTemperatureDerateCurve(object):
    ambient_temp: t.List[float]
    max_ac_power: t.List[float]


@dataclass_json
@dataclass
class ONDEfficiencyCurve(object):
    dc_power: t.List[float]
    ac_power: t.List[float]


@dataclass_json
@dataclass
class ONDInverter(BaseInverter):
    temp_derate_curve: ONDTemperatureDerateCurve
    nominal_voltages: t.List[float]
    power_curves: t.List[ONDEfficiencyCurve]
    dc_turn_on: float
    aux_loss: t.Optional[float] = opt_field()
    aux_loss_threshold: t.Optional[float] = opt_field()
    includes_xfmr: t.Optional[bool] = True

    @classmethod
    def from_ond(cls, ond_file: str):
        ond = read_pvsyst_file(ond_file)
        data = ond["PVObject_"]["items"]
        converter = data["Converter"]["items"]
        voltage_curve_points = [float(v) for v in converter["VNomEff"].split(",") if v]
        if len(voltage_curve_points) != 3:
            raise NotImplementedError(
                "OND Inverter only accepts voltage curves of length 3"
            )
        temp_derate_curve = ONDTemperatureDerateCurve(
            ambient_temp=[
                -300,
                float(converter["TPMax"]),
                float(converter["TPNom"]),
                float(converter["TPLim1"]),
                float(converter["TPLimAbs"]),
            ],
            max_ac_power=[
                float(converter["PMaxOUT"]) * 1e3,
                float(converter["PMaxOUT"]) * 1e3,
                float(converter["PNomConv"]) * 1e3,
                float(converter["PLim1"]) * 1e3,
                float(converter.get("PlimAbs", 0.0)) * 1e3,
            ],
        )
        raw_power_curves = [converter[f"ProfilPIOV{i}"]["items"] for i in [1, 2, 3]]
        power_curves = []
        for curve in raw_power_curves:
            points = [
                [float(v) for v in curve[f"Point_{i}"].split(",")]
                for i in range(1, int(curve["NPtsEff"]) + 1)
            ]
            dc, ac = zip(*points)
            power_curves.append(ONDEfficiencyCurve(dc_power=dc, ac_power=ac))
        aux_loss = data.get("Aux_Loss")
        aux_loss_threshold = data.get("Aux_Thresh")
        if aux_loss is not None:
            aux_loss = float(aux_loss)
            aux_loss_threshold = float(aux_loss_threshold)
        return cls(
            mppt_low=float(converter["VMppMin"]),
            mppt_high=float(converter["VMPPMax"]),
            paco=float(converter["PMaxOUT"]) * 1e3,
            vdco=voltage_curve_points[1],
            temp_derate_curve=temp_derate_curve,
            nominal_voltages=voltage_curve_points,
            power_curves=power_curves,
            dc_turn_on=float(converter["PSeuil"]),
            pnt=float(data["Night_Loss"]),
            aux_loss=aux_loss,
            aux_loss_threshold=aux_loss_threshold,
        )


@dataclass_json
@dataclass
class Inverter(BaseInverter):
    pso: float
    pdco: float
    c0: float
    c1: float
    c2: float
    c3: float
    vdcmax: float
    tdc: t.List[t.List[float]] = field(default_factory=lambda: [[1.0, 52.8, -0.021]])
    includes_xfmr: t.Optional[bool] = True


@dataclass_json
@dataclass
class PVModule(object):
    bifacial: bool
    a_c: float
    n_s: float
    i_sc_ref: float
    v_oc_ref: float
    i_mp_ref: float
    v_mp_ref: float
    alpha_sc: float
    beta_oc: float
    t_noct: float
    a_ref: float
    i_l_ref: float
    i_o_ref: float
    r_s: float
    r_sh_ref: float
    adjust: float
    gamma_r: float
    bifacial_transmission_factor: float
    bifaciality: float
    bifacial_ground_clearance_height: float


@string_enum
class MermoudModuleTech(Enum):
    SiMono = "mtSiMono"
    SiPoly = "mtSiPoly"
    CdTe = "mtCdTe"
    CIS = "mtCIS"
    uCSi_aSiH = "mtuCSi_aSiH"


@dataclass_json
@dataclass
class PVModuleMermoudLejeune(object):
    bifacial: bool
    bifacial_transmission_factor: float
    bifaciality: float
    bifacial_ground_clearance_height: float
    tech: MermoudModuleTech
    i_mp_ref: float
    i_sc_ref: float
    length: float
    n_diodes: int
    n_parallel: int
    n_series: int
    r_s: float
    r_sh_0: float
    r_sh_exp: float
    r_sh_ref: float
    s_ref: float
    t_c_fa_alpha: float
    t_ref: float
    v_mp_ref: float
    v_oc_ref: float
    width: float
    alpha_sc: float
    beta_oc: float
    mu_n: float
    n_0: float
    iam_c_cs_iam_value: t.Optional[t.List[float]] = opt_field()
    iam_c_cs_inc_angle: t.Optional[t.List[float]] = opt_field()
    custom_d2_mu_tau: t.Optional[float] = opt_field()

    @classmethod
    def from_pan(cls, pan_file: str):
        pan_blob = read_pvsyst_file(pan_file)
        data = pan_blob["PVObject_"]["items"]
        commercial = data["PVObject_Commercial"]["items"]
        if "PVObject_IAM" in data:
            iam_points = [
                v.split(",")
                for k, v in data["PVObject_IAM"]["items"]["IAMProfile"]["items"].items()
                if k.startswith("Point_")
            ]
            iam_angles = [float(v[0]) for v in iam_points]
            iam_values = [float(v[1]) for v in iam_points]
        else:
            iam_angles = None
            iam_values = None

        return cls(
            bifacial="BifacialityFactor" in data,
            bifacial_transmission_factor=0.013,
            bifaciality=float(data.get("BifacialityFactor", 0.65)),
            bifacial_ground_clearance_height=1.0,
            n_parallel=int(data["NCelP"]),
            n_diodes=int(data["NDiode"]),
            n_series=int(data["NCelS"]),
            t_ref=float(data["TRef"]),
            s_ref=float(data["GRef"]),
            i_sc_ref=float(data["Isc"]),
            v_oc_ref=float(data["Voc"]),
            i_mp_ref=float(data["Imp"]),
            v_mp_ref=float(data["Vmp"]),
            alpha_sc=float(data["muISC"]) * 1e-3,  # TODO: check units
            beta_oc=float(data["muVocSpec"]) * 1e-3,
            n_0=float(data["Gamma"]),
            mu_n=float(data["muGamma"]),
            r_sh_ref=float(data["RShunt"]),
            r_s=float(data["RSerie"]),
            r_sh_0=float(data["Rp_0"]),
            r_sh_exp=float(data["Rp_Exp"]),
            tech=data["Technol"],
            length=float(commercial["Height"]),
            width=float(commercial["Width"]),
            # faiman cell temp model used by PVSyst
            t_c_fa_alpha=float(data["Absorb"]),
            # IAM
            iam_c_cs_iam_value=iam_values,
            iam_c_cs_inc_angle=iam_angles,
            custom_d2_mu_tau=data.get("D2MuTau"),
        )


@dataclass_json
@dataclass
class Transformer(object):
    load_loss: float
    no_load_loss: float
    rating: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class _DCLosses(object):
    dc_optimizer: t.Optional[float] = opt_field()
    enable_snow_model: t.Optional[bool] = opt_field()
    dc_wiring: t.Optional[float] = opt_field()
    soiling: t.Optional[t.List[float]] = opt_field()
    diodes_connections: t.Optional[float] = opt_field()
    mismatch: t.Optional[float] = opt_field()
    nameplate: t.Optional[float] = opt_field()
    rear_irradiance: t.Optional[float] = opt_field()
    lid: t.Optional[float] = opt_field()
    dc_array_adjustment: t.Optional[float] = opt_field()
    mppt_error: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class ACLosses(object):
    ac_wiring: t.Optional[float] = opt_field()
    transformer_load: t.Optional[float] = opt_field()
    transformer_no_load: t.Optional[float] = opt_field()
    transmission: t.Optional[float] = opt_field()
    poi_adjustment: t.Optional[float] = opt_field()
    mv_transformer: t.Optional[Transformer] = opt_field()
    hv_transformer: t.Optional[Transformer] = opt_field()

    def __post_init__(self):
        if not (
            (self.transformer_load is None and self.transformer_no_load is None)
            or self.hv_transformer is None
        ):
            raise ValidationError(
                "Cannot provide hv_transformer if transformer_load or transformer_no_load are provided"
            )


@dataclass_json
@dataclass
class Losses(_DCLosses, ACLosses):
    pass


@dataclass_json
@dataclass
class Layout(object):
    orientation: t.Optional[str] = opt_field()
    vertical: t.Optional[int] = opt_field()
    horizontal: t.Optional[int] = opt_field()
    aspect_ratio: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class SolarResourceTimeSeries(object):
    year: t.List[int]
    month: t.List[int]
    day: t.List[int]
    hour: t.List[int]
    minute: t.List[int]
    tdew: t.List[float]
    df: t.List[float]
    dn: t.List[float]
    gh: t.List[float]
    pres: t.List[float]
    tdry: t.List[float]
    wdir: t.List[float]
    wspd: t.List[float]
    alb: t.Optional[t.List[float]] = opt_field()
    snow: t.Optional[t.List[float]] = opt_field()


@dataclass_json
@dataclass
class SolarResource(object):
    latitude: float
    longitude: float
    time_zone_offset: float
    elevation: float
    data: SolarResourceTimeSeries
    monthly_albedo: t.Optional[t.List[float]] = opt_field()

    @classmethod
    def from_csv(cls, filename: str) -> SolarResource:
        with open(filename) as f:
            _meta = [f.readline().split(",") for _ in range(2)]
            _data = pd.read_csv(f)
        meta = {k: v for k, v in zip(*_meta)}
        data = _data.rename(columns=psm_column_map)
        return cls(
            latitude=float(meta["Latitude"]),
            longitude=float(meta["Longitude"]),
            elevation=float(meta["Elevation"]),
            time_zone_offset=float(meta["Time Zone"]),
            data=data.to_dict(orient="list"),
        )


@string_enum
class ArrayDegradationMode(str, Enum):
    linear = "linear"
    compounding = "compounding"


@dataclass_json
@dataclass
class PVModel(object):
    solar_resource: t.Union[t.Tuple[float, float], SolarResource]
    inverter: t.Union[str, BaseInverter]
    pv_module: t.Union[str, PVModule, PVModuleMermoudLejeune]
    system_design: SystemDesign
    losses: t.Optional[Losses] = opt_field()
    layout: t.Optional[Layout] = opt_field()
    project_term: t.Optional[int] = opt_field()
    array_degradation_rate: t.Optional[float] = opt_field()
    array_degradation_mode: t.Optional[ArrayDegradationMode] = "linear"


PVGenerationModel = DetailedPVModel = PVModel


@dataclass_json
@dataclass
class DCProductionProfile(object):
    power: t.List[float]
    voltage: t.List[float]
    ambient_temp: t.Optional[t.List[float]]


@dataclass_json
@dataclass
class ACProductionProfile(object):
    power: t.List[float]
    ambient_temp: t.Optional[t.List[float]]


@dataclass_json
@dataclass
class ACExternalGenerationModel(object):
    production_override: ACProductionProfile
    system_design: BaseSystemDesign
    losses: ACLosses = opt_field()
    time_interval_mins: t.Optional[int] = opt_field()
    project_term: t.Optional[int] = opt_field()
    project_term_units: t.Optional[str] = opt_field()


@dataclass_json
@dataclass
class DCExternalGenerationModel(object):
    production_override: DCProductionProfile
    system_design: BaseSystemDesign
    inverter: t.Union[Inverter, ONDInverter, str]
    losses: ACLosses = opt_field()
    time_interval_mins: t.Optional[int] = opt_field()
    project_term: t.Optional[int] = opt_field()
    project_term_units: t.Optional[str] = opt_field()


GenerationModel = t.Union[
    PVGenerationModel, DCExternalGenerationModel, ACExternalGenerationModel
]


@dataclass_json
@dataclass
class BatteryHVAC(object):
    container_temperature: float
    cop: float
    u_ambient: float
    discharge_efficiency_container: float
    charge_efficiency_container: float
    aux_xfmr_efficiency: float


@dataclass_json
@dataclass
class TableCapDegradationModel(object):
    annual_capacity_derates: t.List[float]


@dataclass_json
@dataclass
class TableEffDegradationModel(object):
    annual_efficiency_derates: t.List[float]


@dataclass_json
@dataclass
class Battery(object):
    power_capacity: float
    energy_capacity: float
    charge_efficiency: float
    discharge_efficiency: float
    term: float
    degradation_rate: t.Optional[float] = opt_field()
    degradation_annual_cycles: t.Optional[float] = 365
    hvac: t.Optional[BatteryHVAC] = opt_field()
    capacity_degradation_model: t.Optional[TableCapDegradationModel] = opt_field()
    efficiency_degradation_model: t.Optional[TableEffDegradationModel] = opt_field()


@dataclass_json
@dataclass
class StorageInputs(object):
    batteries: t.List[Battery]
    cycling_cost_adder: t.Optional[float] = 0
    annual_cycle_limit: t.Optional[float] = opt_field()
    window: t.Optional[int] = opt_field()
    step: t.Optional[int] = opt_field()
    flexible_solar: t.Optional[bool] = opt_field()
    dart: t.Optional[bool] = opt_field()
    dam_annual_cycle_limit: t.Optional[float] = opt_field()
    no_virtual_trades: t.Optional[bool] = opt_field()
    initial_soe: t.Optional[float] = 0
    symmetric_reg: t.Optional[bool] = False
    duration_requirement_on_discharge: t.Optional[bool] = opt_field()
    solver: t.Optional[bool] = opt_field()


@dataclass_json
@dataclass
class AncillaryEnergyPrices(object):
    dam: t.List[float]
    rtm: t.List[float]


@dataclass_json
@dataclass
class StorageModel(object):
    storage_inputs: StorageInputs
    energy_prices: t.Union[AncillaryEnergyPrices, t.List[float]]


@dataclass_json
@dataclass
class Utilization(object):
    actual: float
    lower: float
    upper: float


@dataclass_json
@dataclass
class TimeSeriesUtilization(object):
    actual: t.List[float]
    lower: t.List[float]
    upper: t.List[float]


@dataclass_json
@dataclass
class ReserveMarket(object):
    price: t.List[float]
    offer_cap: float
    utilization: t.Union[Utilization, TimeSeriesUtilization]
    obligation: t.Optional[t.List[float]] = opt_field()
    duration_requirement: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class AncillaryUpMarkets(object):
    reserves: t.Optional[ReserveMarket] = opt_field()
    reg_up: t.Optional[ReserveMarket] = opt_field()
    generic_up: t.Optional[ReserveMarket] = opt_field()


@dataclass_json
@dataclass
class AncillaryDownMarket(object):
    reg_down: t.Optional[ReserveMarket] = opt_field()
    generic_down: t.Optional[ReserveMarket] = opt_field()


@dataclass_json
@dataclass
class AncillaryMarkets(object):
    up: t.Optional[AncillaryUpMarkets] = opt_field()
    down: t.Optional[AncillaryDownMarket] = opt_field()


@dataclass_json
@dataclass
class PeakWindow(object):
    mask: t.List[bool]
    price: float


@dataclass_json
@dataclass
class LoadPeakReduction(object):
    load: t.List[float]
    max_load: t.List[float]
    seasonal_peak_windows: t.Optional[t.List[PeakWindow]] = opt_field()
    daily_peak_windows: t.Optional[t.List[PeakWindow]] = opt_field()


@dataclass_json
@dataclass
class StandaloneStorageModel(StorageModel):
    time_interval_mins: t.Optional[int] = opt_field()
    ancillary_markets: t.Optional[AncillaryMarkets] = opt_field()
    ambient_temp: t.Optional[t.List[float]] = opt_field()
    import_limit: t.Optional[t.List[float]] = opt_field()
    export_limit: t.Optional[t.List[float]] = opt_field()
    load_peak_reduction: t.Optional[LoadPeakReduction] = opt_field()
    project_term: t.Optional[int] = opt_field()
    project_term_units: t.Optional[str] = opt_field()


@string_enum
class StorageCoupling(Enum):
    ac = "ac"
    dc = "dc"
    hv_ac = "hv_ac"


@dataclass_json
@dataclass
class PVStorageModel(object):
    storage_coupling: StorageCoupling = field(metadata=StorageCoupling.__metadata__)
    pv_inputs: GenerationModel
    storage_inputs: StorageInputs
    energy_prices: t.Union[AncillaryEnergyPrices, t.List[float]]
    enable_grid_charge_year: t.Optional[int] = opt_field()
    ancillary_markets: t.Optional[AncillaryMarkets] = opt_field()
    import_limit: t.Optional[t.List[float]] = opt_field()
    export_limit: t.Optional[t.List[float]] = opt_field()
    load_peak_reduction: t.Optional[LoadPeakReduction] = opt_field()
    time_interval_mins: t.Optional[int] = opt_field()


@string_enum
class Market:
    RT = "realtime"
    DA = "dayahead"


@string_enum
class AncillaryService:
    REGULATION_UP = "Regulation Up"
    REGULATION_DOWN = "Regulation Down"
    RESERVES = "Reserves"
    ECRS = "ECRS"
