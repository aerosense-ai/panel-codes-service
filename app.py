import os
import xfoil_module

REPOSITORY_ROOT = os.path.abspath(os.path.dirname(__file__))

def run(analysis):
    """
    Runs the application
    """
    print('Hello, app is running!')
    # See what panel code will be used.
    if analysis.configuration_values['analysis_program'] == 'xfoil':
        xfoil_module.call(analysis)  # Pass the parsed input and configuration schema
    elif analysis.configuration_values['analysis_program'] == 'vgfoil':
        pass
    elif analysis.configuration_values['analysis_program'] == 'viiflow':
        pass
    elif analysis.config['analysis_program'] == 'rfoil':
        pass

    analysis.finalise(output_dir=os.path.join(REPOSITORY_ROOT, "data", "output"), save_locally=True)

