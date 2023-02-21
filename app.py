import os
import logging
import xfoil_module

REPOSITORY_ROOT = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)

def run(analysis):
    """
    Runs the application
    """
    logger.info('Panel Codes App is running!')
    # See what panel code will be used.
    if analysis.configuration_values['analysis_program'] == 'xfoil':
        xfoil_module.call(analysis)  # Pass the parsed input and configuration schema
    elif analysis.configuration_values['analysis_program'] == 'vgfoil':
        logger.info("Vortex Generator XFOIL is not implemented yet!")
    elif analysis.configuration_values['analysis_program'] == 'viiflow':
        logger.info("VIIFLOW is not implemented!")
    elif analysis.config['analysis_program'] == 'rfoil':
        logger.info("RFOIL by DTU is not implemented!")

    analysis.finalise()

