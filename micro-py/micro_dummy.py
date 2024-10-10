"""
Micro simulation
In this script we solve a dummy micro problem to just show the working of the macro-micro coupling
"""
import subprocess
import os


class MicroSimulation:
    def __init__(self, sim_id):
        """
        Constructor of MicroSimulation class.
        """
        self._sim_id = sim_id
        self._dims = 3
        self._micro_scalar_data = None
        self._micro_vector_data = None

    def solve(self, macro_data, dt):
        assert dt != 0
        self._micro_vector_data = []

        case_dir = os.path.join(os.path.dirname(__file__), "case_source")
        env = os.environ.copy()
        env["PWD"] = case_dir

        inletValue = macro_data["macro-scalar-data"]
        prepareBC = subprocess.run(['foamDictionary', '0/U', '-entry', 'boundaryField.inlet.value',
                                    '-set', f'uniform ({inletValue} 0 0)'], check=True, cwd=case_dir, env=env)
        if prepareBC.returncode != 0:
            raise RuntimeError(
                f"OpenFOAM BC preparation failed: {prepareBC.stderr}")

        # Call OpenFOAM solver
        mesh = subprocess.run(
            ['blockMesh'], capture_output=True, cwd=case_dir, env=env)
        result = subprocess.run(
            ['simpleFoam'], capture_output=True, text=True, cwd=case_dir, env=env)

        if mesh.returncode != 0:
            raise RuntimeError(
                f"OpenFOAM mesh generation failed: {mesh.stderr}")
        if result.returncode != 0:
            raise RuntimeError(f"OpenFOAM solver failed: {result.stderr}")

        # Read the average velocity from the function object output
        avg_velocity_file = os.path.join(
            case_dir, 'postProcessing', 'fieldAverage1', '0', 'volFieldValue_0.dat')
        with open(avg_velocity_file, 'r') as f:
            lines = f.readlines()
            last_line = lines[-1].strip()
            avg_velocity_vector = last_line.split()[1].strip('()').split()
            avg_velocity = float(avg_velocity_vector[0])

        print(f"Micro simulation {self._sim_id} solved")
        print(f"Average velocity: {avg_velocity}")
        self._micro_scalar_data = avg_velocity
        self._micro_vector_data = [avg_velocity, 0, 0]

        return {
            "micro-scalar-data": self._micro_scalar_data,
            "micro-vector-data": self._micro_vector_data,
        }

    def set_state(self, state):
        None

    def get_state(self):
        None
