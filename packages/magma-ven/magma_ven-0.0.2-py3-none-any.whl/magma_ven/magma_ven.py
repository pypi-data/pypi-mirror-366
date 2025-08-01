import os

from magma_ven.utils import check_directory


class MagmaVen:
    """MAGMA Volcanic Eruption Notice (VEN) base class.

    Attributes:
        volcano_code (str): MAGMA Indonesia volcano code. 3 characters.
        start_date (str): Start date of VEN.
        end_date (str): End date of VEN.
        current_dir (str): Current directory. Defaults to current directory.
        verbose (bool): Verbose mode. Defaults to False.
        debug (bool): Debug mode. Defaults to False.
    """

    def __init__(
        self,
        volcano_code: str,
        start_date: str,
        end_date: str,
        current_dir: str = None,
        verbose: bool = False,
        debug: bool = False,
    ):
        """Init MAGMA Volcanic Eruption Notice (VEN) base class.

        Args:
            volcano_code (str): MAGMA volcano code.
            start_date (str): Start date of VEN.
            end_date (str): End date of VEN.
            current_dir (str): Current directory. Defaults to current directory.
            verbose (bool): Verbose mode. Defaults to False.
            debug (bool): Debug mode. Defaults to False.
        """
        self.volcano_code = volcano_code.upper()
        self.start_date = start_date
        self.end_date = end_date
        self.verbose = verbose
        self.debug = debug

        if current_dir is None:
            current_dir = os.getcwd()
        self.current_dir = current_dir or os.getcwd()
        self.output_dir, self.figures_dir, self.magma_dir = check_directory(current_dir)
        self.ven_dir = os.path.join(self.magma_dir, "ven")
        self.filename = f"{self.volcano_code}_{self.start_date}_{self.end_date}"
