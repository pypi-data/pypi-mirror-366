# SPDX-FileCopyrightText: 2019-2024 Thomas Kramer <code@tkramer.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

from .util import *
from ..cell_types import SingleEdgeDFF
from . import timing_sequential as seq
from ..liberty import util as liberty_util
from ..logic import seq_recognition
from ..characterization.ngspice_subprocess import NgSpiceInteractive, CellSimulation
from ..lccommon.net_util import get_subcircuit_ports

from liberty.types import *
import numpy as np
from sympy.logic import satisfiable

def characterize_flip_flop_output(
        simulation: CellSimulation,
        new_library: Group,
        new_cell_group: Group,
        conf: CharacterizationConfig,
        cell_type: SingleEdgeDFF,
        cell_conf: CellConfig,
        related_pin_transition: np.ndarray,
        input_transition_times: np.ndarray,
        output_capacitances: np.ndarray,
):
    assert isinstance(simulation, CellSimulation)
    assert isinstance(cell_type, SingleEdgeDFF)

    logger.info("Characterize single-edge triggered flip-flop.")

    if related_pin_transition is None:
        logger.error("'related-pin-transition' is not specified for the clock pin.")

    assert related_pin_transition is not None, "'related-pin-transition' is not specified for the clock pin."

    # Create or update the 'ff' group.
    ff_groups = new_cell_group.get_groups('ff')
    if not ff_groups:
        ff_group = Group('ff')
        new_cell_group.groups.append(ff_group)
    else:
        ff_group = ff_groups[0]

    # Store content of 'ff' group.
    ff_group.args = [str(cell_type.internal_state), str(cell_type.internal_state) + "_INV"]
    ff_group.set_boolean_function('clocked_on', cell_type.clocked_on)
    ff_group.set_boolean_function('next_state', cell_type.next_state)
    if cell_type.async_preset:
        ff_group.set_boolean_function('preset', cell_type.async_preset)
    if cell_type.async_clear:
        ff_group.set_boolean_function('clear', cell_type.async_clear)

    # Find clock pin.
    clock_signals = list(cell_type.clocked_on.atoms(sympy.Symbol))
    if len(clock_signals) != 1:
        logger.error(f"Expect exactly one clock signal. Got {clock_signals}")
    clock_signal = clock_signals[0]
    # Find clock polarity:
    clock_edge_polarity = cell_type.clocked_on.subs({clock_signal: True})
    clock_pin = str(clock_signal.name)

    assert isinstance(clock_pin, str)

    logger.info(f"Clock signal: {clock_pin}")
    logger.info(f"Clock polarity: {'rising' if clock_edge_polarity else 'falling'}")

    # Find preset/clear signals.
    # Make sure preset/clear are disabled.
    preset_condition = cell_type.async_preset
    clear_condition = cell_type.async_clear

    assert preset_condition is not None, "preset condition must not be `None`" 
    assert clear_condition is not None, "clear condition must not be `None`"

    # Find a variable assignment such that neither preset nor clear is active.
    no_preset_no_clear = list(satisfiable(~preset_condition & ~clear_condition, all_models=True))
    for model in no_preset_no_clear:
        logger.info(f"FF in normal operation mode when: {model}")
    preset_clear_input = no_preset_no_clear[0]
    if len(no_preset_no_clear) > 1:
        logger.warning(f"Multiple possibilities found for disabling preset and clear. "
                       f"Take the first one ({preset_clear_input}).")

    # Find all data pins that are relevant for the internal state of the flip-flop.
    data_in_pins = sorted(cell_type.next_state.atoms(sympy.Symbol))
    logger.debug(f"Input pins relevant for internal state: {data_in_pins}")

    assert isinstance(cell_type.internal_state,
                      sympy.Symbol), "Internal flip-flop-state variable is not defined."

    # Find all output pins that depend on the internal state.
    data_out_pins: List[sympy.Symbol] = [name for name, output in cell_type.outputs.items()
                                         if cell_type.internal_state in output.function.atoms()
                                         ]
    logger.debug(f"Output pins that depend on the internal state: {data_out_pins}")

    
    # Remember a clock pulse width which for sure samples a stable data signal.
    clock_pulse_width_guess = 0

    # TODO use this function to simplify the below code.
    ## Find data input pins which can control the output pin.
    #control_and_observe_pins = find_flipflop_state_control_and_observe_pins(cell_type, preset_clear_input)
    #assert len(control_and_observe_pins) > 0, "No input pin found which can control the flip-flop state."

    static_inputs_and_observer_outputs = seq_recognition.find_flipflop_state_control_and_observe_pins(
                                    cell_type, preset_clear_input
                                )
    
    # Characterize setup/hold for each data pin.
    for i, data_in_pin in enumerate(data_in_pins):
        logger.info(f"Measure constraints of pin {data_in_pin} ({i}/{len(data_in_pins)}).")
        
        for input_pin, static_inputs, observer_outputs, when_other_inputs in static_inputs_and_observer_outputs:
            if input_pin != str(data_in_pin):
                continue

            if not observer_outputs:
                # When the internal state is not observable we cannot measure constraints.
                # Skip this combination.
                logger.warning(
                    f"Internal memory state {cell_type.internal_state} is not observable from any output "
                    f"when {static_inputs}. Skipping input combination.")
                continue
        
            # Take just one of the observer output pins.
            data_out_pin = observer_outputs[0]
            logger.debug(f"Output pin: {data_out_pin}")

            # == Start characterization ==

            # Convert from sympy.Symbol to string.
            data_in_pin = str(data_in_pin)
            data_out_pin = str(data_out_pin)

            # Convert boolean values to input voltages.
            static_input_voltages = {
                pin: cell_conf.global_conf.supply_voltage if value==True else 0 
                for pin, value in static_inputs.items()
            }

            def find_min_clock_pulse_width(clock_pulse_polarity: bool, rising_data_edge: bool):
                min_clock_pulse_width, delay = seq.find_minimum_clock_pulse_width(
                    simulation=simulation,
                    cell_config=cell_conf,
                    ff_clock_edge_polarity=clock_edge_polarity,
                    clock_input=clock_pin,
                    data_in=data_in_pin,
                    data_out=data_out_pin,
                    setup_time=2e-9,  # Choose a reasonably large setup time.
                    clock_pulse_polarity=clock_pulse_polarity,
                    rising_data_edge_in=rising_data_edge,
                    clock_rise_time=10e-12,  # TODO: Something fails when 0.
                    clock_fall_time=10e-12,  # TODO: How to choose this?
                    output_load_capacitances={data_out_pin: 0},
                    clock_pulse_width_guess=100e-12,
                    max_delay_estimation=1e-7,
                    static_input_voltages=static_input_voltages,
                )
                logger.debug(f'min_clock_pulse_width = {min_clock_pulse_width}, delay = {delay}')
                return min_clock_pulse_width, delay

            # Find the minimal clock pulse for negative and positive pulses.
            # For each pulse type inspect rising and falling data edges.
            logger.info(f"Find minimal clock pulse width ({clock_pin}).")
            min_pulse_width_low, _delay = max(find_min_clock_pulse_width(False, False),
                                              find_min_clock_pulse_width(False, True))
            logger.info(f"min_pulse_width_low = {min_pulse_width_low} s")
            min_pulse_width_high, _delay = max(find_min_clock_pulse_width(True, False),
                                               find_min_clock_pulse_width(True, True))
            logger.info(f"min_pulse_width_high = {min_pulse_width_high} s")
            
            # Find the shortest clock pulse width which samles a stable data signal for all cases.
            clock_pulse_width_guess = max(clock_pulse_width_guess, min_pulse_width_low, min_pulse_width_high)

            # Write information on clock pin to liberty.
            # TODO: minimum pulse width is potentially computed for many different input combinations. Take min/max of them! (Now just the last one will be stored)
            clock_pin_group = new_cell_group.get_group('pin', clock_pin)
            clock_pin_group['clock'] = 'true'
            clock_pin_group['min_pulse_width_high'] = min_pulse_width_high / conf.time_unit
            clock_pin_group['min_pulse_width_low'] = min_pulse_width_low / conf.time_unit

            # Find setup and hold times.
            result = seq.characterize_flip_flop_setup_hold(
                simulation=simulation,
                cell_conf=cell_conf,
                data_in_pin=data_in_pin,
                data_out_pin=data_out_pin,
                clock_pin=clock_pin,
                clock_edge_polarity=clock_edge_polarity,

                constrained_pin_transition=input_transition_times,
                related_pin_transition=related_pin_transition,

                output_load_capacitance=0,  # TODO: Is it accurate to assume zero output load?

                static_input_voltages=static_input_voltages
            )

            # Get the table indices.
            # TODO: get correct index/variable mapping from liberty file.
            index_1 = result['related_pin_transition'] / conf.time_unit
            index_2 = result['constrained_pin_transition'] / conf.time_unit
            # TODO: remember all necessary templates and create template tables.

            input_pin_group = new_cell_group.get_group('pin', data_in_pin)

            clock_edge = 'rising' if clock_edge_polarity else 'falling'

            # Add setup/hold information to the liberty pin group.
            for constraint_type in ['hold', 'setup']:
                template_table = liberty_util.create_constraint_template_table(
                    new_library, constraint_type, len(index_1), len(index_2)
                )
                table_template_name = template_table.args[0]

                rise_constraint = Group('rise_constraint', args=[table_template_name])
                rise_constraint.set_array('index_1', index_1)
                rise_constraint.set_array('index_2', index_2)
                rise_constraint.set_array(
                    'values',
                    result[f'{constraint_type}_rise_constraint'] / conf.time_unit
                )

                fall_constraint = Group('fall_constraint', args=[table_template_name])
                fall_constraint.set_array('index_1', index_1)
                fall_constraint.set_array('index_2', index_2)
                fall_constraint.set_array(
                    'values',
                    result[f'{constraint_type}_fall_constraint'] / conf.time_unit
                )

                timing_group = Group(
                    'timing',
                    attributes=[
                        Attribute('timing_type', f'{constraint_type}_{clock_edge}'),
                        Attribute('related_pin', EscapedString(clock_pin))
                    ],
                    groups=[rise_constraint, fall_constraint]
                )

                if len(when_other_inputs.atoms(sympy.Symbol)) > 0:
                    timing_group.set_boolean_function('when', when_other_inputs)

                input_pin_group.groups.append(timing_group)

    
    # Measure clock-to-output delays.
    for data_out_pin in data_out_pins:
        
        logger.info(f"Measure clock-to-output delay for output '{data_out_pin}'")
        
        output_function = cell_type.outputs[data_out_pin].function
        logger.info(f"Output function: {output_function}")

        
        # Convert output pin to string
        data_out_pin_name = str(data_out_pin)
    
        output_pin_group = new_cell_group.get_group('pin', data_out_pin_name)
        output_pin_group.set_boolean_function('function', output_function)
        related_pin = clock_pin
        
        assert len(static_inputs_and_observer_outputs) > 0, "No input pin found which can control the flip-flop state."
            
        # Select an input pin and a combination of other input values such that the input pin controls output of the flip-flop.
        data_in_pin, static_input_values, observer_outputs, _when_other_inputs = static_inputs_and_observer_outputs[0]

        assert data_out_pin in observer_outputs, f"Flip-flop state is not observable from {data_out_pin} when {static_input_values}."
        
        # Determine if this output is the inverse of the internal state given the current static assignments of the other inputs.
        assignment = static_input_values.copy()
        assignment.update({cell_type.internal_state: False, cell_type.internal_state_n: True})
        is_output_inverted = output_function.subs({var: val for var, val in assignment.items() if var is not None})

        # Determine if the non-inverted internal state is really not inverted (it might be inverted).
        input0 = static_input_values.copy()
        input1 = static_input_values.copy()
        input0[data_in_pin] = False
        input1[data_in_pin] = True
        
        next_state_input0 = cell_type.next_state.subs(input0)
        next_state_input1 = cell_type.next_state.subs(input1)

        # Sanity check.
        assert next_state_input0 != next_state_input1, f"state is not controllable by input {data_in_pin} with {static_input_values}" # Should not happen because the input values are chosen such that the state is controllable.
            
        # If data is 0 and state becomes 1, then the state is inverted.
        is_state_inverted = next_state_input0 
        
        # Determine if the current output is the inverse of the data input.
        inverted_output = is_state_inverted ^ is_output_inverted
        assert inverted_output in [sympy.false, sympy.true], f"Can't determine inversion of output from the output function: {output_function}"
        # Convert to bool.
        inverted_output = bool(inverted_output)

        # Translate logic values to voltages.
        static_input_voltages = {
            pin: value * cell_conf.global_conf.supply_voltage 
            for pin, value in static_input_values.items()
        }

        logger.info(f"Use input pin {data_in_pin} with other pin values {static_input_voltages}")
     
        def delay_f(clock_transition_time, output_capacitance, data_edge_polarity: bool) -> float:
            output_load_capacitances = {data_out_pin_name: output_capacitance} 
            
            # Choose setup and hold time to be used for the delay measurement.
            settings = {
                # TODO: use measured setup/hold times
                CalcMode.BEST: (1e-9, 1e-9), # Use large setup and hold times. This leads to shorter propagation time.
                CalcMode.WORST: (1e-9, 1e-9), # Use short setup and hold times. This leads to longer propagation times.
                CalcMode.TYPICAL: (1e-9, 1e-9),
            }
            
            (setup_time, hold_time) = settings[conf.timing_corner]
            
            clock_cycle_hint = clock_pulse_width_guess * 2 # Choose a big-enough clock pulse such that data is sampled for sure.
            data_transition_time = 1e-13 # TODO
            
            delay, slew_time = seq.measure_clock_to_output_delay(
                simulation,
                cell_conf,
                data_in_pin,
                data_out_pin_name,
                clock_pin,
                clock_edge_polarity,
                data_edge_polarity,
                output_load_capacitances,
                clock_transition_time,
                data_transition_time,
                setup_time,
                hold_time,
                clock_cycle_hint,
                static_input_voltages,
                inverted_output=inverted_output,
            )
            return delay, slew_time
      
        def delay_rise_fall(clock_transition_time, output_capacitance) -> Tuple[float, float]:
            rise_delay, rise_transition = delay_f(clock_transition_time, output_capacitance, True)
            fall_delay, fall_transition = delay_f(clock_transition_time, output_capacitance, False)
            return rise_delay, rise_transition, fall_delay, fall_transition        

        f_vec = np.vectorize(delay_rise_fall, cache=True)
        xx, yy = np.meshgrid(input_transition_times, output_capacitances)
        # Evaluate timing on the grid.
        rise_delay, rise_transition, fall_delay, fall_transition = f_vec(xx, yy)

        result = {
            "cell_rise": rise_delay,
            "cell_fall": fall_delay,
            "rise_transition": rise_transition,
            "fall_transition": fall_transition,
            "total_output_net_capacitance": output_capacitances,
            "input_net_transition": input_transition_times
        }

        # Get the table indices.
        # TODO: get correct index/variable mapping from liberty file.
        index_1 = result['total_output_net_capacitance'] / conf.capacitance_unit
        index_2 = result['input_net_transition'] / conf.time_unit

        # Create template tables.
        delay_template_table = liberty_util.create_delay_template_table(new_library, len(index_1), len(index_2))
        delay_table_template_name = delay_template_table.args[0]

        # Create liberty timing tables.
        timing_tables = []
        for table_name in ['cell_rise', 'cell_fall', 'rise_transition', 'fall_transition']:
            table = Group(
                table_name,
                args=[delay_table_template_name],
            )

            table.set_array('index_1', index_1)
            table.set_array('index_2', index_2)
            table.set_array('values', result[table_name] / conf.time_unit)

            timing_tables.append(table)

        # Create the liberty timing group.
        timing_attributes = [
            Attribute('related_pin', EscapedString(related_pin)),
            Attribute('timing_sense', 'non_unate')
        ]

        timing_group = Group(
            'timing',
            attributes=timing_attributes,
            groups=timing_tables
        )

        # Attach timing group to output pin group.
        output_pin_group.groups.append(timing_group)
 
