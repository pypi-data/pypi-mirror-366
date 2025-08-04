# Copyright (c) 2021 Thomas Kramer.
# SPDX-FileCopyrightText: 2022 Thomas Kramer <code@tkramer.ch>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from .functional_abstraction import *

import itertools
import networkx as nx
from typing import Any, Dict, List, Iterable, Tuple, Set, Optional, Union
from enum import Enum
import collections
import sympy
from sympy.logic import satisfiable, simplify_logic as sympy_simplify_logic
from sympy.logic import boolalg

import logging

from ..cell_types import Latch, SingleEdgeDFF

# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

"""
Recognize sequential cells based on the output of the `functional_abstraction.analyze_circuit_graph()` function.

For each class of cells (latch, single-edge triggered flip-flop, ...) a Extractor class should be created.
The extractor class tries to recognize the cell from an abstract formal description.
For recognizing an unknown cell, all extractor classes are tried until one finds a match.
"""


# def find_clear_and_preset_signals(f: boolalg.Boolean) -> Dict[boolalg.BooleanAtom, Tuple[bool, bool]]:
#     """
#     Find the variables in a boolean formula that can either force the formula to True or False.
#     :param f:
#     :return: Dict[Variable symbol, (is preset, is active high)]
#     """
#     results = dict()
#     atoms = f.atoms(sympy.Symbol)
#     for a in atoms:
#         for v in [False, True]:
#             f.subs({a: v})
#             if f == sympy.true and f != sympy.false:
#                 results[a] = (True, v)
#             elif f == sympy.false and f != sympy.true:
#                 results[a] = (False, v)
#     return results
#
# def test_find_clear_and_preset_signals():
#     a = sympy.Symbol('a')
#     clear = sympy.Symbol('clear')
#     preset = sympy.Symbol('preset')

def find_boolean_isomorphism(a: boolalg.Boolean, b: boolalg.Boolean) -> Optional[
    Dict[boolalg.BooleanAtom, boolalg.BooleanAtom]]:
    """
    Find a one-to-one mapping of the variables in `a` to the variables in `b` such that the both formulas are
    equivalent. Return `None` if there is no such mapping.
    The mapping is not necessarily unique.
    :param a:
    :param b:
    :return:
    """

    a_vars = list(a.atoms(sympy.Symbol))
    b_vars = list(b.atoms(sympy.Symbol))

    if len(a_vars) != len(b_vars):
        return None

    # Do a brute-force search.
    for b_vars_perm in itertools.permutations(b_vars):
        substitution = {old: new for old, new in zip(a_vars, b_vars_perm)}
        a_perm = a.subs(substitution)
        # Check for structural equality first, then for mathematical equality.
        if a_perm == b or bool_equals(a_perm, b):
            return substitution

    return None


def test_find_boolean_isomorphism():
    assert find_boolean_isomorphism(sympy.true, sympy.true) is not None
    assert find_boolean_isomorphism(sympy.true, sympy.false) is None

    a, b, c, x, y, z = sympy.symbols('a b c x y z')
    f = (a & b) | c
    g = (x & y) | z
    mapping = find_boolean_isomorphism(f, g)
    assert mapping == {a: x, b: y, c: z} or mapping == {a: y, b: x, c: z}

    # MUX
    f = (a & c) | (b & ~c)
    g = ~((~x & z) | (~y & ~z))
    mapping = find_boolean_isomorphism(f, g)
    print(mapping)
    assert mapping == {a: x, b: y, c: z} 


class LatchExtractor:
    def __init__(self):
        pass

    def extract(self, c: AbstractCircuit) -> Optional[Latch]:
        """
        Try to recognize a latch based on the abstract circuit representation.
        :param c:
        :return:
        """
        logger.debug("Try to extract a latch.")
        if len(c.latches) != 1:
            logger.debug(f"Not a latch. Wrong number of latches. Need 1, found {len(c.latches)}.")
            return None

        output_nets = list(c.output_pins)
        if len(output_nets) != 1:
            logger.debug(f"Expect 1 output net, found {len(output_nets)}.")
            return None

        # Trace back the output towards the inputs.
        output_net = output_nets[0]
        output = c.outputs[output_net]

        # Check that the output is not tri-state.
        if output.is_tristate():
            logger.debug("Can't recognize DFF with tri-state output.")
            return None

        # Trace back the output towards the inputs.
        latch_path = []
        current_nodes = set(output.function.atoms(sympy.Symbol))
        while current_nodes:
            node = current_nodes.pop()
            if node in c.outputs:
                next = c.outputs[node]
                current_nodes.update(next.function.atoms(sympy.Symbol))
            elif node in c.latches:
                latch = c.latches[node]
                assert isinstance(latch, Memory)

                latch_path.append(latch)
                current_nodes = set(latch.data.atoms(sympy.Symbol))
            else:
                # Cannot further resolve the node, must be an input.
                logger.debug(f"Input node: {node}")

        if len(latch_path) != 1:
            logger.debug(f"No latch found in the fan-in tree of the outputs {output.function.atoms()}.")
            return None

        latch = latch_path[0]

        # Find preset / clear conditions.
        enable_signals = sorted(latch.write_condition.atoms(sympy.Symbol), key=lambda s: s.name)
        logger.debug(f"Potential clock/set/preset signals {enable_signals}")

        # Find preset condition.
        preset_condition = simplify_logic(latch.data & latch.write_condition)
        logger.info(f"Preset condition: {preset_condition}")

        # Find clear condition.
        clear_condition = simplify_logic(~latch.data & latch.write_condition)
        logger.info(f"Clear condition: {clear_condition}")

        # Find single signals that satisfy the preset.
        preset_signals = [s for s in enable_signals if bool_equals(preset_condition.subs({s: True}), sympy.true)]
        preset_signals_inv = [s for s in enable_signals if bool_equals(preset_condition.subs({s: False}), sympy.true)]
        logger.info(f"Preset signals (active high): {preset_signals}")
        logger.info(f"Preset signals (active low): {preset_signals_inv}")

        # Find single signals that satisfy the clear condition.
        clear_signals = [s for s in enable_signals if bool_equals(clear_condition.subs({s: True}), sympy.true)]
        clear_signals_inv = [s for s in enable_signals if bool_equals(clear_condition.subs({s: False}), sympy.true)]
        logger.info(f"Clear signals (active high): {clear_signals}")
        logger.info(f"Clear signals (active low): {clear_signals_inv}")

        result = Latch()
        result.outputs = {output_net: output}
        result.enable = latch.write_condition
        result.data_in = latch.data
        result.clear = clear_condition
        result.preset = preset_condition

        return result


class DFFExtractor:
    def __init__(self):
        pass

    def extract(self, c: AbstractCircuit) -> Optional[SingleEdgeDFF]:
        """
        Try to recognize a single-edge triggered D-flip-flop based on the abstract circuit representation.
        :param c:
        :return:
        """
        logger.debug("Try to extract a D-flip-flop.")
        if len(c.latches) != 2:
            logger.debug(f"Not a flip-flop. Wrong number of latches. Need 2, found {len(c.latches)}.")
            return None

        output_nets = list(c.output_pins)
        if len(output_nets) not in [1, 2]:
            logger.debug(f"Expect 1 or 2 output nets, found {len(output_nets)}.")
            return None

        # Trace back the output towards the inputs.
        outputs = [c.outputs[n] for n in output_nets]

        # Check that the output is not tri-state.
        for output in outputs:
            if output.is_tristate():
                logger.warning(f"'{output}' is a tri-state output.")
                logger.warning("Can't recognize DFF with tri-state output.")
                return None

        # Trace back the output towards the inputs.
        latch_path = []
        current_nodes = set()
        for output in outputs:
            current_nodes.update(output.function.atoms(sympy.Symbol))
        while current_nodes:
            node = current_nodes.pop()
            if node in c.outputs:
                next = c.outputs[node]
                current_nodes.update(next.function.atoms(sympy.Symbol))
            elif node in c.latches:
                latch = c.latches[node]
                assert isinstance(latch, Memory)

                latch_path.append((latch, node))
                current_nodes = set(latch.data.atoms(sympy.Symbol))
            else:
                # Cannot further resolve the node, must be an input.
                logger.debug(f"Input node: {node}")

        # Find trigger condition of the flip-flop.
        latch1, latch1_output_node = latch_path[1]
        latch2, latch2_output_node = latch_path[0]

        # Find condition such that the FF is in normal operation mode.
        # I.e. no set or reset is active.
        ff_normal_condition = simplify_logic(latch1.write_condition ^ latch2.write_condition)
        logger.debug(f"FF normal-mode condition: {ff_normal_condition}")

        # Find clock inputs of the latches.
        latch1_write_normal = simplify_with_assumption(assumption=ff_normal_condition, formula=latch1.write_condition)
        latch2_write_normal = simplify_with_assumption(assumption=ff_normal_condition, formula=latch2.write_condition)

        logger.debug(f"Latch clocks: {latch1_write_normal}, {latch2_write_normal}")

        clocked_on = simplify_logic(~latch1_write_normal & latch2_write_normal)
        logger.debug(f"clocked_on: {clocked_on}")

        clock_signals = set(latch1_write_normal.atoms(sympy.Symbol)) | set(latch2_write_normal.atoms(sympy.Symbol))
        if len(clock_signals) != 1:
            logger.warning(f"Clock must be a single signal. Found: {clock_signals}")
            return None

        clock_signal = clock_signals.pop()
        logger.info(f"Clock signal: {clock_signal}")

        assert not satisfiable(boolalg.Equivalent(latch1_write_normal, latch2_write_normal)), \
            "Clock polarities of latches must be complementary."

        # Find polarity of the active clock-edge.
        active_edge_polarity = latch2_write_normal.subs({clock_signal: True})

        # Sanity check: The both latches must be transparent for the opposite phases of the clock.
        assert active_edge_polarity == latch1_write_normal.subs({clock_signal: False}), \
            "Latches must be transparent in opposite phases of the clock."

        logger.info(f"Active edge polarity: {'rising' if active_edge_polarity else 'falling'}")

        # Assemble D-flip-flop description object.
        dff = SingleEdgeDFF()
        dff.clocked_on = clocked_on
        # dff.clock_edge_polarity = active_edge_polarity

        # == Detect asynchronous set/reset signals ==
        potential_set_reset_signals = list((set(latch1.write_condition.atoms(sympy.Symbol))
                                            | set(latch2.write_condition.atoms(sympy.Symbol))) - {clock_signal}
                                           )
        logger.debug(
            f"Potential asynchronous set/reset signals: {sorted(potential_set_reset_signals, key=lambda n: n.name)}")

        if potential_set_reset_signals:
            # More than 2 asynchronous set/reset signals are not supported.
            if len(potential_set_reset_signals) > 2:
                logger.error(f"Cannot recognize flip-flops with more than 2 asynchronous set/reset signals "
                             f"(found {potential_set_reset_signals}).")
                return None

            # Find signal values such that the FF is in normal operation mode.
            inactive_set_reset_models = list(satisfiable(ff_normal_condition, all_models=True))
            if len(inactive_set_reset_models) != 1:
                logger.warning(f"There's not exactly one signal assignment such that the FF is in normal mode: "
                               f"{inactive_set_reset_models}")
            assert inactive_set_reset_models, f"Normal operation condition is not satisfiable: {ff_normal_condition}."

            # Determine polarity of the set/reset signals.
            sr_disabled_values = inactive_set_reset_models[0]
            logger.info(f"Set/reset disabled when: {sr_disabled_values}")
            sr_enabled_values = {k: not v for k, v in sr_disabled_values.items()}
            logger.info(f"Set/reset enabled when: {sr_enabled_values}")

            async_set_signals = []
            async_reset_signals = []

            # Find if the signals are SET or RESET signals.
            # Set just one to active and observe the flip-flop output.
            for signal in potential_set_reset_signals:
                one_active = sr_disabled_values.copy()
                signal_value = sr_enabled_values[signal]
                one_active.update({signal: signal_value})

                wc2 = latch2.write_condition.subs(one_active)
                data2 = latch2.data.subs(one_active)
                assert bool_equals(wc2, True)
                if data2:
                    logger.info(f"{signal} is an async SET/PRESET signal, active {'high' if signal_value else 'low'}.")
                    async_set_signals.append((signal, signal_value))
                else:
                    logger.info(f"{signal} is an async RESET/CLEAR signal, active {'high' if signal_value else 'low'}.")
                    async_reset_signals.append((signal, signal_value))

            # TODO: Find out what happens when all asynchronous set/reset signals are active at the same time.
            all_sr_active_wc = latch2.write_condition.subs(sr_enabled_values)
            all_sr_active_data = latch2.data.subs(sr_enabled_values)
            # TODO

            if len(async_set_signals) > 1:
                logger.error(f"Multiple async SET/PRESET signals: {async_set_signals}")
            if len(async_reset_signals) > 1:
                logger.error(f"Multiple async RESET/CLEAR signals: {async_reset_signals}")

            # Store the results in the flip-flop description object.
            if async_set_signals:
                async_preset, async_set_polarity = async_set_signals[0]
                # TODO: This can be simplified by just finding the 'preset' condition.
                if async_set_polarity:
                    dff.async_preset = async_preset
                else:
                    dff.async_preset = ~async_preset
            if async_reset_signals:
                async_clear, async_reset_polarity = async_reset_signals[0]
                if async_reset_polarity:
                    dff.async_clear = async_clear
                else:
                    dff.async_clear = ~async_clear

        # Eliminate Set/Reset.
        latch1_data_normal = simplify_with_assumption(ff_normal_condition, latch1.data)
        latch2_data_normal = simplify_with_assumption(ff_normal_condition, latch2.data)
        # Eliminate clock.
        latch1_data_normal = latch1_data_normal.subs({clock_signal: not active_edge_polarity})
        latch2_data_normal = latch2_data_normal.subs({clock_signal: active_edge_polarity})

        ff_internal_state_name = sympy.Symbol('IQ')
        ff_internal_state_node = latch2_output_node

        # Resolve the data which gets written into the internal state on a clock edge.
        # Find data that gets written into the flip-flop in normal operation mode.
        ff_data_next = simplify_with_assumption(ff_normal_condition, ff_internal_state_node)

        # Resolve through second latch.
        ff_data_next = ff_data_next.subs({
            latch2_output_node: latch2_data_normal,
            clock_signal: active_edge_polarity
        })

        # Resolve through first latch.
        ff_data_next = ff_data_next.subs({
            latch1_output_node: latch1_data_normal,
            clock_signal: not active_edge_polarity
        })
        ff_data_next = simplify_logic(ff_data_next)

        dff.internal_state = ff_internal_state_name

        # Normalize by removing inversions.
        if type(ff_data_next) == boolalg.Not:
            ff_data_next = ~ff_data_next
            ff_internal_state_name = ~ff_internal_state_name

        # Store the formula of the next state.
        dff.next_state = ff_data_next

        logger.debug(f"Flip-flop output data: {dff.next_state}")

        # Find combinational output formulas. They may depend on the internal state of the flip-flop.
        ff_outputs = dict()
        for output_net in output_nets:

            # Find combinational function of the output net.
            # It should be a function of the primary inputs and of latch outputs.
            output_function = c.outputs[output_net].function
            high_impedance = c.outputs[output_net].high_impedance

            # Find data that gets written into the flip-flop in normal operation mode.
            output_formula = simplify_with_assumption(ff_normal_condition, output_function)

            # Resolve through second latch.
            output_formula = output_formula.subs({
                ff_internal_state_node: ff_internal_state_name
            })
            high_impedance = high_impedance.subs({
                ff_internal_state_node: ff_internal_state_name
            })

            logger.debug(f"Output: {output_net} = {output_formula}")
            comb = CombinationalOutput(function=output_formula, high_impedance=high_impedance)
            ff_outputs[output_net] = comb

        # Store the output functions.
        dff.outputs = ff_outputs

        # if len(ff_output_data) == 1:
        #     # FF has only one output.
        #     logger.info(f"{output_nets[0]} = {ff_output_data[0]}")
        #     out_data = ff_output_data[0]
        #     dff.data_in = out_data
        #     dff.data_out = output_nets[0]
        # elif len(ff_output_data) == 2:
        #     # Check if the outputs are inverted versions.
        #
        #     out1, out2 = output_nets
        #     out1_data, out2_data = ff_output_data
        #
        #     # Check if the outputs are inverses.
        #     if out1_data == boolalg.Not(out2_data):
        #         logger.debug("Outputs are inverses of each other.")
        #     else:
        #         logger.warning("If a flip-flop has two outputs, then need to be inverses of each other.")
        #         return None
        #
        #     # Find the inverted and non-inverted output.
        #     if type(out1_data) == boolalg.Not:
        #         assert type(out2_data) != boolalg.Not
        #         out_inv_net = out1
        #         out_net = out2
        #         out_inv_data = out1_data
        #         out_data = out2_data
        #     else:
        #         assert type(out2_data) == boolalg.Not
        #         out_inv_net = out2
        #         out_net = out1
        #         out_inv_data = out2_data
        #         out_data = out1_data
        #
        #     logger.info(f"Non-inverted output: {out_net} = {out_data}")
        #     logger.info(f"Inverted output: {out_inv_net} = {out_inv_data}")
        #
        #     dff.data_in = out_data
        #     dff.data_out = out_net
        #     dff.data_out_inv = out_inv_net
        # else:
        #     assert False

        # Analyze boolean formula of the next flip-flop state.
        # In the simplest case of a D-flip-flop this is just one variable.
        # But there might also be a scan-chain multiplexer or synchronous
        # clear/preset logic.
        data_variables = ff_data_next.atoms(sympy.Symbol)
        num_variables = len(data_variables)

        if num_variables == 1:
            # Simple. Only a data variable, no clear/preset/scan.
            pass
        elif num_variables == 2:
            # There might be a synchronous clear/preset.
            logger.debug(f"Try to detect a synchronous clear or preset from the two data signals {data_variables}.")
            # It is not possible to distinguish data input from clear/preset based only on
            # the boolean formula.
            d, clear, preset = sympy.symbols('d clear preset')
            with_clear = d & clear
            with_preset = d | preset
            if find_boolean_isomorphism(ff_data_next, with_clear) is not None:
                logger.info("Detected synchronous clear.")
            if find_boolean_isomorphism(ff_data_next, with_preset) is not None:
                logger.info("Detected synchronous preset.")
        elif num_variables == 3:
            # Either synchronous clear/preset or scan.
            logger.debug("Try to detect scan-mux.")
            d, scan_enable, scan_in = sympy.symbols('d scan_enable scan_in')

            scan_mux = (scan_in & scan_enable) | (d & ~scan_enable)

            mapping = find_boolean_isomorphism(scan_mux, ff_data_next)
            if mapping is not None:
                logger.info(f"Detected scan-chain mux: {mapping}")
                dff.scan_in = mapping[scan_in]
                dff.scan_enable = mapping[scan_enable]

        else:
            logger.warning(f"Flip-flop data depends on {num_variables} variables."
                           f" Cannot distinguish scan-mux, clear, preset.")

        return dff


def extract_sequential_circuit(c: AbstractCircuit) -> Optional[Union[Latch, SingleEdgeDFF]]:
    logger.debug("Recognize sequential cells.")
    logger.debug(f"Combinational formulas: {c.outputs}")
    logger.debug(f"Latches: {c.latches}")

    extractors = [LatchExtractor(), DFFExtractor()]

    for ex in extractors:
        result = ex.extract(c)
        if result is not None:
            return result
    return None

def find_flipflop_state_control_and_observe_pins(
    cell_type: SingleEdgeDFF,
    other_inputs: Dict[sympy.Symbol, sympy.Symbol]
) -> List[Tuple[str, Dict[str, bool]]]:
    """
    Find data input pins which control the state of the flip-flop.


    Returns a list of pins which can control the flip-flop state together with 
    1) an assignment of other input values (clear, preset, ...) such that the input pin becomes controlling
    2) a list of output pins which allow to observe the internal state with the given other input values
    """

    assert isinstance(cell_type, SingleEdgeDFF), "cell_type must be a SingleEdgeDFF"
    
    # Find all data pins that are relevant for the internal state of the flip-flop.
    data_in_pins = sorted(cell_type.next_state.atoms(sympy.Symbol))
    logger.debug(f"Input pins relevant for internal state: {data_in_pins}")

    # Find data input pins which can control the output pin.
    controlling_input_pins = []
    for data_in_pin in data_in_pins:
    
        # Find all assignments of the other data pins such that the data pin controls
        # the internal state.
        # Find values of the other pins such that:
        #  next_state(data_in_pin=0, other_pins) != next_state(data_in_pin=1, other_pins)
        next_state_0 = cell_type.next_state.subs({data_in_pin: False})
        next_state_1 = cell_type.next_state.subs({data_in_pin: True})
        models = list(satisfiable(next_state_0 ^ next_state_1, all_models=True))

        for other_pin_values in models:
            # Express the assignment of the other pins as a boolean formula.
            # This will also be used as a 'when' statement in the liberty file.
            when_other_inputs = sympy.And(*(pin if value else ~pin for pin, value in other_pin_values.items()))
            logger.info(f"Measure clock-to-output delay with data input {data_in_pin} when {when_other_inputs}.")

            # Set static voltages of other input pins.
            other_pin_values.update(other_inputs)
            
            logger.debug(f"Pin {data_in_pin} controls the flip-flop state when: {other_pin_values}")
            

            static_input_voltages = dict()
            for pin, value in other_pin_values.items():
                if not isinstance(pin, sympy.Symbol):
                    continue
                value = value == True
                pin = str(pin)
                logger.debug(f"{pin} = {value} V")
                static_input_voltages[pin] = value
                
            # Find an output pin such that the internal state is observable.
            observer_outputs = []  # Output pins that can observe the internal memory state.
            for output_pin, output in cell_type.outputs.items():
                function = output.function
                # Substitute with constant input pins.
                function = function.subs(other_pin_values)

                # Compute the output for all values of the internal state and make sure it is different.
                function0 = function.subs({cell_type.internal_state: False})
                function1 = function.subs({cell_type.internal_state: True})
                is_observable = not satisfiable(~(function0 ^ function1))  # Test if function0 != function1

                logger.debug(f"Internal state {cell_type.internal_state} observable from output {output_pin} "
                             f"when {other_pin_values}: {is_observable}")

                if is_observable:
                    observer_outputs.append(output_pin)

            logger.debug(f"Internal state is observable from: {observer_outputs}")

            # Remember the pin which controls the internal state and the the required
            # voltages at the other pins.
            controlling_input_pins.append((str(data_in_pin), static_input_voltages, observer_outputs, when_other_inputs))

    return controlling_input_pins


