# multiscale-openfoam
Implicit two-scale coupling with OpenFOAM as micro-scale solver.

The macro-scale generates random scalars and the pitz daily case in micro-scale use this scalars as the initial velocity in x direction. Same time length is used for both scales. Since it'S random data, so convergence is not expected.

### Software requirements
- OpenFOAM (v2312 tested)
- preCICE (>v3.0.0)
- Micro Manager (> v0.5.0)
- Python (v3.10 tested)

### Run the code
In the root folder:
1. Open a terminal and run the following command to start the OpenFOAM solver in micro-scale:
```bash
 bash clean.sh && micro-manager-precice micro-manager-config.json
```
The clean script is mainly to remove the existing openFoam case folder of every micro simulation, otherwise `foamCloneCase` complains.

2. Open another terminal and run the following command to start the macro-scale solver:
```bash
py3 macro_dummy.py
```
