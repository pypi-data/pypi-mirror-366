# redix_client/client.py
import os
import httpx
import logging
from typing import List, Optional, Dict, Any, Generator
from datetime import date

from .models import (
    BatchStatusResponse, BatchJobSummary, ConversionResponse, UploadResponse, FileDeleteResponse,
    FileInfo, FileViewResponse, BatchLog, BatchFileDetail, BatchSummaryResponse, StagingProfilesResponse
)
from .enums import ConversionFlag, FileType, WarningLevel, BatchJobStatus
from .exceptions import RedixAPIError

logger = logging.getLogger(__name__)

class RedixClient:
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 60, verbose: bool = False):
        """
        Python client for Redix Healthcare Data Conversion REST API.
        
        Args:
            api_url (str): Base URL for API (e.g. http://localhost:8000)
            api_key (str): API key for authentication
            timeout (int): Timeout for HTTP requests in seconds
            verbose (bool): Enable debug logging (default False)
        """
        self.api_url = (api_url or os.getenv("REDIX_API_URL", "")).rstrip("/")
        self.headers = {"X-API-Key": api_key or os.getenv("REDIX_API_KEY", "")}
        self.timeout = timeout
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    # --- Batch Processing ---

    def batch_convert_folder(
        self,
        Input_Subfolder: str,
        Config_Profile: str,
        Output_Subfolder: Optional[str] = None,
        User_Data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate batch conversion on a folder.
        
        Args:
            Input_Subfolder (str): Subfolder in batch input dir.
            Config_Profile (str): Configuration profile name (validate with list_staging_profiles()).
            Output_Subfolder (Optional[str]): Optional output subfolder.
            User_Data (Optional[str]): Optional user data.
        
        Returns:
            Dict[str, Any]: Job ID and status message.
        
        Raises:
            RedixAPIError: If API call fails.
        """
        logger.debug(f"Starting batch conversion for profile: {Config_Profile}")
        url = f"{self.api_url}/api/v1/batch-convert/folder"
        data = {
            "Input_Subfolder": Input_Subfolder,
            "Config_Profile": Config_Profile,
        }
        if Output_Subfolder:
            data["Output_Subfolder"] = Output_Subfolder
        if User_Data:
            data["User_Data"] = User_Data
        resp = httpx.post(url, data=data, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return resp.json()

    def batch_status(self, job_id: str) -> BatchStatusResponse:
        """
        Get status of a batch job.
        
        Args:
            job_id (str): Batch job ID.
        
        Returns:
            BatchStatusResponse: Job status details.
        
        Raises:
            RedixAPIError: If API call fails.
        """
        url = f"{self.api_url}/api/v1/batch-status/{job_id}"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return BatchStatusResponse.parse_obj(resp.json())

    def batch_jobs(
        self,
        Status: Optional[BatchJobStatus] = None,
        Config_Profile: Optional[str] = None,
        Start_Date: Optional[date] = None,
        End_Date: Optional[date] = None,
        Limit: int = 10,
        Offset: int = 0
    ) -> List[BatchJobSummary]:
        """
        List batch jobs with filters.
        
        Args:
            Status (Optional[BatchJobStatus]): Job status filter (enum).
            Config_Profile (Optional[str]): Profile filter (validate with list_staging_profiles()).
            Start_Date (Optional[date]): Start date filter.
            End_Date (Optional[date]): End date filter.
            Limit (int): Max results (default 10).
            Offset (int): Results offset (default 0).
        
        Returns:
            List[BatchJobSummary]: List of batch job summaries.
        
        Raises:
            RedixAPIError: If API call fails.
        """
        url = f"{self.api_url}/api/v1/batch-jobs"
        params = {
            "Status": Status.value if Status else None,
            "Config_Profile": Config_Profile,
            "Start_Date": Start_Date.isoformat() if Start_Date else None,
            "End_Date": End_Date.isoformat() if End_Date else None,
            "Limit": Limit,
            "Offset": Offset
        }
        params = {k: v for k, v in params.items() if v is not None}
        resp = httpx.get(url, headers=self.headers, params=params, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return [BatchJobSummary.parse_obj(item) for item in resp.json()]

    def all_batch_jobs(
        self,
        Status: Optional[BatchJobStatus] = None,
        Config_Profile: Optional[str] = None,
        Start_Date: Optional[date] = None,
        End_Date: Optional[date] = None,
        page_size: int = 50
    ) -> Generator[BatchJobSummary, None, None]:
        """
        Generator to fetch all batch jobs across pages.
        
        Args:
            Status (Optional[BatchJobStatus]): Job status filter (enum).
            Config_Profile (Optional[str]): Profile filter.
            Start_Date (Optional[date]): Start date filter.
            End_Date (Optional[date]): End date filter.
            page_size (int): Results per page (default 50).
        
        Yields:
            BatchJobSummary: Each batch job summary.
        
        Raises:
            RedixAPIError: If API call fails.
        """
        offset = 0
        while True:
            jobs = self.batch_jobs(
                Status=Status,
                Config_Profile=Config_Profile,
                Start_Date=Start_Date,
                End_Date=End_Date,
                Limit=page_size,
                Offset=offset
            )
            if not jobs:
                break
            for job in jobs:
                yield job
            offset += page_size

    def batch_job_logs(self, Job_Id: str, Limit=50, Offset=0, Log_Level: Optional[str]=None) -> List[BatchLog]:
        """
        Get logs for a batch job.
        
        Args:
            Job_Id (str): Batch job ID.
            Limit (int): Max logs (default 50).
            Offset (int): Logs offset (default 0).
            Log_Level (Optional[str]): Log level filter.
        
        Returns:
            List[BatchLog]: List of log entries.
        
        Raises:
            RedixAPIError: If API call fails.
        """
        url = f"{self.api_url}/api/v1/batch-jobs/{Job_Id}/logs"
        params = {"Limit": Limit, "Offset": Offset}
        if Log_Level:
            params["Log_Level"] = Log_Level
        resp = httpx.get(url, headers=self.headers, params=params, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return [BatchLog.parse_obj(item) for item in resp.json()]

    def batch_job_file_details(self, Job_Id: str, Filename: str) -> BatchFileDetail:
        """
        Get details for a file in a batch job.
        
        Args:
            Job_Id (str): Batch job ID.
            Filename (str): Filename in the batch.
        
        Returns:
            BatchFileDetail: File details.
        
        Raises:
            RedixAPIError: If API call fails.
        """
        url = f"{self.api_url}/api/v1/batch-jobs/{Job_Id}/files/{Filename}/details"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return BatchFileDetail.parse_obj(resp.json())

    def batch_jobs_summary(
        self, Start_Date: Optional[date] = None, End_Date: Optional[date] = None, Config_Profile: Optional[str]=None
    ) -> BatchSummaryResponse:
        """
        Get summary of batch jobs.
        
        Args:
            Start_Date (Optional[date]): Start date filter.
            End_Date (Optional[date]): End date filter.
            Config_Profile (Optional[str]): Profile filter (validate with list_staging_profiles()).
        
        Returns:
            BatchSummaryResponse: Aggregate summary.
        
        Raises:
            RedixAPIError: If API call fails.
        """
        url = f"{self.api_url}/api/v1/batch-jobs/summary"
        params = {
            "Start_Date": Start_Date.isoformat() if Start_Date else None,
            "End_Date": End_Date.isoformat() if End_Date else None,
            "Config_Profile": Config_Profile
        }
        params = {k: v for k, v in params.items() if v is not None}
        resp = httpx.get(url, headers=self.headers, params=params, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return BatchSummaryResponse.parse_obj(resp.json())

    # --- File Upload/Download/View ---

    def upload_to_staging(self, file_path: str) -> UploadResponse:
        """
        Upload a file to staging area.
        
        Args:
            file_path (str): Local path to file.
        
        Returns:
            UploadResponse: Upload result.
        
        Raises:
            RedixAPIError: If upload fails or file not found.
        """
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                resp = httpx.post(f"{self.api_url}/api/v1/staging/upload", files=files, headers=self.headers, timeout=self.timeout)
            if resp.status_code != 200:
                raise RedixAPIError(resp.status_code, resp.text)
            return UploadResponse.parse_obj(resp.json())
        except FileNotFoundError as e:
            raise RedixAPIError(404, f"Local file not found: {str(e)}") from e
        except PermissionError as e:
            raise RedixAPIError(403, f"Permission denied for local file: {str(e)}") from e

    def delete_from_staging(self, filename: str) -> FileDeleteResponse:
        """
        Delete a file from staging.
        
        Args:
            filename (str): Filename in staging.
        
        Returns:
            FileDeleteResponse: Deletion result.
        
        Raises:
            RedixAPIError: If deletion fails.
        """
        url = f"{self.api_url}/api/v1/staging/{filename}"
        resp = httpx.delete(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return FileDeleteResponse.parse_obj(resp.json())

    def download_file(self, File_Type: FileType, Filename: str, dest_path: Optional[str]=None) -> str:
        """
        Download a file to local path.
        
        Args:
            File_Type (FileType): Type of file (enum).
            Filename (str): Filename to download.
            dest_path (Optional[str]): Local save path (defaults to Filename).
        
        Returns:
            str: Path where file was saved.
        
        Raises:
            RedixAPIError: If download fails or local write issues.
        """
        url = f"{self.api_url}/api/v1/download-file/{File_Type.value}/{Filename}"
        if dest_path is None:
            dest_path = Filename
        if os.path.isdir(dest_path):
            dest_path = os.path.join(dest_path, Filename)
        try:
            with httpx.stream("GET", url, headers=self.headers, timeout=self.timeout) as resp:
                if resp.status_code != 200:
                    raise RedixAPIError(resp.status_code, resp.text)
                with open(dest_path, "wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)
            return dest_path
        except PermissionError as e:
            raise RedixAPIError(403, f"Permission denied writing to local path: {str(e)}") from e

    def view_file(self, File_Type: FileType, Filename: str, as_bytes: bool = False) -> Any:
        """
        View file content as text or bytes.
        
        Args:
            File_Type (FileType): Type of file (enum).
            Filename (str): Filename to view.
            as_bytes (bool): Return as bytes for binary/non-text files (default False). 
            Note: Text mode is only for UTF-8 or ASCII-safe files; for others, always use as_bytes=True to avoid decoding errors.
        
        Returns:
            FileViewResponse or bytes: File content.
        
        Raises:
            RedixAPIError: If view fails.
        """
        url = f"{self.api_url}/api/v1/view-file/{File_Type.value}/{Filename}"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        if as_bytes:
            return resp.content
        try:
            return FileViewResponse(content=resp.text)
        except UnicodeDecodeError as e:
            logger.warning(f"Decoding error for text mode; recommend as_bytes=True: {str(e)}")
            raise RedixAPIError(500, "Decoding error - use as_bytes=True for non-text files.") from e

    # --- Listing/Discovery ---

    def list_form_options(self) -> Dict[str, Any]:
        """
        Get form options for conversion (flags, files, etc.).
        
        Returns:
            Dict[str, Any]: Form options data.
        
        Raises:
            RedixAPIError: If call fails.
        """
        url = f"{self.api_url}/api/v1/form-options"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return resp.json()

    def list_files(self) -> List[FileInfo]:
        """
        List recent conversion files.
        
        Returns:
            List[FileInfo]: List of file info.
        
        Raises:
            RedixAPIError: If call fails.
        """
        url = f"{self.api_url}/api/v1/files"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return [FileInfo.parse_obj(item) for item in resp.json()["files"]]

    def list_server_files(self, path: str = "", include_dirs: bool = False) -> Dict[str, Any]:
        """
        List files/directories in shared server dir.
        
        Args:
            path (str): Subpath to list (default "").
            include_dirs (bool): Include directories (default False).
        
        Returns:
            Dict[str, Any]: Current path and files list.
        
        Raises:
            RedixAPIError: If call fails.
        """
        url = f"{self.api_url}/api/v1/server-files"
        params = {"path": path, "include_dirs": include_dirs}
        resp = httpx.get(url, headers=self.headers, params=params, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return resp.json()

    def list_staging_files(self) -> List[FileInfo]:
        """
        List files in staging directory.
        
        Returns:
            List[FileInfo]: List of staging file info.
        
        Raises:
            RedixAPIError: If call fails.
        """
        url = f"{self.api_url}/api/v1/staging-files"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return [FileInfo.parse_obj(item) for item in resp.json()["files"]]

    def list_staging_profiles(self) -> StagingProfilesResponse:
        """
        List available staging profiles.
        
        Returns:
            StagingProfilesResponse: Default and available profiles.
        
        Raises:
            RedixAPIError: If call fails.
        """
        url = f"{self.api_url}/api/v1/staging-profiles"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return StagingProfilesResponse.parse_obj(resp.json())

    # --- File Conversion ---

    def convert_file_upload(
        self,
        Input_File: str,
        IFD_File: str,
        OFD_File: str,
        Conversion_Flag: ConversionFlag,
        WarningLevel: WarningLevel = WarningLevel.CONTINUE_WITH_WARNINGS,
        User_Data: str = "",
        Segment_Terminator: str = "new line",
        Element_Separator: str = "*",
        Composite_Separator: str = ":",
        Release_Character: str = "?"
    ) -> ConversionResponse:
        """
        Convert via file upload (browser-style).
        
        Args:
            Input_File (str): Path to input file.
            IFD_File (str): Path to IFD rule file.
            OFD_File (str): Path to OFD rule file.
            Conversion_Flag (ConversionFlag): Conversion type (enum).
            WarningLevel (WarningLevel): Warning level (enum, default CONTINUE_WITH_WARNINGS).
            User_Data (str): Optional user data.
            Segment_Terminator (str): Segment terminator (default "new line").
            Element_Separator (str): Element separator (default "*").
            Composite_Separator (str): Composite separator (default ":").
            Release_Character (str): Release character (default "?").
        
        Returns:
            ConversionResponse: Conversion result.
        
        Raises:
            RedixAPIError: If conversion fails or files not found.
        """
        url = f"{self.api_url}/api/v1/convert/file-upload"
        try:
            with open(Input_File, "rb") as input_f, open(IFD_File, "rb") as ifd_f, open(OFD_File, "rb") as ofd_f:
                files = {
                    "Input_File": (os.path.basename(Input_File), input_f),
                    "IFD_File": (os.path.basename(IFD_File), ifd_f),
                    "OFD_File": (os.path.basename(OFD_File), ofd_f),
                }
                data = {
                    "Conversion_Flag": Conversion_Flag.value,
                    "WarningLevel": WarningLevel.value,
                    "User_Data": User_Data,
                    "Segment_Terminator": Segment_Terminator,
                    "Element_Separator": Element_Separator,
                    "Composite_Separator": Composite_Separator,
                    "Release_Character": Release_Character
                }
                resp = httpx.post(url, data=data, files=files, headers=self.headers, timeout=self.timeout)
            if resp.status_code != 200:
                raise RedixAPIError(resp.status_code, resp.text)
            return ConversionResponse.parse_obj(resp.json())
        except FileNotFoundError as e:
            raise RedixAPIError(404, f"Local file not found: {str(e)}") from e
        except PermissionError as e:
            raise RedixAPIError(403, f"Permission denied for local file: {str(e)}") from e

    def convert_staging_file(
        self, Staged_Filename: str, Config_Profile: Optional[str] = None, User_Data: Optional[str] = None
    ) -> ConversionResponse:
        """
        Convert a staged file using a profile.
        
        Args:
            Staged_Filename (str): Filename in staging.
            Config_Profile (Optional[str]): Profile name (validate with list_staging_profiles()).
            User_Data (Optional[str]): Optional user data.
        
        Returns:
            ConversionResponse: Conversion result.
        
        Raises:
            RedixAPIError: If conversion fails.
        """
        url = f"{self.api_url}/api/v1/convert/staging-file"
        data = {"Staged_Filename": Staged_Filename}
        if Config_Profile:
            data["Config_Profile"] = Config_Profile
        if User_Data:
            data["User_Data"] = User_Data
        resp = httpx.post(url, data=data, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return ConversionResponse.parse_obj(resp.json())

    # --- Info & Health ---

    def health_check(self) -> Dict[str, Any]:
        """
        Get API health status.
        
        Returns:
            Dict[str, Any]: Health info.
        
        Raises:
            RedixAPIError: If call fails.
        """
        url = f"{self.api_url}/"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return resp.json()

    def engine_info(self) -> Dict[str, Any]:
        """
        Get Redix engine info.
        
        Returns:
            Dict[str, Any]: Engine details.
        
        Raises:
            RedixAPIError: If call fails.
        """
        url = f"{self.api_url}/engine/info"
        resp = httpx.get(url, headers=self.headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RedixAPIError(resp.status_code, resp.text)
        return resp.json()