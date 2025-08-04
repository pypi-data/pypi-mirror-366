# SPDX-FileCopyrightText: 2021-2022 Thomas Kramer <code@tkramer.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List, Set
import sympy
from sympy.logic import boolalg
from .logic.types import CombinationalOutput


class CellType:
    """
    Description of a standard-cell type.
    A `CellType` object should contain information that is necessary for the characterization of this type of cells.
    """

    def __init__(self):
        self.power_down_function: boolalg.Boolean = None
        "Boolean expression that tells when the cell is not powered."
        self.inputs: List[sympy.Symbol] = []
        "Input pins of the cell."
        self.outputs: Dict[sympy.Symbol, CombinationalOutput] = dict()
        "Dictionary with output pins mapped to their boolean expressions."

    def get_tristate_outputs(self) -> Set[sympy.Symbol]:
        """
        Return all output pins which can be high-impedance.
        :return:
        """
        return {name for name, comb in self.outputs.items() if comb.is_tristate()}

    def human_readable_description(self) -> str:
        raise NotImplementedError()


class Combinational(CellType):
    """
    Purely combinational cell without any feed-back loops.
    """

    def __init__(self):
        super().__init__()


class Latch(CellType):

    def __init__(self):
        super().__init__()

        self.data_in = None
        self.enable = None  # Write condition / clock.
        self.clear = None  # Clear condition.
        self.preset = None  # Preset condition.

    def __str__(self):
        return self.human_readable_description()

    def human_readable_description(self) -> str:
        return f"""Latch {{
    write data: {self.data_in}
    write enable: {self.enable}
    clear: {self.clear}
    preset: {self.preset}
}}"""


class SingleEdgeDFF(CellType):
    """
    Single-edge triggered delay flip-flop.
    """

    def __init__(self):
        super().__init__()

        self.internal_state: sympy.Symbol = None
        self.internal_state_n: sympy.Symbol = None # TODO: Is this necessary? Or can it be avoided by substituting any references to this with `!internal_state`.
        """
        Variable for the current internal state.
        """

        self.clocked_on: boolalg.Boolean = sympy.false
        "Clocked when the value of the boolean expression rises to true."
        self.next_state: boolalg.Boolean = sympy.false
        "Next state that follows a clock edge."

        self.outputs: Dict[sympy.Symbol, CombinationalOutput] = dict()
        """
        Boolean functions for all outputs. The output functions
        are functions of the primary inputs and of the `internal_state` variable.
        """

        self.scan_enable = None
        "Name of the scan-enable input."
        self.scan_in = None

        self.async_preset: boolalg.Boolean = sympy.false
        "Preset condition."

        self.async_clear: boolalg.Boolean = sympy.false
        "Clear condition."

    def __str__(self):
        return self.human_readable_description()

    def clock_signal(self) -> sympy.Symbol:
        """
        Return the clock signal if there is exactly one clock signal.
        :return:
        """
        atoms = list(self.clocked_on.atoms(sympy.Symbol))
        if len(atoms) == 1:
            return atoms[0]
        else:
            return None

    def clock_edge_polarity(self) -> bool:
        """
        Get the polarity of the clock edge if there is exactly one clock signal.
        If there are multiple or no clock signal, return `None`.
        """
        clock = self.clock_signal()
        if clock is None:
            return None
        return self.clocked_on.subs({clock: True}) == True

    def human_readable_description(self) -> str:

        return f"""SingleEdgeDFF {{
    internal_state: {self.internal_state}
    next_state: {self.next_state}
    clocked_on: {self.clocked_on}
    active clock edge: {"rising" if self.clock_edge_polarity() else "falling"}
    outputs: {self.outputs}

    asynchronous preset: {self.async_preset} 
    asynchronous clear: {self.async_clear} 

    scan enable: {self.scan_enable}
    scan input: {self.scan_in}
}}"""
