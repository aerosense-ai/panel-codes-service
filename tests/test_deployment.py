import os

from octue.cloud.pub_sub.service import Service
from octue.resources import Datafile, Dataset, Manifest
from octue.resources.service_backends import GCPPubSubBackend


def test_deployment():
    """Test that the Google Cloud Run integration works, providing a service that can be asked questions and send
    responses.
    """
    PROJECT_NAME = os.environ["TEST_PROJECT_NAME"]
    BUCKET_NAME = "panel-codes-twine-deployment-testing"
    SERVICE_ID = "octue.services.8765b5f2-1778-4a6f-809d-46b91e01bd97"

    dataset = Dataset(
        files = [
            Datafile.from_cloud(
                project_name=PROJECT_NAME,
                bucket_name=BUCKET_NAME,
                datafile_path="aerofoil_shape_data/naca_2412.dat",
                id="abff07bc-7c19-4ed5-be6d-a6546eae8f86",
                cluster=0,
                sequence=0,
                timestamp=0,
                tags={"name": "naca-2412"},
                allow_overwrite=True
            ),
            Datafile.from_cloud(
                project_name=PROJECT_NAME,
                bucket_name=BUCKET_NAME,
                datafile_path="aerofoil_shape_data/naca_0012.dat",
                id="abff07bc-7c19-4ed5-be6d-a6546eae8f87",
                cluster=0,
                sequence=1,
                timestamp=0,
                tags={"name": "naca-0012"},
                allow_overwrite=True
            )
        ]
    )

    input_manifest = Manifest(datasets=[dataset], keys={"aerofoil_shape_data": 0})

    input_values = {
        "airfoil_name": "naca-0012",
        "alpha_range": [-10, 10, 5],
        "inflow_speed": 1,
        "kinematic_viscosity": 1e-6,
        "characteristic_length": 1,
        "mach_number": 0,
        "n_critical": 9,
        "re_xtr": [5e5, 5e5]
    }

    asker = Service(backend=GCPPubSubBackend(project_name=os.environ["TEST_PROJECT_NAME"]))

    subscription, _ = asker.ask(service_id=SERVICE_ID, input_values=input_values, input_manifest=input_manifest)
    answer = asker.wait_for_answer(subscription, timeout=1000)
    assert all(key in answer["output_values"] for key in ("cl", "cd", "cm"))


if __name__ == "__main__":
    test_deployment()
