# Build

To build, run the following commands:

```sh
# Create Conda environment containing required packages.
conda env create -n py2exe-test --file .\conda-env.yaml
activate py2exe-test
# Need to uninstall Conda version of `cycler`, since it is in an `egg` archive,
# which is incompatible with `py2exe`.
conda uninstall --force cycler -y
pip install cycler
# Build `jupyter-notebook.exe` and `ipython.exe` executables.
python .\setup.py py2exe
```
