from distutils.core import setup
import itertools as it
import os

from py2exe.build_exe import py2exe as build_exe
import jsonschema
import notebook
import nbformat
import path_helpers as ph
import matplotlib
import zmq


class JsonSchemaCollector(build_exe):
    """
    This class Adds jsonschema files draft3.json and draft4.json to
    the list of compiled files so it will be included in the zipfile.
    """
    def copy_extensions(self, extensions):
        build_exe.copy_extensions(self, extensions)
        collect_dir = ph.path(self.collect_dir)

        for path_i, module_i in ((ph.path(notebook.__path__[0]),
                                  ('templates', )),
                                 (ph.path(jsonschema.__path__[0]),
                                  ('schemas', )),
                                 (ph.path(nbformat.__path__[0]),
                                  ('v4', )),
                                 ):
            data_path = path_i.joinpath(*module_i)

            # Copy the template files to the collection dir. Also add the copied
            # file to the list of compiled files so it will be included in the
            # zipfile.
            # self.collect_dir.joinpath(rel_path_i).makedirs_p()

            for file_j in data_path.walkfiles():
                if file_j.ext.startswith('.py'):
                    continue
                rel_path_j = path_i.parent.relpathto(file_j)
                collected_j = collect_dir.joinpath(rel_path_j)
                collected_j.parent.makedirs_p()
                self.copy_file(file_j, collected_j)
                self.compiled_files.append(rel_path_j)


# libzmq.dll is in same directory as zmq's __init__.py

os.environ["PATH"] = \
    os.environ["PATH"] + \
    os.path.pathsep + os.path.split(zmq.__file__)[0]


def data_files():
    '''
    Collect data files for packages that are not supported out of the box.
    '''
    # Seems like `libzmq.pyd` needs to be copied to `dist` directory, *even
    # though* it is already automatically copied by `py2exe` to the name
    # `zmq.libzmq.pyd`.
    data_files_ = [('', [ph.path(zmq.__path__[0]).joinpath('libzmq.pyd')])]

    # Jupyter notebook templates and static files cannot be accessed within the
    # zip file, so need to be copied.
    # The `nbformat` package contains a `jsonschema` file which cannot be
    # accessed within the zip file, so it also needs to be copied.
    for path_i, module_i in ((ph.path(notebook.__path__[0]), ('templates', )),
                             (ph.path(notebook.__path__[0]), ('static', )),
                             (ph.path(nbformat.__path__[0]), tuple())):
        data_path = path_i.joinpath(*module_i)

        # Copy the template files to the collection dir. Also add the copied
        # file to the list of compiled files so it will be included in the
        # zipfile.
        files = sorted([file_j for file_j in data_path.walkfiles()])
        for parent_i, files_i in it.groupby(files, lambda x: x.parent):
            data_files_ += [(path_i.parent.relpathto(parent_i),
                             list(files_i))]
    return data_files_


setup(console=['jupyter-notebook.py', 'ipython.py'],
      cmdclass={"py2exe": JsonSchemaCollector},
      # See http://www.py2exe.org/index.cgi/ListOfOptions
      options={'py2exe': {'excludes': ['jinja2.asyncsupport'],
                          'includes': ['matplotlib', 'numpy', 'pandas',
                                       'cycler', 'IPython',
                                       'zmq',
                                       'zmq.utils',
                                       'zmq.utils.jsonapi',
                                       'zmq.utils.strtypes']}},
      # See http://www.py2exe.org/index.cgi/MatPlotLib
      data_files=matplotlib.get_py2exe_datafiles() +
      data_files())
