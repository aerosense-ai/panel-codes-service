import os
from unittest import TestCase

from octue import Runner
from octue.resources import Manifest

from app import REPOSITORY_ROOT


class TestXFoil(TestCase):
    def run_xfoil_case(self, case):
        """Runs XFOIL case"""
        case_path = os.path.join(REPOSITORY_ROOT, "tests", "xfoil", "cases", case)

        runner = Runner(
            app_src=REPOSITORY_ROOT,
            twine=os.path.join(REPOSITORY_ROOT, "twine.json"),
            configuration_values=os.path.join(case_path, "configuration_values.json")
        )

        manifest = Manifest(
                datasets={
                    "aerofoil_shape_data": os.path.join(REPOSITORY_ROOT, "tests", "xfoil", "cases", "geometry_files")
                }
            ).to_primitive()

        analysis = runner.run(
            input_values=os.path.join(case_path, "input_values.json"),
            input_manifest=manifest
        )

        return analysis

    def test_naca0012(self):
        """Test that xfoil runs NACA0012 analysis and that results are consistent with compiled version from NASA
        website.
        """
        result = self.run_xfoil_case("naca0012")
        # TODO compare cl, cd, cm values to unwrapped xfoil solver
        assert all(key in result.output_values for key in ("cl", "cd", "cm"))

    def test_xfoil_run_with_json_geometry(self):
        """Test that xfoil runs NACA0018 analysis if geometry is provided as a dictionary"""
        result = self.run_xfoil_case("naca0018")

        assert all(key in result.output_values for key in ("cl", "cd", "cm"))
