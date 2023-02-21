from unittest import TestCase

from octue.resources import Manifest, Child
from octue.log_handlers import apply_log_handler


apply_log_handler()


class TestDeployment(TestCase):
    def test_deployment(self):
        """Test that the Google Cloud Run integration works, providing a service that can be asked questions and send
        responses.
        """
        input_manifest = Manifest(
            datasets={"aerofoil_shape_data": "gs://panel-codes-twine-deployment-testing/aerofoil_shape_data"}
        )

        input_values = {
            "airfoil_label": "naca-0012",
            "alpha_range": [-10, 10, 3],
            "repanel": False,
            "inflow_speed": 1,
            "kinematic_viscosity": 1e-6,
            "characteristic_length": 1,
            "mach_number": 0,
            "n_critical": 9,
            "re_xtr": [5e5, 5e5]
        }

        child = Child(
            id="aerosense/panel-codes:0.0.1",
            backend={"name": "GCPPubSubBackend", "project_name": "aerosense-twined"},
        )

        answer = child.ask(input_values=input_values, input_manifest=input_manifest, timeout=1000)
        assert all(key in answer["output_values"] for key in ("cl", "cd", "cm"))
