"""A class to read openmc depletion result files."""

import xml.etree.ElementTree as ET
from typing import Dict, Iterable, List, Optional, Union

import h5py
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from uncertainties import ufloat
from uncertainties import unumpy as unp
from .data import element, z_a_i, atomic_mass, AVOGADRO
import pint

ureg = pint.UnitRegistry(cache_folder=":auto:")
ureg.define("atom = 1 * count")
ureg.define("reaction = 1 * count")


class DepletionResults:
    """A class to read openmc depletion result files.

    Attributes:
        path (str): Path to the result file.
        dconst (dict): Decay constant dictionnary.
        decay_energy (dict): Decay energy dictionnary.
        _nuclides (List[str]): Internal list of nuclide names
        _rr_ids (List[str]): Internal nuclides ids in the reaction rates matrix.
        _reaction_ids (list[str]): Internal reaction ids.
        _reactions (NDArray[float64]): Internal reaction rates matrix.
        _materials (Dict): Internal material indices and volumes.
        _time (NDArray[float64]): Internal time vector.
        _number (NDArray[float64]): Internal concentration vector.
        _power (NDArray[float64]): Internal power level vector.
        _keffs (NDArray[ufloat]): Internal keffs vector.
        chain (str): Path to the chain file.

    """

    def __init__(self, path: str, chain_file: str = None) -> None:
        """Load a depletion result file.

        Args:
            path (str): Path to the result file.
            chain_file (str): Path to a result file.

        """
        self.path = path
        self.dconst: Optional[Dict[str, float]] = None
        self.decay_energy: Optional[Dict[str, float]] = None
        self._nuclides: Optional[List[str]] = None
        self._rr_ids: Optional[List[str]] = None
        self._reaction_ids: Optional[List[str]] = None
        self._reactions: Optional[NDArray[np.float64]] = None
        self._materials: Optional[dict] = None
        self._time: Optional[NDArray[np.float64]] = None
        self._number: Optional[NDArray[np.float64]] = None
        self._power: Optional[NDArray[np.float64]] = None
        self._keffs: Optional[NDArray[ufloat]] = None
        self.chain: str = chain_file

    @property
    def chain(self) -> str:
        """The path to the depletion chain in the openmc format. Chains are used is the user asks for an activity recap.

        Returns:
            str: the chain file path.

        """
        return self._chain

    @chain.setter
    def chain(self, chain_file: str) -> None:
        """Setting the depletion chain. This also sets the dconst attribute.

        Args:
            chain_file (str): Path to the chain file.

        """
        if chain_file is None:
            self._chain = None
            self.dconst = None
            self.decay_energy = None
            return
        self._chain = chain_file
        f = ET.parse(self._chain)
        self.dconst = {}
        self.decay_energy = {}
        for isotnode in f.findall("nuclide"):
            parent = isotnode.get("name")
            hl = isotnode.get("half_life")
            energy = isotnode.get("decay_energy", 0)
            self.dconst[parent] = np.log(2) / float(hl) if hl is not None else 0.0
            self.decay_energy[parent] = float(energy)

    @property
    def nuclides(self) -> List[str]:
        """The list of isotopes in the result file.

        Returns:
            list[str]: The isotopes sorted in the order of the concentration
                        indices.

        """
        if self._nuclides is None:
            with h5py.File(self.path) as f:
                nuclides = f["nuclides"]
                unsorted = [
                    (i, nuclides[i].attrs["atom number index"]) for i in nuclides
                ]
                isotopes = sorted(unsorted, key=lambda x: x[1])
            self._nuclides = [i[0] for i in isotopes]
        return self._nuclides

    @property
    def rr_ids(self) -> List[str]:
        """The indices of the reaction rates in the file. For internal use.

        Returns:
            dict: The nuclides' indices in the reaction rate array.

        """
        if self._rr_ids is None:
            with h5py.File(self.path) as f:
                nuclides = f["nuclides"]
                unsorted = []
                for i in nuclides:
                    try:
                        unsorted.append((i, nuclides[i].attrs["reaction rate index"]))
                    except KeyError:
                        pass
                rr_ids = sorted(unsorted, key=lambda x: x[1])
            self._rr_ids = [i[0] for i in rr_ids]
        return self._rr_ids

    @property
    def reaction_ids(self) -> List[str]:
        """The indices of the reactions in the file. For internal use.

        Returns:
            list: The reaction list.

        """
        if self._reaction_ids is None:
            with h5py.File(self.path) as f:
                reactions = f["reactions"]
                unsorted = [(i, reactions[i].attrs["index"]) for i in reactions]
                reaction_ids = sorted(unsorted, key=lambda x: x[1])
            self._reaction_ids = [i[0] for i in reaction_ids]
        return self._reaction_ids

    @property
    def reactions(self) -> NDArray[np.float64]:
        """The reaction rate array.

        Returns:
            dict: The reaction rate array for each material.

        """
        if self._reactions is None:
            rr = {}
            with h5py.File(self.path) as f:
                raw_rr = f["reaction rates"][...]
                for mat_id, material in self.materials.items():
                    rr[mat_id] = raw_rr[:, 0, material["index"], :, :]
            self._reactions = rr
        return self._reactions

    @property
    def materials(self) -> dict:
        """The materials in the file.

        Returns:
            dict: Each material indices with their index in the concentration
                    and reaction rates arrays, and their volume.

        """
        if self._materials is None:
            materials = {}
            with h5py.File(self.path) as f:
                for mat in f["materials"]:
                    materials[int(mat)] = {
                        "index": f[f"materials/{mat}"].attrs["index"],
                        "volume": f[f"materials/{mat}"].attrs["volume"],
                    }
            self._materials = materials
        return self._materials

    @property
    def time(self) -> NDArray[np.float64]:
        """The time boundaries of the depletion problem.

        Return:
            Array: The time boundaries.

        """
        if self._time is None:
            with h5py.File(self.path) as f:
                time = f["time"][:, 0]
            self._time = time
        return self._time

    @property
    def number(self) -> NDArray[np.float64]:
        """Array of atom number for each time boundary, for each material, and for each nuclide.

        Returns:
            dict: An array for each material.

        """
        if self._number is None:
            number = {}
            with h5py.File(self.path) as f:
                raw_number = f["number"][...]
                for mat_id, material in self.materials.items():
                    number[mat_id] = raw_number[:, 0, material["index"], :]
            self._number = number
        return self._number

    @property
    def power(self) -> NDArray[np.float64]:
        """The power used to compute the depletion on the time step.

        Returns:
            Array: The array of power values.

        """
        if self._power is None:
            with h5py.File(self.path) as f:
                self._power = f["source_rate"][:, 0]
        return self._power

    @property
    def keffs_array(self) -> NDArray[ufloat]:
        """The eigenvalues for each depletion step.

        Returns:
            NDArray[ufloat]: the eigenvalue at each step with associated sigma.

        """
        if self._keffs is None:
            with h5py.File(self.path) as f:
                self._keffs = f["eigenvalues"][:, 0, :]
                self._keffs = unp.uarray(
                    nominal_values=f["eigenvalues"][:, 0, 0],
                    std_devs=f["eigenvalues"][:, 0, 1],
                )
        return self._keffs

    @property
    def rhos_array(self) -> NDArray[ufloat]:
        """The reactivity for each depletion step.

        Returns:
            NDArray[ufloat]: the reactivity at each step with associated sigma.

        """
        return (self.keffs_array - 1) / self.keffs_array * 1e5

    def keffs(self, time_unit: str = "d") -> pd.DataFrame:
        """The eigenvalues for each depletion step in a dataframe format.

        Args:
            time_unit (str): The unit in which the time should be expressed. (default: "d")

        Returns:
            pd.dataframe: the eigenvalue at each step with associated sigma.

        """
        converter = (1 * ureg.s).to(time_unit).magnitude
        str_index = [round(i, ndigits=10) for i in self.time * converter]
        index = pd.Index(str_index, name=f"Time [{time_unit}]")
        cols = ("keff", "keff std. dev.")
        data = np.array(
            [unp.nominal_values(self.keffs_array), unp.std_devs(self.keffs_array)]
        )
        return pd.DataFrame(data=data.T, index=index, columns=cols)

    def rhos(self, time_unit: str = "d") -> pd.DataFrame:
        """The reactivity values for each depletion step in a dataframe format.

        Args:
            time_unit (str): The unit in which the time should be expressed. (default: "d")

        Returns:
            pd.dataframe: reactivity at each step with associated sigma.

        """
        rho = (self.keffs_array - 1) / self.keffs_array * 1e5
        converter = (1 * ureg.s).to(time_unit).magnitude
        str_index = [round(i, ndigits=10) for i in self.time * converter]
        index = pd.Index(str_index, name=f"Time [{time_unit}]")
        cols = ("rho [pcm]", "rho std. dev. [pcm]")
        data = np.array([unp.nominal_values(rho), unp.std_devs(rho)])
        return pd.DataFrame(data=data.T, index=index, columns=cols)

    def get_atoms(
        self,
        unit: str = "atoms",
        time_unit: str = "d",
        multiindex: bool = False,
        squeeze: bool = True,
    ) -> Union[dict[int, pd.DataFrame], pd.DataFrame]:
        """Buiding an atom number dataframe for each material in the depletion problem.

        Args:
            unit (str): The unit in which the number of atoms should be expressed.
                        Can be volume averaged (e.g. 'atoms/cm**3') or not (e.g. 'atoms').
                        All pint unit strings homogeneous to either are valid values for this
                        argument. (default: 'atoms).
            time_unit (str): The unit in which the time should be expressed. (default: "d")
            multiindex (bool): If False, the dataframe will have a nuclide names as indices.
                               If True, a pd.MultiIndex will be used using a Z A I hierarchy.
                               (default: False)
            squeeze (bool): If True and the return dictionnary is of length 1, the method
                            will instead return the only dataframe in the dictionnary.
                            (default: True)

        Returns:
            dict: A dictionnary that associates a atom number dataframe to each material id
                  in the result file. If the dictionnary is of length 1 and the squeeze parameter
                  is True, returns a pd.DataFrame instead.

        """
        cols = np.round(self.time * ureg("s").to(time_unit).m, decimals=5)

        if multiindex:
            index_tuples = [
                (element(nuc), z_a_i(nuc)[1], z_a_i(nuc)[2]) for nuc in self.nuclides
            ]
            index = pd.MultiIndex.from_tuples(index_tuples, names=["Z", "A", "I"])
        else:
            index = self.nuclides

        dfs = {}
        for mat in self.materials:
            if ureg(unit).dimensionality == ureg.atom.dimensionality:
                multiplier = 1.0 * ureg("atom").to(unit).m
            elif ureg(unit).dimensionality == ureg("atom/cm**3").dimensionality:
                volume = self.materials[mat]["volume"]  # Material volume in cm**3
                multiplier = 1.0 / volume * ureg("atom/cm**3").to(unit).m
            else:
                raise ValueError(f"Forbidden atom number unit: {unit}")

            data = self.number[mat].T * multiplier
            dfs[mat] = pd.DataFrame(data=data, index=index, columns=cols)

        if squeeze and len(self.materials) == 1:
            key = list(self.materials.keys())[0]
            dfs = dfs[key]
        return dfs

    def get_mass(
        self,
        unit: str = "kg",
        time_unit: str = "d",
        multiindex: bool = False,
        squeeze: bool = True,
    ) -> Union[dict[int, pd.DataFrame], pd.DataFrame]:
        """Buiding an atom concentration dataframe for each material in the depletion problem.

        Args:
            unit (str): The unit in which mass should be expressed. Can be volume averaged
                        (e.g. 'g/cm**3') or not (e.g. 'kg'). All pint unit strings homogeneous to
                        either unit are valid values for this argument. (default: "kg").
            time_unit (str): The unit in which the time should be expressed. (default: "d")
            multiindex (bool): If False, the dataframe will have a nuclide names as indices. If True,
                                a pd.MultiIndex will be used using a Z A I hierarchy. (default: False)
            squeeze (bool): If True and the return dictionnary is of length 1, the method will instead return the only
                            dataframe in the dictionnary. (default: True)

        Returns:
            dict[int, pd.DataFrame] | pd.DataFrame: A dictionnary that associates a atom concentration dataframe
            to each material id in the result file. If the dictionnary is of length 1 and
            the squeeze parameter is True, returns a pd.DataFrame instead.

        """
        if ureg(unit).dimensionality == ureg("g").dimensionality:
            dfs = self.get_atoms(
                unit="atoms", time_unit=time_unit, multiindex=False, squeeze=False
            )
            multiplier = ureg("g").to(unit).m / AVOGADRO
        elif ureg(unit).dimensionality == ureg("g/cm**3").dimensionality:
            dfs = self.get_atoms(
                unit="atoms/cm**3", time_unit=time_unit, multiindex=False, squeeze=False
            )
            multiplier = ureg("g/cm**3").to(unit).m / AVOGADRO
        else:
            raise ValueError(f"Forbidden mass unit: {unit}")

        for i in self.materials:
            dfs[i] = dfs[i].apply(
                lambda atom: atom * atomic_mass(atom.name) * multiplier,
                axis=1,
            )

        if multiindex:
            for _, df in dfs.items():
                index_tuples = [
                    (element(nuc), z_a_i(nuc)[1], z_a_i(nuc)[2])
                    for nuc in self.nuclides
                ]
                index = pd.MultiIndex.from_tuples(index_tuples, names=["Z", "A", "I"])
                df.set_index(index, inplace=True)

        if squeeze and len(self.materials) == 1:
            key = list(self.materials.keys())[0]
            dfs = dfs[key]
        return dfs

    def get_activity(
        self,
        unit: str = "Bq",
        time_unit: str = "d",
        multiindex: bool = False,
        squeeze: bool = True,
    ) -> Union[dict[int, pd.DataFrame], pd.DataFrame]:
        """Buiding an atom activity dataframe for each material in the depletion problem.

        Args:
            unit (str): The unit in which activity should be expressed. Can be volume averaged
                        (e.g. 'Bq/cm**3') or not (e.g. 'Ci'). All pint unit strings homogeneous to
                        either unit are valid values for this argument. (default: "Bq")
            time_unit (str): The unit in which the time should be expressed. (default: "d")
            multiindex (bool): If False, the dataframe will have a nuclide names as indices. If True,
                                a pd.MultiIndex will be used using a Z A I hierarchy. (default: False)
            squeeze (bool): If True and the return dictionnary is of length 1, the method will instead return the only
                            dataframe in the dictionnary. (default: True)

        Returns:
            dict[int, pd.DataFrame] | pd.DataFrame: A dictionnary that associates a atom activity dataframe
            to each material id in the result file. If the dictionnary is of length 1 and
            the squeeze parameter is True, returns a pd.DataFrame instead.

        """
        if self.dconst is None:
            raise ValueError("No chain file provided, cannot compute activity.")
        if ureg(unit).dimensionality == ureg("Bq").dimensionality:
            dfs = self.get_atoms(
                unit="atoms", time_unit=time_unit, multiindex=False, squeeze=False
            )
            multiplier = ureg("Bq").to(unit).m
        elif ureg(unit).dimensionality == ureg("Bq/cm**3").dimensionality:
            dfs = self.get_atoms(
                unit="atoms/cm**3", time_unit=time_unit, multiindex=False, squeeze=False
            )
            multiplier = ureg("Bq/cm**3").to(unit).m
        else:
            raise ValueError(f"Forbidden activity unit: {unit}")

        for i in dfs:
            dfs[i] = dfs[i].apply(
                lambda x: x * self.dconst[x.name] * multiplier, axis=1
            )

        if multiindex:
            for _, df in dfs.items():
                index_tuples = [
                    (element(nuc), z_a_i(nuc)[1], z_a_i(nuc)[2])
                    for nuc in self.nuclides
                ]
                index = pd.MultiIndex.from_tuples(index_tuples, names=["Z", "A", "I"])
                df.set_index(index, inplace=True)

        if squeeze and len(self.materials) == 1:
            key = list(self.materials.keys())[0]
            dfs = dfs[key]
        return dfs

    def get_decay_heat(
        self,
        unit: str = "W",
        time_unit: str = "d",
        multiindex: bool = False,
        squeeze: bool = True,
    ) -> Union[dict[int, pd.DataFrame], pd.DataFrame]:
        """Buiding a decay heat dataframe for each material in the depletion problem.

        Args:
            unit (str): The unit in which activity should be expressed. Can be volume averaged
                        (e.g. 'W/cm**3') or not (e.g. 'kW'). All pint unit strings homogeneous to
                        either unit are valid values for this argument. (default: "W")
            time_unit (str): The unit in which the time should be expressed. (default: "d")
            multiindex (bool): If False, the dataframe will have a nuclide names as indices. If True,
                                a pd.MultiIndex will be used using a Z A I hierarchy. (default: False)
            squeeze (bool): If True and the return dictionnary is of length 1, the method will instead return the only
                            dataframe in the dictionnary. (default: True)

        Returns:
            dict[int, pd.DataFrame] | pd.DataFrame: A dictionnary that associates a decay heat dataframe
            to each material id in the result file. If the dictionnary is of length 1 and
            the squeeze parameter is True, returns a pd.DataFrame instead.

        """
        if self.dconst is None or self.decay_energy is None:
            raise ValueError("No chain file provided, cannot compute decay heat.")
        if ureg(unit).dimensionality == ureg("eV/s").dimensionality:
            dfs = self.get_atoms(
                unit="atoms", time_unit=time_unit, multiindex=False, squeeze=False
            )
            multiplier = ureg("eV/s").to(unit).m
        elif ureg(unit).dimensionality == ureg("eV/s/cm**3").dimensionality:
            dfs = self.get_atoms(
                unit="atoms/cm**3", time_unit=time_unit, multiindex=False, squeeze=False
            )
            multiplier = ureg("eV/s/cm**3").to(unit).m
        else:
            raise ValueError(f"Forbidden power unit: {unit}")

        for i in dfs:
            dfs[i] = dfs[i].apply(
                lambda x: x
                * self.dconst[x.name]
                * self.decay_energy[x.name]
                * multiplier,
                axis=1,
            )

        if multiindex:
            for _, df in dfs.items():
                index_tuples = [
                    (element(nuc), z_a_i(nuc)[1], z_a_i(nuc)[2])
                    for nuc in self.nuclides
                ]
                index = pd.MultiIndex.from_tuples(index_tuples, names=["Z", "A", "I"])
                df.set_index(index, inplace=True)

        if squeeze and len(self.materials) == 1:
            key = list(self.materials.keys())[0]
            dfs = dfs[key]
        return dfs

    def __call__(
        self, unit: str, **kwargs
    ) -> Union[dict[int, pd.DataFrame], pd.DataFrame]:
        """Buiding a dataframe for each material in the depletion problem, for a quantity of the specified unit.

        Args:
            unit (str): The unit in which the quantity should be expressed. All pint unit strings homogeneous to
                        either atoms, mass, activity and decay heat are valid values for this argument.
                        Accepted values are : "atom", "mass", "activity" and "heat".
            time_unit (str): The unit in which the time should be expressed. (default: "d")
            multiindex (bool): If False, the dataframe will have a nuclide names as indices. If True,
                                a pd.MultiIndex will be used using a Z A I hierarchy. (default: False)
            squeeze (bool): If True and the return dictionnary is of length 1, the method will instead return the only
                            dataframe in the dictionnary. (default: True)

        Returns:
            Union[dict[int, pd.DataFrame], pd.DataFrame]: A dictionnary that associates a dataframe
            to each material id in the result file. If the dictionnary is of length 1 and
            the squeeze parameter is True, returns a pd.DataFrame instead.

        """
        dimensions = {
            "atom": [ureg("atom").dimensionality, ureg("atom/cm**3").dimensionality],
            "mass": [ureg("g").dimensionality, ureg("g/cm**3").dimensionality],
            "activity": [ureg("Bq").dimensionality, ureg("Bq/cm**3").dimensionality],
            "heat": [ureg("W").dimensionality, ureg("W/cm**3").dimensionality],
        }
        if ureg(unit).dimensionality in dimensions["atom"]:
            return self.get_atoms(unit, **kwargs)
        if ureg(unit).dimensionality in dimensions["mass"]:
            return self.get_mass(unit, **kwargs)
        if ureg(unit).dimensionality in dimensions["activity"]:
            return self.get_activity(unit, **kwargs)
        if ureg(unit).dimensionality in dimensions["heat"]:
            return self.get_decay_heat(unit, **kwargs)

    def report(
        self,
        filename: str,
        params: Union[Iterable[str], Iterable[Dict]],
        multiindex: bool = False,
        dconst: bool = True,
        decay_energy: bool = True,
        keffs: bool = True,
    ):
        """Write an excel file containing the results from the depletion result file.

        Args:
            filename (str): The path to the file to write.
            params (Union[Iterable[str], Iterable[Dict]]): An iterable of the result sheet
            multiindex (bool): If False, the dataframe will have a nuclide names as indices. If True,
                                a pd.MultiIndex will be used using a Z A I hierarchy. (default: False)
            dconst (bool, optional): Wether to include a decay constants sheet. (defaults: False).
            decay_energy (bool, optional): Wether to include a decay energy sheet. (defaults: False).
            keffs (bool, optional): Wether to include a keffs sheet. (defaults: False).

        """
        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            if dconst:
                data = [
                    self.dconst[nuclide]
                    for nuclide in self("atoms", multiindex=False).index
                ]
                df = pd.DataFrame(
                    data=data, index=self("atoms", multiindex=multiindex).index
                )
                df.to_excel(writer, sheet_name="Decay Constant (s)")
            if decay_energy:
                data = [
                    self.decay_energy[nuclide]
                    for nuclide in self("atoms", multiindex=False).index
                ]
                df = pd.DataFrame(
                    data=data, index=self("atoms", multiindex=multiindex).index
                )
                df.to_excel(writer, sheet_name="Decay Energy (eV)")
            if keffs:
                df = self.get_keffs().join(self.get_rhos())
                df.to_excel(writer, sheet_name="Keff")
            if isinstance(params[0], str):
                for unit in params:
                    df = self(unit, multiindex=multiindex)
                    df.to_excel(writer, sheet_name=unit.replace("/", "|"))
            elif isinstance(params[0], dict):
                for param in params:
                    matid = param["mat"]
                    unit = param["unit"]
                    time_unit = param.get("time_unit", "d")
                    sheet_name = param["sheet_name"]
                    sheet_multiindex = param.get("multiindex", multiindex)
                    df = self(
                        unit,
                        time_unit=time_unit,
                        multiindex=sheet_multiindex,
                        squeeze=False,
                    )[matid]
                    df.to_excel(writer, sheet_name=sheet_name)

    def rr(
        self, time_unit: str = "d", squeeze: bool = True
    ) -> Union[dict[int, pd.DataFrame], pd.DataFrame]:
        """Buiding an reaction rate dataframe for each material in the depletion result file. Activity values are given
        in reaction/atom/s.

        Args:
            time_unit (str): The unit in which the time should be expressed. (default: "d")
            squeeze (bool): If True and the return dictionnary is of length 1, the method will instead return the only
                            dataframe in the dictionnary. (default: True)

        Returns:
            dict | pd.DataFrame: A dictionnary that associates a reaction rate dataframe
                                 to each material id in the result file. If the dictionnary is of length 1 and
                                 the squeeze parameter is True, returns a pd.DataFrame instead.

        """
        cols = np.round(self.time * ureg("s").to(time_unit).m, decimals=5)

        index = pd.MultiIndex.from_product(
            [self.rr_ids, self.reaction_ids], names=["nuclide", "reaction"]
        )
        dfs = {}
        for imat, matrix in self.reactions.items():
            shape = matrix.shape
            melted = matrix.reshape((shape[0], shape[1] * shape[2]))
            dfs[imat] = pd.DataFrame(data=melted.T, index=index, columns=cols)

        if squeeze and len(self.materials) == 1:
            key = list(self.materials.keys())[0]
            dfs = dfs[key]
        return dfs
