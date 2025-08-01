import os
import subprocess
from collections import namedtuple

FLAG_MAP = {
    'f': '-f',
    'v': '-v',
    'o': '-o',
    'e': '-e',
    'c': '-c',
    'hf': '-hf',
    'wh': '-wh',
    'ref': '-ref',
    'target': '-target',
    'atom_index': '--atom_index',
    'res_name': '--res_name',
    'res_chain': '--res_chain',
    'res_number': '--res_number',
    'force_gpa': '--force_gpa',
    'force_pcg': '--force_pcg',
    'gen3D': '--gen3D',
}

ProcessLigandResult = namedtuple('ProcessResult', ['stdout', 'stderr', 'returncode'])

class ProcessLigandError(Exception):
    """Custom exception for errors related to the ProcessLigand."""
    pass


def run_processligand(file_path, **kwargs):
    """
    A wrapper to run the processligand utility with specified options.

    Args:
        file_path (str, required): Absolute path to the ligand/target file.
        **kwargs: Arbitrary keyword arguments that correspond to the command-line
                  options of the ligand processing utility. See readme for a description of each keyword argument.
    Raises:
        FileNotFoundError: If the required input file 'f' does not exist.
        ProcessLigandError: If the external process fails to execute.
    Returns:
        ProcessLigandResult: A namedtuple containing stdout, stderr, and the returncode.
    """
    default_options = {

        # Arguments with values
        'v': None,            # -v <INT>: Verbose level
        'o': None,            # -o <STR>: Output base filename
        'e': None,            # -e <STR>: Residue to extract
        'c': None,            # -c <STR>: Convert molecule to specified format
        'atom_index': None,   # --atom_index <INT>: Starting atom index
        'res_name': None,     # --res_name <STR>: 3-char ligand code
        'res_chain': None,    # --res_chain <CHAR>: Ligand chain
        'res_number': None,   # --res_number <INT>: Ligand number
        'force_gpa': None,    # --force_gpa <INT>: Force reference atom
        'force_pcg': None,    # --force_pcg <FLOAT FLOAT FLOAT>: Force protein center of geometry

        # Boolean flags
        'hf': False,          # -hf: Include hydrogen flexible bonds
        'wh': False,          # -wh: Add hydrogen atoms in output
        'ref': False,         # -ref: Output final PDB from IC
        'target': False,      # -target: Parse a target
        'gen3D': False,       # --gen3D: Generate 3D conformation
    }

    config = default_options.copy()
    config.update(kwargs)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    executable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'ProcessLigand')
    command = [executable_path, FLAG_MAP['f'], file_path]

    for key, value in config.items():
        if value:
            arg_flag = FLAG_MAP.get(key)
            if arg_flag:
                command.append(arg_flag)
                if not isinstance(value, bool):
                    command.append(str(value))

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        return ProcessLigandResult(result.stdout, result.stderr, result.returncode)

    except FileNotFoundError:
        raise ProcessLigandError(f"Executable not found at '{executable_path}'.")

    except subprocess.CalledProcessError as e:
        error_message = (
            f"ProcessLigand failed with exit code {e.returncode}.\n"
            f"Stderr:\n{e.stderr.strip()}"
        )
        raise ProcessLigandError(error_message) from e
