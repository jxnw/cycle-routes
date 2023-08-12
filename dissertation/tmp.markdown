# Cycle routes: connecting the network {.unlisted .unnumbered}
Dissertation project for MSc Computer Science at the University of St Andrews

## Installation {.unlisted .unnumbered}
Run the `install.sh` script to create a Python virtual environment for this project.

## Usage {.unlisted .unnumbered}
To run the program, first activate the virtual environment:

    source env/bin/activate

To run the program with the default configuration in `configuration.json`:

    python main.py

Alternatively, the configuration file can be passed as an argument:

    python main.py --config path_to_config_file

To specify the directory to save the generated plot:

    python main.py --save path_to_plots

## Testing {.unlisted .unnumbered}
To run all unit tests:

    python -m unittest -v

To run all unit tests with code coverage:

    coverage run -m unittest

To view the coverage report:

    coverage report -m

