"""This module contains the abstract base class for all upgrade
modules. Provides a basic workflow for the definition of new
upgrades.

"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, cast

import pandas as pd
from mosaik.async_scenario import CmdModel, PythonModel
from typing_extensions import TypeAlias

from midas.util.dict_util import (
    set_default_bool,
    set_default_float,
    set_default_int,
)

if TYPE_CHECKING:
    from midas.scenario.scenario import Scenario


LOG = logging.getLogger(__name__)
ConstraintsConfig: TypeAlias = list[tuple[str, int | float]]
Names: TypeAlias = list[str]
TimeSeriesMapping: TypeAlias = dict[
    int, list[tuple[str | tuple[str, str], float]]
]
SimParams: TypeAlias = dict[
    str,
    str | bool | int | float | TimeSeriesMapping | ConstraintsConfig | Names,
]
ModuleParams: TypeAlias = dict[
    str, str | bool | int | float | SimParams | ConstraintsConfig | Names
]


class UpgradeModule(ABC):
    """Base class for upgrade modules.

    Parameters
    ----------
    name: str
        The name of this module. This is the name that is referenced
        in the yaml file and must be present in the module load order.
    default_sim_config_name: str
        This is the name that is placed in the mosaik sim config. The
        simulator will be known under this name within mosaik.
        This is a default value; individual simulators may overwrite
        this.
    default_import_str: str
        This is default import path for this module if `python` is used
        to start this simulator.
    default_cmd_str: str
        This is the default command to start this module if `cmd` is
        used to start this simulator.
    default_scope_name: str
        If no scope is provided for this module, a new scope will be
        created with this name.

    """

    def __init__(
        self,
        module_name: str,
        default_scope_name: str,
        default_sim_config_name: str,
        default_import_str: str,
        default_cmd_str: str = "",
        log: Optional[logging.Logger] = None,
    ):
        self.module_name: str = module_name
        self.default_scope_name: str = default_scope_name
        self.default_sim_config_name: str = default_sim_config_name
        self.default_import_str: str = default_import_str
        self.default_cmd_str = default_cmd_str
        self.scenario: "Scenario"
        self.params: dict
        self.module_params: ModuleParams
        self.sim_params: SimParams
        self.sim_key: str = ""
        self.sid: str = ""
        self.scope_name: str = ""
        self.scopes: dict = {}
        self.logger: logging.Logger
        self._sim_ctr: int = 0
        self._model_ctr: Dict[str, int] = {}

        if log is None:
            self.logger = LOG
        else:
            self.logger = log

    def upgrade(self, scenario: "Scenario", params: dict):
        """Upgrade the scenario with this module.

        Adds the functionality provided by this upgrade to the
        scenario, i.e., define and start a simulator in the mosaik
        world, instantiate models, and add connections to other
        existing models.

        Parameters
        ----------
        scenario : :class:`midas.scenario.scenario.Scenario`
            The scenario containing reference to everything created in
            former upgrades.
        params : dict
            A *dict* containing the content of the config files and
            additional information generated during other upgrades.

        """
        self.scenario = scenario
        self.params = params
        self.module_params = self._check_module_params()

        for scope_name, sim_params in self.module_params.items():
            if not isinstance(sim_params, dict):
                continue

            self.scope_name = scope_name
            self.sim_params = sim_params

            self._check_sim_params(self.module_params)
            self.scopes[scope_name] = sim_params

            self._start_simulator()

            self.start_models()

            self.connect()
            if self.sim_params["with_arl"]:
                self.get_sensors()
                self.get_actuators()

            if not self.sim_params["no_db"]:
                try:
                    self.connect_to_db()
                except Exception as err:
                    LOG.error(
                        "Could not connect to the database module: %s "
                        "Did you add it to the modules key of your scenario? "
                        "e.g.: modules: [store, ...]",
                        err,
                    )

            if self.sim_params["with_timesim"]:
                try:
                    self.connect_to_timesim()
                except Exception as err:
                    LOG.error(
                        "Could not connect to the timesim module: %s "
                        "Did you add it to the modules key of your scenario? "
                        "e.g.: modules: [timesim, ...]",
                        err,
                    )

    def _check_module_params(self) -> ModuleParams:
        module_params = self.params.setdefault(
            f"{self.module_name}_params", {}
        )

        if not module_params:
            module_params[self.default_scope_name] = {}

        module_params.setdefault("sim_name", self.default_sim_config_name)
        module_params.setdefault("cmd", self.scenario.base.cmd)
        if module_params["cmd"] == "python":
            module_params.setdefault("import_str", self.default_import_str)
        elif module_params["cmd"] == "cmd":
            module_params.setdefault("import_str", self.default_cmd_str)
        else:
            LOG.error(
                "Invalid or unsupported cmd string: %s", module_params["cmd"]
            )
        module_params.setdefault("step_size", self.scenario.base.step_size)
        module_params.setdefault("no_db", self.scenario.base.no_db)
        module_params.setdefault(
            "with_timesim", self.scenario.base.with_timesim
        )
        module_params.setdefault("no_rng", self.scenario.base.no_rng)
        module_params.setdefault("with_arl", self.scenario.base.with_arl)
        self.check_module_params(module_params)
        return module_params

    @abstractmethod
    def check_module_params(self, mp: ModuleParams):
        """Check and provide default values for module params.
        
        Is called from within the upgrade method. For each parameter
        this function should check if the value is present already, i.e.,
        it was provided by the scenario file. If it is not present, a
        default value should be set.
        """
        raise NotImplementedError

    def _check_sim_params(self, mp: ModuleParams) -> None:
        self._simp_from_modulep(mp, "sim_name")
        self._simp_from_modulep(mp, "cmd")
        if self.sim_params["cmd"] == mp["cmd"]:
            self._simp_from_modulep(mp, "import_str")
        elif self.sim_params["cmd"] == "python":
            self.sim_params.setdefault("import_str", self.default_import_str)
        else:
            self.sim_params.setdefault("import_str", self.default_cmd_str)
        self._simp_from_modulep(mp, "step_size")
        self._simp_from_modulep(mp, "with_timesim", dtype="bool")
        self._simp_from_modulep(mp, "no_db", dtype="bool")
        self._simp_from_modulep(mp, "no_rng", dtype="bool")
        self._simp_from_modulep(mp, "with_arl", dtype="bool")

        self.check_sim_params(mp)

    def _simp_from_modulep(
        self, mp: ModuleParams, key: str, *, dtype: str = "str"
    ) -> None:
        default_val = mp[key]
        if type(default_val) is SimParams:
            msg = (
                "Attempted to set sim_params as part of other sim_params, "
                f"which is not allowed. Scope: {self.scope_name} Key: {key}"
            )
            raise ValueError(msg)

        if isinstance(default_val, dict):
            self.sim_params.setdefault(
                key,
                cast(
                    str | bool | int | float | TimeSeriesMapping, default_val
                ),
            )
        else:
            if dtype == "bool":
                set_default_bool(self.sim_params, key, cast(bool, default_val))
            elif dtype == "int":
                set_default_int(self.sim_params, key, cast(int, default_val))
            elif dtype == "float":
                set_default_float(
                    self.sim_params, key, cast(float, default_val)
                )
            else:
                self.sim_params.setdefault(key, default_val)

    @abstractmethod
    def check_sim_params(self, mp: ModuleParams):
        """Check and provide default values for sim params.
        
        Is called from within the upgrade method. For each parameter
        that a simulator expects, the it should be checked if the
        values are already set by the scenario file and, if not,
        provide default values. Generally, default values should be
        derived from the module params *mp*. There is a convenience
        function that can be used for this::

            def _simp_from_moduleP(
                mp: ModuleParams, 
                name: str, 
                *, 
                dtype: str|None = "str",
            ):

        It will check if an attribute *name* is already present in
        *sim_params*  and, if not, will take the value from *mp* to
        provide the value. If *dtype* is specified, a conversion is
        done as well (useful especially for bool values).
        
        """
        raise NotImplementedError

    def _start_simulator(self):
        """Start a certain simulator instance."""

        cmd = cast(str, self.sim_params.pop("cmd"))
        import_str = self.sim_params.pop("import_str")
        with_timesim = self.sim_params.pop("with_timesim")
        no_db = self.sim_params.pop("no_db")
        no_rng = self.sim_params.pop("no_rng")
        with_arl = self.sim_params.pop("with_arl")
        sim_name = cast(str, self.sim_params["sim_name"])

        # Place model in the world's *sim_config*
        self.scenario.makelists.sim_config[sim_name] = cast(
            PythonModel | CmdModel, {cmd: import_str}
        )
        self.scenario.script.simconfig = [
            f"sim_config = {self.scenario.makelists.sim_config}\n"
        ]

        # Create a unique simulator key
        self.sim_key = self.scenario.generate_sim_key(self)

        # Start the simulator if it was not started before
        if not self.scenario.sim_started(self.sim_key):
            self.scenario.add_sim(self.sim_key, self.sim_params)
            self.sid = self.guess_sid()
            self._model_ctr = {}
            self.scenario.entities[self.sid] = None  # Just reserve the space
            self.scenario.script.definitions.append(
                f"{self.sim_key}_params = {self.sim_params}\n"
            )
            self.scenario.script.sim_start.append(
                f"{self.sim_key} = world.start(**{self.sim_key}_params)\n"
            )
        self.sim_params["cmd"] = cmd
        self.sim_params["import_str"] = import_str
        self.sim_params["with_timesim"] = with_timesim
        self.sim_params["with_arl"] = with_arl
        self.sim_params["no_db"] = no_db
        self.sim_params["no_rng"] = no_rng

    @abstractmethod
    def start_models(self):
        raise NotImplementedError

    @abstractmethod
    def connect(self):
        raise NotImplementedError

    @abstractmethod
    def connect_to_db(self):
        raise NotImplementedError

    def connect_to_timesim(self):
        pass

    def start_model(
        self, model_key: str, model_name: str, params: Dict[str, Any]
    ) -> None:
        if not self.scenario.model_started(model_key, self.sim_key):
            full_id = self.guess_full_id(model_name)

            self.scenario.add_model(
                model_key, self.sim_key, model_name, params, full_id
            )
            self.scenario.entities[full_id] = None

            self.scenario.script.definitions.append(
                f"{model_key}_params = {params}\n"
            )
            self.scenario.script.model_start.append(
                f"{model_key} = {self.sim_key}.{model_name}(**{model_key}"
                "_params)\n"
            )

    def connect_entities(
        self,
        from_ent_key: str,
        to_ent_key: str,
        attrs: List[Union[str, Tuple[str, str]]],
        **kwargs,
    ):
        self.scenario.makelists.connects.append(
            {
                "from": from_ent_key,
                "to": to_ent_key,
                "attrs": attrs,
                "kwargs": kwargs,
            }
        )
        self.scenario.script.connects.append(
            f"world.connect({from_ent_key}, {to_ent_key}, *{attrs}, "
            f"**{kwargs})\n"
        )

    def get_sensors(self):
        pass

    def get_actuators(self):
        pass

    def get_info(self):
        self.logger.debug("I don't provide info!")

    def download(self, data_path: str, tmp_path: str, force: bool):
        """Download the data set of this module.
        This method should if be overwritten if the module has any data
        sets that need to be downloaded.

        Parameters
        ==========
        data_path: str
            Path to the data folder of MIDAS.
        tmp_path: str
            Path to the temporary folder, where temporary download
            artifacts can be stored. Will be deleted afterwards.
        force: bool
            This flag allows to force a download and overwrite any
            existing data sets of this module.
        """
        self.logger.debug("I don't provide downloads!")

    def analyze(
        self,
        name: str,
        data: pd.DataFrame,
        output_folder: str,
        start: int,
        end: int,
        step_size: int,
        full: bool,
    ):
        self.logger.debug("I don't provide analyis!")

    def guess_sid(self):
        while True:
            sid = f"{self.default_sim_config_name}-{self._sim_ctr}"
            self._sim_ctr += 1
            if sid not in self.scenario.entities:
                break

        return sid

    def guess_full_id(self, model_name):
        self._model_ctr.setdefault(model_name, 0)
        while True:
            full_id = f"{self.sid}.{model_name}-{self._model_ctr[model_name]}"
            self._model_ctr[model_name] += 1

            if full_id not in self.scenario.entities:
                break
        return full_id
