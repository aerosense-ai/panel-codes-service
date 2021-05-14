import os.path

import numpy as np
from xfoil import XFoil
# from vgfoil import VGFoil



# TODO properly code initialization of VGFoil or XFoil instance and property setters
xf = XFoil()  # create xfoil object
xf.print = 1  # Suppress terminal output: 0, enable output: 1
#xf.ctauvg = (0, 0, 0.25, 2.5)
#xf.xvg = (1, 0.8)
#xf.hvg = (0, 0.002)
#xf.xtr = (0.05, 0.1)


def call(analysis):
    '''Runs analysis using Xfoil'''
    print("Lets run Xfoil!")
    # load airfoil shapefiles dataset
    input_dataset = analysis.input_manifest.get_dataset("aerofoil_shape_data")

    #TODO [?] Should airfoil section and repanel settings be in config rather then input?
    airfoil_file = input_dataset.get_file_by_tag("name:"+analysis.input_values["airfoil_name"])
    xf.airfoil = load_airfoil(airfoil_file)
    # It is possible to repanel
    if analysis.input_values['repanel']:
        xf.repanel(n_nodes=analysis.input_values['repanel_configuration']['nodes'])

    # Reynolds number,
    xf.Re = set_input(analysis.input_values)[0]

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

    # Setting Mach number before assigning airfoil throws in the error.
    # BUG in xfoil-python 1.1.1 !! Changing Mach number has no effect on results!
    # There seems to be confusion between MINf and MINf1, adding a line MINf1 = M
    # after line 204 of the api.f90, seems to solve the issue.
    xf.M = analysis.input_values['mach_number']

    # Set the max number of iterations
    xf.max_iter = analysis.configuration_values['max_iterations']

    # Feed the AoA range to Xfoil and perfom the analysis
    # TODO aseq cannot be used as get_cp_distribution returns only last converged result
    #  [?] Use xf.a with a for loop?
    aoa_range=np.linspace(analysis.input_values['alpha_range'][0],
                          analysis.input_values['alpha_range'][1],
                          analysis.input_values['alpha_range'][2])
    cp_dump = []
    results = []

    for aoa in aoa_range:
        # The result contains following vectors Cl, Cd, Cm, Cp_min
        result = xf.a(aoa)
        # USE forked version of xfoil, so that get_cp_distribution also outputs y-coordinate!
        cp = np.array([aoa*np.ones(len(xf.get_cp_distribution()[0])),
                    xf.get_cp_distribution()[0],
                    xf.get_cp_distribution()[1],
                    xf.get_cp_distribution()[2]])
        cp_dump.append(cp.T)
        results.append(result)

    # TODO should aoa be duplicated?
    # analysis.output_values['aoa'] =

    # Cast to np array for easier handling
    results=np.array(results)
    analysis.output_values['cl'] = results[:, 0]
    analysis.output_values['cd'] = results[:, 1]
    analysis.output_values['cm'] = results[:, 2]
    analysis.output_values['cp_min'] = results[:, 3]

    # TODO hangle this properly. Dumping cp to csv file for now
    # np.savetxt("cp_dump.csv", np.concatenate(cp_dump), delimiter=",")
    # analysis.output_values['cp'] or should we make a manifested file?

def set_input(_in):
    # Calculate Reynolds from input values
    reynolds = _in['inflow_speed'] * _in['characteristic_length'] / _in['kinematic_viscosity']
    # Calculate x-transition from Critical Reynolds
    x_transition = tuple(_xtr / reynolds for _xtr in _in['re_xtr'])
    return reynolds, x_transition


def load_airfoil(airfoil_file):
    """
    Loads airfoil geometry data from .dat file
    """
    print(airfoil_file.get_local_path())
    with open(airfoil_file.get_local_path()) as f:
        content = f.readlines()

    x_coord = []
    y_coord = []

    for line in content[1:]:
        x_coord.append(float(line.split()[0]))
        y_coord.append(float(line.split()[1]))

    airfoilObj = xf.airfoil
    airfoilObj.x = np.array(x_coord)
    airfoilObj.y = np.array(y_coord)

    return airfoilObj
