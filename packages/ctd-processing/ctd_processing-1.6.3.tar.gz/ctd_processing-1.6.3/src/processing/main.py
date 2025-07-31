import logging
import sys
from pathlib import Path

import typer
from seabirdfilehandler import CnvFile, HexCollection

from processing.procedure import Procedure
from processing.settings import Configuration
from processing.utils import default_seabird_exe_path

# Configure the root logger with a file handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("processing.log"),
    ],
)

logger = logging.getLogger(__name__)


app = typer.Typer()


@app.command()
def run(
    processing_target: str = "",
    path_to_configuration: str = "processing_config.toml",
    procedure_fingerprint_directory: str = "",
    file_type_dir: str = "",
    verbose: bool = False,
):
    """
    Processes one target file using the given procedure workflow file.

    Parameters
    ----------
    processing_target: str :
        The target file to process.
         (Default value = "")

    path_to_configuration: Path | str :
        The path to the configuration file.
         (Default value = Path("processing_config.toml"))

    procedure_fingerprint_directory: str | None :
        The path to a fingerprint directory. If none given, no fingerprints
        will be created.
         (Default value = None)

    file_type_dir: str | None :
        The path to a file type directory. If none given, the files will not be
        separated into file type directories.
         (Default value = None)

    verbose: bool :
        An option to allow more verbose output.
         (Default value = False)

    Returns
    -------

    """
    path_to_config = Path(path_to_configuration)
    if path_to_config.exists():
        config = Configuration(path_to_config)
    else:
        sys.exit("Could not find the configuration file.")
    config["input"] = processing_target
    Procedure(
        configuration=config,
        procedure_fingerprint_directory=procedure_fingerprint_directory,
        file_type_dir=file_type_dir,
        verbose=verbose,
    )


@app.command()
def convert(
    input_dir: str,
    psa_path: str,
    output_dir: str = "",
    xmlcon_dir: str = "",
    pattern: str = "",
) -> list[Path]:
    """
    Converts a list of Sea-Bird raw data files (.hex) to .cnv files.

    Does either use an explicit list of paths or searches for all .hex files in
    the given directory.

    Parameters
    ----------
    input_dir: Path | str :
        The data directory with the target .hex files.
    psa_path: Path | str :
        The path to the .psa for datcnv.
    output_dir: Path | str :
        The directory to store the converted .cnv files in. (Default is the input directory)
    xmlcon_dir: Path | str :
        The directory to look for .xmlcon files. (Default is the input directory)
    pattern: str :
        A name pattern to filter the target .hex files with. (Default is none)

    Returns
    -------
    A list of paths or CnvFiles of the converted files.

    """
    if not output_dir:
        output_dir = input_dir
    if not xmlcon_dir:
        xmlcon_dir = input_dir
    hexes = HexCollection(
        path_to_files=input_dir,
        pattern=pattern,
        file_suffix="hex",
        path_to_xmlcons=xmlcon_dir,
    )
    resulting_cnvs = []
    proc_config = {
        "output_dir": output_dir,
        "modules": {
            "datcnv": {"psa": psa_path},
        },
    }
    procedure = Procedure(
        proc_config,
        auto_run=False,
    )
    for hex in hexes:
        try:
            result = procedure.run(hex.path_to_file)
        except Exception as e:
            logger.error(f"Failed to convert: {hex.path_to_file}, {e}")
        else:
            resulting_cnvs.append(result)
    return resulting_cnvs


@app.command()
def batch(
    input_dir: str,
    config: str,
    pattern: str = ".cnv",
) -> list[Path] | list[CnvFile]:
    """
    Applies a processing config to multiple .hex or. cnv files.

    Parameters
    ----------
    input_dir: Path | str :
        The data directory with the target files.
    config: dict | Path | str:
        Either an explicit config as dict or a path to a .toml config file.
    pattern: str :
        A name pattern to filter the target files with. (Default is ".cnv")

    Returns
    -------
    A list of paths or CnvFiles of the processed files.

    """
    resulting_cnvs = []
    if isinstance(config, dict):
        proc_config = config
    else:
        proc_config = Configuration(config)
    procedure = Procedure(proc_config, auto_run=False)
    for file in Path(input_dir).rglob(f"*{pattern}*"):
        try:
            result = procedure.run(file)
        except Exception as e:
            logger.error(f"Error when processing {file}: {e}")
        else:
            resulting_cnvs.append(result)
    return resulting_cnvs


try:
    from processing.gui.procedure_config_view import run_gui
except ImportError:
    pass
else:

    @app.command()
    def edit(file: str):
        """
        Opens a procedure workflow file in GUI for editing.
        """
        run_gui(file)


@app.command()
def show(file: typer.FileText):
    """
    Display the contents of a procedure workflow file.
    """
    content = file.read()
    print(content, end="")


@app.command()
def check():
    """
    Assures that all requirements to use this tool are met.
    """
    if not default_seabird_exe_path().exists():
        print(
            "You are missing a Sea-Bird Processing installation or are not using the default path. Please ensure that a valid installation can be found in Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/"
        )
    print("All set, you are ready to go.")


if __name__ == "__main__":
    app()
