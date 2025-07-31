import json
import SimpleITK as sitk
from pathlib import Path
from loguru import logger
from multiprocessing import Pool
from threadpoolctl import threadpool_limits

from mircat_v2.configs import read_dbase_config, read_segmentation_config
from mircat_v2.dbase import insert_data_batch
from mircat_v2.nifti import StatsNifti
from mircat_v2.stats.aorta import calculate_aorta_stats
from mircat_v2.stats.contrast import predict_contrast
from mircat_v2.stats.tissues import calculate_tissue_stats
from mircat_v2.stats.vertebrae import calculate_vertebrae_stats
from mircat_v2.stats.vol_int import calculate_volume_and_intensity_stats


class Analyzer:
    """Analyzer class for processing and analyzing tasks with specified parameters."""

    # Map for resolution settings
    resolution_map = {
        "normal": [1.0, 1.0, 1.0],
        "high": [0.75, 0.75, 0.75],
        "highest": [0.5, 0.5, 0.5],
    }
    # Segmentations needed for specific tasks in order of preference
    task_map = {
        "vol_int": ["999"],
        "contrast": ["999"],
        "vertebrae": ["999"],
        "aorta": ["999"],
        "tissues": ["485", "481"],
        "body": ["299", "300"],
    }

    empty_stats_insert = {
        "metadata": [],
        "vol_int": [],
        "contrast": [],
        "vertebrae": [],
        "aorta_metrics": [],
        "aorta_diameters": [],
        "tissues_volumetric": [],
        "tissues_vertebral": [],
    }

    def __init__(
        self,
        task_list: list[str],
        resolution: str,
        image_resampler: str,
        label_resampler: str,
        n_processes: int,
        threads_per_process: int,
        dbase_insert: bool = False,
        overwrite: bool = False,
        gzip: bool = False,
    ):
        if task_list == ["all"]:
            task_list = list(self.task_map.keys())
        # This orders the tasks by the order they are defined in task_map
        self.task_list = [task for task in self.task_map if task in task_list]
        if "tissues" in self.task_list and "body" not in task_list:
            self.task_list.append("body")
        self.resolution = self.resolution_map.get(resolution)
        self.image_resampler = image_resampler
        self.label_resampler = label_resampler
        self.n_processes = n_processes
        self.threads_per_process = threads_per_process
        # Read database configuration if dbase_insert is True
        self.dbase_insert = dbase_insert
        if dbase_insert:
            self.dbase_config = read_dbase_config()
        else:
            self.dbase_config = {}
        # Read segmentation configuration
        seg_config = read_segmentation_config()
        # We only need the labels for each task
        self.segmentation_labels = {
            task: seg_config[task]["labels"] for task in seg_config
        }
        self.overwrite = overwrite
        self.gzip = gzip

    def _get_nifti_list(self, niftis):
        niftis = Path(niftis).resolve()
        if not niftis.exists():
            raise FileNotFoundError(f"Nifti file {niftis} does not exist.")
        if niftis.suffix in [".nii", ".gz"]:
            self.niftis = [niftis]
        else:
            with niftis.open() as f:
                self.niftis = [Path(line.strip()).resolve() for line in f.readlines()]
        self.total_niftis = len(self.niftis)
        if self.total_niftis == 0:
            raise ValueError("No valid nifti files found in the provided path or file.")
        logger.info(f"Found {self.total_niftis} nifti files to process from {niftis}.")

    def analyze(self, nifti_path: Path | str) -> StatsNifti:
        """Analyze a single nifti file.
        :param nifti_path: Path to the nifti file to analyze.
        """
        sitk.ProcessObject.SetGlobalDefaultNumberOfThreads(self.threads_per_process)
        with threadpool_limits(self.threads_per_process):
            nifti = StatsNifti(nifti_path, self.overwrite)
            # Preprocess the nifti file for statistics
            (
                nifti.check_for_segmentations(
                    self.task_list, self.task_map
                ).preprocess_for_stats(
                    self.resolution, self.image_resampler, self.label_resampler
                )
            )
            self.analyze_tasks(nifti)
        nifti.save_json_stats(self.gzip)
        nifti.format_stats_for_db()
        return nifti

    def analyze_tasks(self, nifti: StatsNifti) -> None:
        for task in self.task_list:
            seg_id = nifti.task_to_id_map[task]
            seg_labels = self.segmentation_labels[seg_id]
            match task:
                case "vol_int":
                    vol_int_stats = calculate_volume_and_intensity_stats(
                        nifti, seg_id, seg_labels
                    )
                    nifti.add_stats("vol_int", vol_int_stats)
                case "contrast":
                    if not nifti.stats.get("vol_int", {}):
                        logger.warning(
                            "Organ intensities are needed for contrast prediction. Skipping contrast task."
                        )
                        continue
                    contrast_stats = predict_contrast(nifti.stats["vol_int"])
                    nifti.add_stats("contrast", contrast_stats)
                case "vertebrae":
                    vertebrae_stats = calculate_vertebrae_stats(
                        nifti, seg_id, seg_labels
                    )
                    # Add the structural vert stats to the metadata for easy searching
                    for key in [
                        "lowest_vertebra",
                        "highest_vertebra",
                        "correct_vertebrae_order",
                        "abdominal_scan",
                        "chest_scan",
                    ]:
                        nifti.add_stats(key, vertebrae_stats.pop(key, None), "metadata")
                    nifti.add_stats("vertebrae", vertebrae_stats)
                    nifti.set_vertebrae_midlines(vertebrae_stats)
                case "aorta":
                    aorta_stats = calculate_aorta_stats(nifti, seg_id, seg_labels)
                    nifti.add_stats("aorta", aorta_stats)
                case "tissues":
                    # Need body segmentation for tissue stats
                    body_seg_id = nifti.task_to_id_map.get("body", None)
                    if not body_seg_id:
                        logger.warning(
                            "Body segmentation is required for tissue statistics. Skipping tissue task."
                        )
                        continue
                    body_labels = self.segmentation_labels[body_seg_id]
                    tissue_stats = calculate_tissue_stats(
                        nifti, seg_id, seg_labels, body_seg_id, body_labels
                    )
                    nifti.add_stats("tissues", tissue_stats)

    def run(self, niftis: Path | str, batch_insert_size: int = 100) -> None:
        """Run the analysis on the provided NiFTi files.
        :param niftis: Path to a nifti file with mircat-v2 segmentations or a text file with a list of multiple mircat-v2 nifti files.
        """
        self._get_nifti_list(niftis)
        if self.n_processes > 1:
            logger.info(f"Running analysis with {self.n_processes} processes.")
        else:
            logger.info("Running analysis with single process.")
        logger.info(
            f"Using resolution: {self.resolution} mm, image resampler: {self.image_resampler}, label resampler: {self.label_resampler}."
        )
        logger.info(f"Tasks to run: {self.task_list}.")
        logger.info(f"Starting analysis on {self.total_niftis} nifti files.")
        batch_data = self.empty_stats_insert.copy()
        with Pool(processes=self.n_processes) as pool:
            for i, nifti in enumerate(
                pool.imap_unordered(self.analyze, self.niftis), start=1
            ):
                logger.success(
                    f"Stats: [{i}/{self.total_niftis}] - Successfully calculated statistics for {nifti.name}."
                )
                if self.dbase_insert:
                    for key, list_data in nifti.db_stats.items():
                        batch_data[key].extend(list_data)
                    if i % batch_insert_size == 0:
                        logger.info(
                            "inserting data from {} nifti files into the database.",
                            batch_insert_size,
                        )
                        for key, list_data in batch_data.items():
                            if list_data:
                                insert_data_batch(self.dbase_config, key, list_data)
                        batch_data = self.empty_stats_insert.copy()

        if self.dbase_insert and batch_data:
            logger.info("inserting remaining nifti files into the database.")
            for key, list_data in batch_data.items():
                if list_data:
                    insert_data_batch(self.dbase_config, key, list_data)
