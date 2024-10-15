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
        self._start_time = 0

        source_dir = os.path.join(os.path.dirname(
            __file__), "case_source")
        self._case_dir = os.path.join(os.path.dirname(
            __file__), f"case_source_{str(self._sim_id)}")
        print(f"Micro simulation {self._sim_id} case dir: {self._case_dir}")
        self._env = os.environ.copy()
        self._env["PWD"] = self._case_dir

        # copy case
        copy_case = subprocess.run(
            ['foamCloneCase', source_dir, self._case_dir], check=True, cwd=os.path.dirname(__file__), env=self._env)
        if copy_case.returncode != 0:
            raise RuntimeError(
                f"OpenFOAM case clone failed: {copy_case.stderr}")

        # mesh generation
        mesh = subprocess.run(
            ['blockMesh'], capture_output=True, cwd=self._case_dir, env=self._env)
        if mesh.returncode != 0:
            raise RuntimeError(
                f"OpenFOAM mesh generation failed: {mesh.stderr}")

    def solve(self, macro_data, dt):
        assert dt != 0
        end_time = self._start_time + dt
        print(
            f"Solving micro simulation {self._sim_id} from {self._start_time} to {end_time}")
        self._micro_vector_data = []

        inletValue = macro_data["macro-scalar-data"]
        # Set the inlet velocity from the macro data and set the start and end time
        prepareBC = subprocess.run(
            f"echo 'start' && "
            f"foamDictionary {self._start_time:g}/U -entry boundaryField.inlet.value -set 'uniform ({inletValue} 0 0)' && "
            f"foamDictionary system/controlDict -entry startTime -set {self._start_time} && "
            f"foamDictionary system/controlDict -entry endTime -set {end_time}",
            shell=True,
            check=True,
            cwd=self._case_dir,
            env=self._env
        )
        if prepareBC.returncode != 0:
            raise RuntimeError(
                f"OpenFOAM BC preparation failed: {prepareBC.stderr}")

        result = subprocess.run(
            ['simpleFoam'], capture_output=True, text=True, cwd=self._case_dir, env=self._env)

        if result.returncode != 0:
            raise RuntimeError(f"OpenFOAM solver failed: {result.stderr}")

        # Read the average velocity from the function object output
        avg_velocity_file = os.path.join(
            self._case_dir, 'postProcessing', 'fieldAverage1', '0', 'volFieldValue.dat')
        with open(avg_velocity_file, 'r') as f:
            lines = f.readlines()
            last_line = lines[-1].strip()
            avg_velocity_vector = last_line.split()[1].strip('()').split()
            avg_velocity = float(avg_velocity_vector[0])

        print(f"Micro simulation {self._sim_id} solved")
        print(f"Average velocity: {avg_velocity}")
        self._micro_scalar_data = avg_velocity
        self._micro_vector_data = [avg_velocity, 0, 0]
        self._start_time = end_time

        return {
            "micro-scalar-data": self._micro_scalar_data,
            "micro-vector-data": self._micro_vector_data,
        }

    def set_state(self, state):
        self._start_time = state[0]

    def get_state(self):
        # store the start time for this time step if iteration is required
        return [self._start_time]
