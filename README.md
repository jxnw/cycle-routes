# Cycle routes: connecting the network
Dissertation project for M.Sc. Computer Science at the University of St Andrews

## Installation
Run the `install.sh` script to create a Python virtual environment for this project.

## Usage
To run the program, first activate the virtual environment:
```commandline
source env/bin/activate
```

To run the program with the default configuration in `configuration.json`:
```commandline
python main.py
```

Alternatively, the configuration file can be passed as an argument:
```commandline
python main.py --config path_to_config_file
```

To specify the directory to save the generated plot:
```commandline
python main.py --save path_to_plots
```

## Testing
To run all unit tests:
```commandline
python -m unittest -v
```

To run all unit tests with code coverage:
```commandline
coverage run -m unittest
```

To view the coverage report:
```commandline
coverage report -m
```