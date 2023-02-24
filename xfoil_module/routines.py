import os.path
import logging
import numpy as np
from xfoil import XFoil

logger = logging.getLogger(__name__)


def call(analysis):
    '''Runs analysis using Xfoil'''
    # TODO properly code initialization of XFoil Class instance and property setters
    xf = XFoil()
    xf.print = int(not analysis.configuration_values["silent_mode"])  # Suppress terminal output: 0, enable output: 1
    xf.airfoil = load_airfoil(xf, analysis)

    # TODO [?] Should airfoil section and repanel settings be in config rather then input?
    # It is possible to re-panel
    if analysis.input_values["airfoil_geometry"]['repanel']:
        xf.repanel(n_nodes=analysis.input_values["airfoil_geometry"]['repanel_configuration']['nodes'])

    # Reynolds number,
    xf.Re = set_input(analysis.input_values)[0]

    # Setting Mach number before assigning airfoil throws in the error.
    xf.M = analysis.input_values['mach_number']

    # TODO Research for Critical Reynolds Number dependency from leading edge erosion, and force xtr or modify Ncrit.
    #      Default xtr is (1,1), Default n_ctit is 9.

    # Force transition location
    # Set xtr value: a forced location of BL transition. Default xtr is (1,1): no forced transition
    # (xtr top, xtr bot), should be a tuple
    # xf.xtr = set_input(twine_input_values)[1]

    # n_crit from eN method.
    # References:
    # [1] J.L. van Ingen, The eN method for transition prediction. Historical review of work at TU Delft
    # [2] L. M. Mack, Transition and Laminar Instability
    # Default value is 9 which predicts a transition for a flat plate at 7% TI level
    # N =  -8.43 - 2.4*ln(0.01*TI) according to Mack
    # Beginning and end of transition for TI>0.1%
    # N_1 = 2.13 - 6.18 log10(TI)
    # N_2 = 5    - 6.18 log10(TI)
    xf.n_crit = analysis.input_values['n_critical']

    # Set the max number of iterations
    xf.max_iter = analysis.configuration_values['max_iterations']

    # Feed the AoA range to Xfoil and perform the analysis
    # TODO
    #  [?] Use "xf.a" with a for loop OR we should care only about the last result in seq???
    #  Note: IF "xf.aseq" is used get_cp_distribution returns only last converged result
    logger.info("Xfoil solver started.")
    aoa_range=np.linspace(analysis.input_values['alpha_range'][0],
                          analysis.input_values['alpha_range'][1],
                          analysis.input_values['alpha_range'][2])

    results = []
    cp_results = []

    for aoa in aoa_range:
        # The result contains following tuples (Cl, Cd, Cm, Cp_min)
        results.append(xf.a(aoa))
        # TODO x-coord and y-coord remain same between iterations... But I guess we can duplicate them for now
        cp_results.append({
            'x-coord': xf.get_cp_distribution()[0],
            'y-coord': xf.get_cp_distribution()[1],
            'cp': xf.get_cp_distribution()[2],
        })

    # TODO should aoa be duplicated?
    analysis.output_values['aoa'] = aoa_range
    # Cast to np array for easier handling
    results = np.array(results)
    analysis.output_values['cl'] = results[:, 0]
    analysis.output_values['cd'] = results[:, 1]
    analysis.output_values['cm'] = results[:, 2]
    analysis.output_values['cp_min'] = results[:, 3]
    # TODO should we make a manifested file?
    # np.savetxt("cp_dump.csv", np.concatenate(cp_dump), delimiter=",")
    analysis.output_values['cp'] = cp_results


def set_input(_in):
    # Calculate Reynolds from input values
    reynolds = _in['inflow_speed'] * _in['characteristic_length'] / _in['kinematic_viscosity']
    # Calculate x-transition from Critical Reynolds
    # x_transition = tuple(_xtr / reynolds for _xtr in _in['re_xtr'])
    x_transition = _in['characteristic_length']
    return reynolds, x_transition


def load_airfoil(xf, analysis):
    """
    Loads airfoil geometry data from .dat file or from dictionary specified in the input
    """
    if "airfoil_geometry_filename" in analysis.input_values["airfoil_geometry"].keys():
        # load airfoil shapefiles dataset
        input_dataset = analysis.input_manifest.get_dataset("aerofoil_shape_data")
        airfoil_file_path = input_dataset.files.filter(
            name=analysis.input_values["airfoil_geometry"]["airfoil_geometry_filename"]
        ).one().local_path

        with open(airfoil_file_path) as f:
            content = f.readlines()

        x_coord = []
        y_coord = []

        for line in content[1:]:
            x_coord.append(float(line.split()[0]))
            y_coord.append(float(line.split()[1]))
    else:
        x_coord = analysis.input_values["airfoil_geometry"]["xy_coordinates"]["x_coordinates"]
        y_coord = analysis.input_values["airfoil_geometry"]["xy_coordinates"]["y_coordinates"]

    airfoilObj = xf.airfoil
    airfoilObj.x = np.array(x_coord)
    airfoilObj.y = np.array(y_coord)
    logger.info("Loaded airfoil geometry.")
    return airfoilObj
