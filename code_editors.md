# Code Editors

- [Code Editors](#code-editors)
  - [Visual Studio Code](#visual-studio-code)
    - [Hail](#hail)

## Visual Studio Code

### Hail

After installing the Python extension, Visual Studio Code by default uses
Pylance for code navigation. As Hail requires a non-trivial `PYTHONPATH` to
resolve all modules, this is a little tricky to set up.

Add a `.env` file to the main Hail directory, which can be used to set up
environment variables. Unfortunately, environment variable substitutions like
`$HOME` don't work in this file, so you'll have to use absolute paths. Add the
following line, adjusted accordingly for your system and user name:

    PYTHONPATH="/Users/leo/hail:/Users/leo/hail/hail/python:/Users/leo/hail/gear:/Users/leo/hail/web_common"

At the time of writing, the Pylance build just got a
[fix](https://github.com/microsoft/pylance-release/issues/275) to respect the
`$PYTHONPATH` variable. However, it requires a new version of the Python (not
Pylance!) extension. You can
[switch](https://devblogs.microsoft.com/python/python-in-visual-studio-code-august-2019-release/)
to that using the "Python: Insiders Channel" command.

Finally, you'll have to set up a Python environment. Open a terminal in Visual
Studio Code and run the following to install the required dependencies:

    ```bash
    conda create --name hail-dev python=3.7.7
    conda activate hail-dev
    pip3 install -r hail/python/requirements.txt
    pip3 install -r docker/requirements.txt
    ```

Switch Visual Studio Code to this conda environment using the "Python: Select
Interpreter" command. You might also want to disable the
[inheritEnv setting](https://github.com/microsoft/vscode-python/issues/7607)
when using conda.

If symbols still don't get resolved properly, you might have to reload Visual
Studio Code.
