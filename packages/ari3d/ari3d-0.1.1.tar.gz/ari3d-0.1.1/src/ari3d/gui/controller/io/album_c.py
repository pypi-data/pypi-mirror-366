"""Controller for managing solutions for the ari3d application using Album API."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Set
import traceback

from PyQt6.QtWidgets import QMessageBox, QWidget
from album.runner.album_logging import get_active_logger

from ari3d.gui.ari3d_logging import Ari3dLogger
from ari3d.resources.default_values import DefaultValues

cur_file_path = Path(__file__).parent

SOLUTION_IDS = [
    "de.mdc:data_viewer",
    "de.mdc:particleSeg3D-predict",
    "de.mdc:property_extraction",
]

ARI3D_BASE_PATH = Path.home().joinpath(".ari3d")
ALBUM_BASE_PATH = ARI3D_BASE_PATH.joinpath("collection")


class AlbumController:
    """Controller class for managing solutions in the ari3d application using Album API."""

    def __init__(self, parent: QWidget, interactive: bool = True):
        """Initialize the AlbumController with the album API and logger."""
        self.parent = parent
        self._setup_album()
        self.logger = Ari3dLogger()
        self._add_logging_to_file()
        self.interactive = interactive

    def _setup_album(self):
        from album.api import Album
        ALBUM_BASE_PATH.mkdir(parents=True, exist_ok=True)

        self.album_api = Album.Builder().base_cache_path(ALBUM_BASE_PATH).build()
        self.album_log = logging.getLogger("album")
        self.album_api.load_or_create_collection()

    def _add_logging_to_file(self):
        # get the FileHandler in ari3d_logger
        for handler in self.logger.log.handlers:
            if isinstance(handler, logging.FileHandler):
                # add album logging to the same file
                self.album_log.addHandler(handler)
                self.album_log.setLevel(self.logger.log.level)

    def check_steps(self) -> Set[str]:
        """Check for updates of the solutions in the album catalog."""
        updates = self.album_api.upgrade(dry_run=True)

        self.logger.log.debug("All updates:" + str(updates))

        ari3d_updates = updates["ari3d"]
        ari3d_update_lit = ari3d_updates._solution_changes
        coordinate_set = {
            ":".join([x.coordinates().group(), x.coordinates().name()])
            for x in ari3d_update_lit
        }
        text = (
            "No updates available!"
            if ari3d_update_lit == []
            else (
                "Updates available for:"
                + ", ".join(coordinate_set)
                + ". Run update new steps to install them."
            )
        )

        self.logger.log.info(text)

        return coordinate_set

    def update_steps(self):
        """Update the solutions in the album."""
        coordinate_set = self.check_steps()
        self.album_api.upgrade()
        for solution in coordinate_set:
            self.reinstall_solution(solution)

    def reinstall_solution(self, solution: str):
        """Reinstall a specific solution in the album."""
        self.uninstall_solution(solution)
        self.install_solution(solution)

    def reinstall_steps(self):
        """Reinstall all solutions in the album."""
        self.uninstall_required()
        self.try_install_required()

    def install_solution(self, solution: str) -> bool:
        """Install a specific album solution."""
        # add catalog
        try:
            self.album_api.get_catalog_by_src(str(DefaultValues.repo_link.value))
        except LookupError:
            self.album_api.add_catalog(str(DefaultValues.repo_link.value))

        # install from catalog
        try:
            level = get_active_logger().level
            get_active_logger().setLevel("ERROR")
            if not self.album_api.is_installed(solution):
                get_active_logger().setLevel(level)
                self.logger.log.info(f"Installing {solution}")
                self.album_api.install(solution)
            self.logger.log.info(f"{solution} is ready to run!")
            get_active_logger().setLevel(level)
        except LookupError:
            self.logger.log.info(
                f"Solution {solution} not found in the catalog. Unable to run this step!"
            )
            return False
        except RuntimeError as e:
            self.logger.log.error(
                f"Failed to install {solution}: {e}. Look into logfile {str(self.logger.log_file_path)} for details."
            )
            return False

        return True

    def uninstall_solution(self, solution: str):
        """Uninstall a specific album solution."""
        # add catalog
        try:
            self.album_api.get_catalog_by_src(str(DefaultValues.repo_link.value))
        except LookupError:
            self.album_api.add_catalog(str(DefaultValues.repo_link.value))

        # install from catalog
        try:
            level = get_active_logger().level
            get_active_logger().setLevel("ERROR")
            if self.album_api.is_installed(solution):
                get_active_logger().setLevel(level)
                self.logger.log.info(f"Uninstalling {solution}")
                self.album_api.uninstall(solution)
            self.logger.log.info(f"{solution} is uninstalled!")
            get_active_logger().setLevel(level)
        except LookupError:
            self.logger.log.info(
                f"Solution {solution} not found in the catalog. Unable to uninstall this step!"
            )

    def install_from_disk(self, solution: str):
        """Install a specific solution from disk."""
        name = solution.split(":")[1]
        try:
            if not self.album_api.is_installed(solution):
                self.logger.log.info(f"Installing {solution}")
                self.album_api.install(
                    str(cur_file_path.joinpath("..", "..", "..", "solutions", name))
                )
            self.logger.log.info(f"{solution} is ready to run")
        except LookupError:
            self.album_api.install(
                str(cur_file_path.joinpath("..", "..", "..", "solutions", name))
            )

    def run(self, solution, argv=None):
        """Run a specific solution in the album."""
        self.album_api.run(solution, argv=argv)

    def install_required(self):
        """Install all required solutions for the interactive workflow."""
        # loop to install all solutions necessary for this interactive workflow
        for solution_id in SOLUTION_IDS:
            success = self.install_solution(solution_id)
            if not success:
                self.logger.log.error(
                    f"Solution {solution_id} could not be installed. Please check the logs for details."
                )
                raise RuntimeError("Installation failed for one or more solutions.")

    def try_install_required(self):
        """Try to install all required solutions for the interactive workflow."""
        # loop to install all solutions necessary for this interactive workflow
        for solution_id in SOLUTION_IDS:
            try:
                solution_install_file = ARI3D_BASE_PATH.joinpath(solution_id.replace(":", "_"))

                # check if installation failed before
                if solution_install_file.exists() and self.interactive:
                    # pop up a message box to the user asking whether to reinstall the solution
                    reply = QMessageBox.question(
                        self.parent,
                        "Re-trigger installation",
                        "Installation of %s failed before. Do you want to try to install it again?" % solution_id,
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if reply == QMessageBox.StandardButton.No:
                        self.logger.log.info(
                            f"Skipping installation of {solution_id} as per user request."
                        )
                        continue

                r = self.install_solution(solution_id)
                if r:
                    # remove installation failed file if it exists
                    if solution_install_file.exists():
                        solution_install_file.unlink()
                else:
                    # mark installation as failed
                    with open(solution_install_file, "w") as f:
                        f.write("Installation failed")

            except Exception as e:  # noqa: BLE001
                self.logger.log.error(
                    f"Failed to install {solution_id}. {traceback.format_exc()} Look into logfile {str(self.logger.log_file_path)} for details.  You will not be able to run this step!"
                )

    @staticmethod
    def write_install_txt(project_files_path: Path):
        """Write a file indicating that the installation of solutions is done."""
        # create results file for snakemake
        output_file = project_files_path.joinpath("installation_done.txt")
        with open(output_file, "w") as f:
            f.write("Installation of solutions done.\n")
            f.write(f"Date: {str(datetime.now().strftime('%Y%m%d_%H%M%S'))}")

    def uninstall_required(self):
        """Uninstall all required solutions for the interactive workflow."""
        # loop to install all solutions necessary for this interactive workflow
        for solution_id in SOLUTION_IDS:
            try:
                self.uninstall_solution(solution_id)
            except Exception as e:
                print(f"Failed to uninstall {solution_id}: {e}")
