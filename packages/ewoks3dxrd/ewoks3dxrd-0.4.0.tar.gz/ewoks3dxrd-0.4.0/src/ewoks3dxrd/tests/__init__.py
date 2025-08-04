import os

# Because of OpenMP and Multiprocessing mix, we are suppressing OpenMP usage in the C code of cImageD11
# See https://github.com/FABLE-3DXRD/ImageD11/issues/486 and https://gitlab.esrf.fr/workflow/ewoksapps/ewoks3dxrd/-/issues/19
os.environ["OMP_NUM_THREADS"] = "1"
