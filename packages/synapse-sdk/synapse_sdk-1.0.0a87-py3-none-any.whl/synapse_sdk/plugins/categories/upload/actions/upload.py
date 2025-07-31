import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Dict, List

from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.clients.utils import get_batched_list
from synapse_sdk.clients.validators.collections import FileSpecificationValidator
from synapse_sdk.i18n import gettext as _
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.models import Run
from synapse_sdk.shared.enums import Context
from synapse_sdk.utils.pydantic.validators import non_blank
from synapse_sdk.utils.storage import get_pathlib


class UploadStatus(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'


class UploadRun(Run):
    class DataFileLog(BaseModel):
        """Data file log model."""

        data_file_info: str | None
        status: UploadStatus
        created: str

    class DataUnitLog(BaseModel):
        """Data unit log model."""

        data_unit_id: int | None
        status: UploadStatus
        created: str

    class TaskLog(BaseModel):
        """Task log model."""

        task_id: int | None
        status: UploadStatus
        created: str

    class MetricsRecord(BaseModel):
        """Metrics record model."""

        stand_by: int
        failed: int
        success: int

    def log_data_file(self, data_file_info: dict, status: UploadStatus):
        """Upload data_file log.

        Args:
            data_file_info (dict): The json info of the data file.
            checksum (str): The checksum of the data file.
            status (DataUnitStatus): The status of the data unit.
        """
        now = datetime.now().isoformat()
        self.log(
            'upload_data_file',
            self.DataFileLog(data_file_info=json.dumps(data_file_info), status=status.value, created=now).model_dump(),
        )

    def log_data_unit(self, data_unit_id: int, status: UploadStatus):
        """Upload data_unit log.

        Args:
            data_unit_id (int): The ID of the data unit.
            status (DataUnitStatus): The status of the data unit.
        """
        now = datetime.now().isoformat()
        self.log(
            'upload_data_unit',
            self.DataUnitLog(data_unit_id=data_unit_id, status=status.value, created=now).model_dump(),
        )

    def log_task(self, task_id: int, status: UploadStatus):
        """Upload task log.

        Args:
            task_id (int): The ID of the task.
            status (UploadStatus): The status of the task.
        """
        now = datetime.now().isoformat()
        self.log('upload_task', self.TaskLog(task_id=task_id, status=status.value, created=now).model_dump())

    def log_metrics(self, record: MetricsRecord, category: str):
        """Log upload metrics.
        Args:
            record (MetricsRecord): The metrics record to log.
            category (str): The category of the metrics.
        """
        record = self.MetricsRecord.model_validate(record)
        self.set_metrics(value=record.model_dump(), category=category)


class UploadParams(BaseModel):
    """Upload action parameters.

    Args:
        name (str): The name of the action.
        description (str | None): The description of the action.
        checkpoint (int | None): The checkpoint of the action.
        path (str): The path of the action.
        storage (int): The storage of the action.
        collection (int): The collection of the action.
        project (int | None): The project of the action.
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None
    path: str
    storage: int
    collection: int
    project: int | None
    is_generate_tasks: bool = False
    is_generate_ground_truths: bool = False

    @field_validator('storage', mode='before')
    @classmethod
    def check_storage_exists(cls, value: str, info) -> str:
        """Validate synapse-backend storage exists.

        TODO: Need to define validation method naming convention.
        TODO: Need to make validation method reusable.
        """
        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Error occurred while checking storage exists.'))
        return value

    @field_validator('collection', mode='before')
    @classmethod
    def check_collection_exists(cls, value: str, info) -> str:
        """Validate synapse-backend collection exists."""
        action = info.context['action']
        client = action.client
        try:
            client.get_data_collection(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Error occurred while checking collection exists.'))
        return value

    @field_validator('project', mode='before')
    @classmethod
    def check_project_exists(cls, value: str, info) -> str:
        """Validate synapse-backend project exists."""
        if not value:
            return value

        action = info.context['action']
        client = action.client
        try:
            client.get_project(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Error occurred while checking project exists.'))
        return value


@register_action
class UploadAction(Action):
    """Upload action class.

    Attrs:
        name (str): The name of the action.
        category (PluginCategory): The category of the action.
        method (RunMethod): The method to run of the action.

    Progress Categories:
        analyze_collection: The progress category for the analyze collection process.
        data_file_upload: The progress category for the upload process.
        generate_data_units: The progress category for the generate data units process.
        generate_tasks: The progress category for the generate tasks process.
        generate_ground_truths: The progress category for the generate ground truths process.

    Metrics Categories:
        data_file: The metrics category for the data file.
        data_unit: The metrics category for the data unit.
    """

    name = 'upload'
    category = PluginCategory.UPLOAD
    method = RunMethod.JOB
    run_class = UploadRun
    progress_categories = {
        'analyze_collection': {
            'proportion': 10,
        },
        'upload_data_files': {
            'proportion': 50,
        },
        'generate_data_units': {
            'proportion': 40,
        },
    }
    metrics_categories = {
        'data_file': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
        'data_unit': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
    }

    def get_uploader(self, path, file_specification, organized_files):
        """Get uploader from entrypoint."""
        return self.entrypoint(self.run, path, file_specification, organized_files)

    def start(self) -> Dict:
        """Start upload process.

        Returns:
            Dict: The result of the upload process.
        """
        # Setup path object with path and storage.
        storage = self.client.get_storage(self.params['storage'])
        pathlib_cwd = get_pathlib(storage, self.params['path'])

        # Analyze Collection file specifications to determine the data structure for upload.
        file_specification_template = self._analyze_collection()
        organized_files = self._organize_files(pathlib_cwd, file_specification_template)

        # Initialize uploader.
        uploader = self.get_uploader(pathlib_cwd, file_specification_template, organized_files)

        # Setup result dict.
        result = {}

        # Get organized files from the uploader (plugin developer's custom implementation)
        # or use the default organization method if uploader doesn't provide valid files
        organized_files = uploader.handle_upload_files()

        # Validate the organized files
        if not self._validate_organized_files(organized_files, file_specification_template):
            self.run.log_message('Validation failed.', context=Context.ERROR.value)
            self.run.end_log()
            return result

        # Upload files to synapse-backend.
        organized_files_count = len(organized_files)
        if not organized_files_count:
            self.run.log_message('Files not found on the path.', context=Context.WARNING.value)
            self.run.end_log()
            return result
        uploaded_files = self._upload_files(organized_files, organized_files_count)
        result['uploaded_files_count'] = len(uploaded_files)

        # Generate data units for the uploaded data.
        upload_result_count = len(uploaded_files)
        if not upload_result_count:
            self.run.log_message('No files were uploaded.', context=Context.WARNING.value)
            self.run.end_log()
            return result
        generated_data_units = self._generate_data_units(uploaded_files, upload_result_count)
        result['generated_data_units_count'] = len(generated_data_units)

        # Setup task with uploaded synapse-backend data units.
        if not len(generated_data_units):
            self.run.log_message('No data units were generated.', context=Context.WARNING.value)
            self.run.end_log()
            return result

        self.run.end_log()
        return result

    def _analyze_collection(self) -> Dict:
        """Analyze Synapse Collection Specifications.

        Returns:
            Dict: The file specifications of the collection.
        """

        # Initialize progress
        self.run.set_progress(0, 1, category='analyze_collection')

        client = self.run.client
        collection_id = self.params['data_collection']
        collection = client.get_data_collection(collection_id)

        # Finish progress
        self.run.set_progress(1, 1, category='analyze_collection')

        return collection['file_specifications']

    def _upload_files(self, organized_files, organized_files_count: int) -> List:
        """Upload files to synapse-backend.

        Returns:
            Dict: The result of the upload.
        """
        # Initialize progress
        self.run.set_progress(0, organized_files_count, category='upload_data_files')
        self.run.log_message('Uploading data files...')
        data_file_metrics_record = self.run.MetricsRecord(stand_by=organized_files_count, success=0, failed=0)

        client = self.run.client
        collection_id = self.params['data_collection']
        upload_result = []
        organized_files_count = len(organized_files)
        current_progress = 0
        for organized_file in organized_files:
            uploaded_data_file = client.upload_data_file(organized_file, collection_id)
            self.run.log_data_file(organized_file, UploadStatus.SUCCESS)
            data_file_metrics_record.stand_by -= 1
            data_file_metrics_record.success += 1
            self.run.log_metrics(record=data_file_metrics_record, category='data_file')
            upload_result.append(uploaded_data_file)
            self.run.set_progress(current_progress, organized_files_count, category='upload_data_files')
            current_progress += 1

        # Finish progress
        self.run.set_progress(organized_files_count, organized_files_count, category='upload_data_files')
        self.run.log_message('Upload data files completed.')

        return upload_result

    def _generate_data_units(self, uploaded_files: List, upload_result_count: int) -> List:
        """Generate data units for the uploaded data.

        TODO: make batch size configurable.

        Returns:
            Dict: The result of the generate data units process.
        """
        # Initialize progress
        self.run.set_progress(0, upload_result_count, category='generate_data_units')
        data_unit_metrics_record = self.run.MetricsRecord(stand_by=upload_result_count, success=0, failed=0)

        client = self.run.client

        generated_data_units = []
        current_progress = 0
        batches = get_batched_list(uploaded_files, 100)
        batches_count = len(batches)
        for batch in batches:
            created_data_units = client.create_data_units(batch)
            data_unit_metrics_record.stand_by -= len(created_data_units)
            data_unit_metrics_record.success += len(created_data_units)
            self.run.log_metrics(record=data_unit_metrics_record, category='data_unit')
            generated_data_units.append(created_data_units)
            self.run.set_progress(current_progress, batches_count, category='generate_data_units')
            current_progress += 1
            for created_data_unit in created_data_units:
                self.run.log_data_unit(created_data_unit['id'], UploadStatus.SUCCESS)

        # Finish progress
        self.run.set_progress(upload_result_count, upload_result_count, category='generate_data_units')

        return sum(generated_data_units, [])

    def _validate_organized_files(self, organized_files: List, file_specification_template: Dict) -> bool:
        """Validate organized files from Uploader."""
        validator = FileSpecificationValidator(file_specification_template, organized_files)
        return validator.validate()

    def _organize_files(self, directory: Path, file_specification: List) -> List:
        """Organize files according to the file specification.
        This method handles type-based directory structure where files are organized in
        directories named after file types (e.g., 'image_1/' directory contains image files
        like '1.jpg', '2.jpg'). For each dataset ID found in the primary directory, it attempts
        to find corresponding files in all type directories.

        TODO : Add Logic to handle file specific name patterns and extensions.
        (e.g. pcd:S_DCH_230725_0156_LR_037.pcd, image_1:S_DCH_230725_0156_FC_037, image_2:S_DCH_230725_0156_LF_037.jpg)
        Args:
            directory (Path): Root directory containing files to organize.
            file_specification (List): File specification list.
        Returns:
            List: List of dictionaries containing organized files.
        """
        organized_files = []

        # Check for type-based directory structure (e.g., image_1/, pcd_1/)
        type_dirs = {}
        type_extensions = {}  # Store common extensions for each type directory

        for spec in file_specification:
            spec_name = spec['name']

            spec_dir = directory / spec_name
            if spec_dir.exists() and spec_dir.is_dir():
                type_dirs[spec_name] = spec_dir

                # Analyze file extensions in this directory
                extensions = {}
                for file_path in spec_dir.glob('*'):
                    if file_path.is_file():
                        ext = file_path.suffix.lower()
                        extensions[ext] = extensions.get(ext, 0) + 1

                # Find the most common extension
                if extensions:
                    common_ext = max(extensions.items(), key=lambda x: x[1])[0]
                    type_extensions[spec_name] = common_ext
                    self.run.log_message(f'Found type directory: {spec_name} (extension: {common_ext})')

        # If type-based directories don't exist, exit early
        if not type_dirs:
            self.run.log_message('No type-based directory structure found.', context=Context.INFO.value)
            return organized_files

        self.run.log_message('Detected type-based directory structure')

        # Build a comprehensive map of all dataset IDs across all type directories
        dataset_files = {}  # Dictionary: file_name -> {spec_name -> file_path}

        # First pass: collect all dataset IDs from all type directories
        for spec_name, dir_path in type_dirs.items():
            for file_path in dir_path.glob('*'):
                if file_path.is_file():
                    file_name = file_path.stem

                    # Initialize dataset entry if it doesn't exist
                    if file_name not in dataset_files:
                        dataset_files[file_name] = {}

                    # Map this file to its specification
                    if spec_name not in dataset_files[file_name]:
                        dataset_files[file_name][spec_name] = file_path
                    else:
                        # If multiple files with same file_name for same spec, use most recent
                        existing_file = dataset_files[file_name][spec_name]
                        if file_path.stat().st_mtime > existing_file.stat().st_mtime:
                            dataset_files[file_name][spec_name] = file_path
                            self.run.log_message(
                                f"Found newer file for name of {file_name}, spec '{spec_name}': "
                                f'{file_path.name} (replacing {existing_file.name})'
                            )

        if not dataset_files:
            self.run.log_message('No files found.', context=Context.WARNING.value)
            return organized_files

        self.run.log_message(f'Found {len(dataset_files)} files by ID')

        # Second pass: organize valid datasets
        for file_name, files_dict in sorted(dataset_files.items()):
            # Check if all required files are present
            required_specs = [spec['name'] for spec in file_specification if spec.get('is_required', False)]
            if all(req in files_dict for req in required_specs):
                # Create metadata for this dataset
                meta_data = {
                    'origin_file_stem': file_name,
                    'created_at': datetime.now().isoformat(),
                }

                # Add the organized dataset
                organized_files.append({'files': files_dict, 'meta': meta_data})
            else:
                # Missing required files warning
                missing = [req for req in required_specs if req not in files_dict]
                self.run.log_message(
                    f'Dataset ID {file_name} is missing required files: {", ".join(missing)}',
                    context=Context.WARNING.value,
                )

        self.run.log_message(f'Total datasets organized: {len(organized_files)}')
        return organized_files
