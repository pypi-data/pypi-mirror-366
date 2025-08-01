from typing import List, Dict, Union, Optional, Callable
from typing import TYPE_CHECKING
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

import requests
import time

from .authorization import Authorization

if TYPE_CHECKING:
    from typing import List, Dict, Union, Optional


class Perception:
    def __init__(self, enable_async_mode: bool = False, max_workers: int = 10):
        # Initialize authorization
        self.auth = Authorization()
        self.base_url = f"{self.auth.host}/perception"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_access_token()}"
        }

        # Async mode configuration
        self.enable_async_mode = enable_async_mode
        self.max_workers = max_workers
        self._executor = None
        self._polling_tasks = {}  # task_id -> future
        self._result_callbacks = {}  # task_id -> callback

        if enable_async_mode:
            self._executor = ThreadPoolExecutor(max_workers=max_workers)
            self._polling_queue = queue.Queue()
            self._start_polling_worker()

    def _start_polling_worker(self):
        """Start background polling worker thread"""
        def polling_worker():
            while True:
                try:
                    task_info = self._polling_queue.get(timeout=1)
                    if task_info is None:  # Shutdown signal
                        break

                    task_id, callback, timeout = task_info
                    try:
                        result = self._poll_task_result(task_id, timeout)
                        if callback:
                            callback(result, None)
                    except Exception as e:
                        if callback:
                            callback(None, e)
                    finally:
                        self._polling_queue.task_done()

                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Polling worker error: {e}")

        self._polling_thread = threading.Thread(target=polling_worker, daemon=True)
        self._polling_thread.start()

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, '_executor') and self._executor:
            self._executor.shutdown(wait=False)
        if hasattr(self, '_polling_queue'):
            self._polling_queue.put(None)  # Shutdown signal

    def _get_task_result(self, task_id: str) -> Dict:
        """Get the result of a perception task
        
        Args:
            task_id (str): The ID of the task to get results for
        
        Returns:
            Dict: The complete task result containing status and data.
                 The structure of taskResult varies depending on the task type.
                 For detailed response structures, please refer to:
                 https://qj-robots.feishu.cn/wiki/CT5cwncfdi28nEk24vZcOl9Nnye
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        return self._make_get_request(
            endpoint="/open-api/open-apis/app/perception/result",
            params={"task_id": task_id}
        )

    def _poll_task_result(self, task_id: str, timeout: int = 30) -> Dict:
        """Poll for task result until completion or timeout
        
        Args:
            task_id (str): The ID of the task to poll for
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 30.
        
        Returns:
            Dict: The complete task result
        
        Raises:
            TimeoutError: If polling exceeds timeout seconds
        """
        start_time = time.time()
        while True:
            # Check if polling has exceeded timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f"{task_id} => Polling exceeded {timeout} seconds timeout")

            # Get task result
            result = self._get_task_result(task_id)

            if result['taskStatus'] == 'SUBMIT_FAILED':
                raise RuntimeError(f"{task_id} => task submit failed,please retry later.")
            # Return if task is complete
            if result['taskStatus'] == 'DONE':
                return result

            # Wait before next poll
            time.sleep(0.01)

    def _validate_image_params(self, image_type: str, depth_url: Optional[str] = None) -> None:
        """Validate image type and depth_url parameters
        
        Args:
            image_type (str): Image type to validate
            depth_url (Optional[str], optional): Depth URL to validate for 3D images
        
        Raises:
            ValueError: If parameters are invalid
        """
        if image_type not in ['2D', '3D']:
            raise ValueError("image_type must be either '2D' or '3D'")

        if image_type == '3D' and not depth_url:
            raise ValueError("depth_url is required for 3D images")

    def _process_object_names(self, object_names: Union[str, List[str]]) -> str:
        """Process object names into comma-separated string
        
        Args:
            object_names (Union[str, List[str]]): Names of objects to process
        
        Returns:
            str: Comma-separated string of object names
        """
        if isinstance(object_names, list):
            return ','.join(object_names)
        return object_names

    def _prepare_request_data(self, image_type: str, image_url: str,
                              object_names: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict:
        """Prepare request data for perception API calls
        
        Args:
            image_type (str): Image type ('2D' or '3D')
            image_url (str): URL of the image
            object_names (Union[str, List[str]]): Names of objects
            depth_url (Optional[str], optional): URL of the depth image
        
        Returns:
            Dict: Prepared request data
        """
        data = {
            "image_type": image_type,
            "image_url": image_url,
            "object_names": self._process_object_names(object_names)
        }

        if depth_url:
            data["depth_url"] = depth_url

        return data

    def _make_post_request(self, endpoint: str, data: Dict) -> Dict:
        """Make POST request to perception API
        
        Args:
            endpoint (str): API endpoint
            data (Dict): Request data
        
        Returns:
            Dict: Response data
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.auth.host}{endpoint}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()

        result = response.json()
        if result["code"] != 0:
            raise Exception(f"API request failed: {result['message']}")

        return result["data"]

    def _make_get_request(self, endpoint: str, params: Dict) -> Dict:
        """Make GET request to perception API
        
        Args:
            endpoint (str): API endpoint
            params (Dict): Request parameters
        
        Returns:
            Dict: Response data
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.auth.host}{endpoint}"
        response = requests.get(url, params=params)

        result = response.json()
        if result["code"] != 0:
            raise Exception(f"API request failed: {result['message']}")

        return result["data"]

    def submit_task_async(self, endpoint: str, data: Dict,
                         callback: Optional[Callable[[Dict, Exception], None]] = None,
                         timeout: int = 30) -> str:
        """Submit a perception task asynchronously

        Args:
            endpoint (str): API endpoint
            data (Dict): Request data
            callback (Optional[Callable]): Callback function called when task completes
            timeout (int): Polling timeout in seconds

        Returns:
            str: Task ID for tracking

        Raises:
            RuntimeError: If async mode is not enabled
        """
        if not self.enable_async_mode:
            raise RuntimeError("Async mode is not enabled. Initialize with enable_async_mode=True")

        # Submit task and get task ID
        result = self._make_post_request(endpoint, data)
        task_id = result['taskId']

        # Add to polling queue
        self._polling_queue.put((task_id, callback, timeout))

        return task_id

    def get_task_result_sync(self, task_id: str) -> Dict:
        """Get task result synchronously (for async submitted tasks)

        Args:
            task_id (str): Task ID

        Returns:
            Dict: Task result
        """
        return self._get_task_result(task_id)

    def check_image(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                    depth_url: Optional[str] = None) -> Dict:
        """Check image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be checked
            object_names (Union[str, List[str]]): Names of objects to detect, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 For detailed response structures, please refer to:
                 https://qj-robots.feishu.cn/wiki/CT5cwncfdi28nEk24vZcOl9Nnye
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/check",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def split_image(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                    depth_url: Optional[str] = None) -> Dict:
        """Split objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to segment, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - masks: List of mask objects containing maskImage URL and maskData
                 - croppedImagesListBbox: List of cropped image URLs
                 - labels: List of detected object labels
                 - scores: List of confidence scores
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/split",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def props_describe(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                       questions: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict:
        """Get detailed property descriptions of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to describe, can be a comma-separated string or a list of strings
            questions (Union[str, List[str]]): Questions about object properties, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - answers: List of property description objects
                 - questions: List of property questions
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Add questions to request data
        if isinstance(questions, list):
            data["questions"] = ','.join(questions)
        else:
            data["questions"] = questions

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/props-describe",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def angle_prediction(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                         depth_url: Optional[str] = None) -> Dict:
        """Predict angles of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to predict angles for, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - angles: List of angle objects containing angle value and corner points
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - croppedImagesListAngle: List of cropped image URLs
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/angle-prediction",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def key_point_prediction(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                             depth_url: Optional[str] = None) -> Dict:
        """Predict key points of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to predict key points for, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - points: List of point objects containing:
                   - pointBoxes: List of point box coordinates [x1,y1,x2,y2]
                   - pointLabels: List of point labels
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - croppedImagesListPoint: List of cropped image URLs
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/key-point-prediction",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def grab_point_prediction(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                              depth_url: Optional[str] = None) -> Dict:
        """Predict grab points of objects in an image using perception model
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to predict grab points for, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - grasps: List of grasp objects containing:
                   - graspAngle: Angle of the grasp
                   - graspPoint: List of grasp point coordinates [x,y]
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - labels: List of detected object labels
                 - scores: List of confidence scores
                 - croppedImagesListGrasp: List of cropped image URLs
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/grab-point-prediction",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    def full_perception(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                        questions: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict:
        """Submit a comprehensive perception task that includes all 6 perception functions
        
        Args:
            image_type (str): Image type, must be either '2D' or '3D'
            image_url (str): URL of the image to be processed
            object_names (Union[str, List[str]]): Names of objects to analyze, can be a comma-separated string or a list of strings
            questions (Union[str, List[str]]): Questions about object properties, can be a comma-separated string or a list of strings
            depth_url (Optional[str], optional): URL of the depth image, required when image_type is '3D'. Defaults to None.
        
        Returns:
            Dict: The complete task result containing status and data.
                 The taskResult includes:
                 - angles: List of angle objects containing angle value and corner points
                 - angles3D: List of 3D angle information
                 - answers: List of property description objects
                 - boxes: List of bounding box coordinates [x1,y1,x2,y2]
                 - croppedImagesListAngle: List of angle-based cropped image URLs
                 - croppedImagesListBbox: List of bbox-based cropped image URLs
                 - croppedImagesListGrasp: List of grasp-based cropped image URLs
                 - croppedImagesListPoint: List of point-based cropped image URLs
                 - croppedImagesListSegment: List of segment-based cropped image URLs
                 - grasps: List of grasp objects containing angle, depth, height, width etc.
                 - labels: List of detected object labels
                 - maskImage: List of mask image download URLs
                 - maskData: List of mask data download URLs
                 - points: List of point objects containing coordinates and labels
                 - questions: List of property questions
                 - scores: List of confidence scores
        
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            TimeoutError: If polling exceeds 30 seconds
        """
        # Validate parameters
        self._validate_image_params(image_type, depth_url)

        # Prepare request data
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)

        # Add questions to request data
        if isinstance(questions, list):
            data["questions"] = ','.join(questions)
        else:
            data["questions"] = questions

        # Send request and get task ID
        result = self._make_post_request(
            endpoint="/open-api/open-apis/app/perception/full",
            data=data
        )

        # Poll for results
        return self._poll_task_result(result['taskId'])

    # Async versions of perception methods
    def check_image_async(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                         depth_url: Optional[str] = None,
                         callback: Optional[Callable[[Dict, Exception], None]] = None,
                         timeout: int = 30) -> str:
        """Async version of check_image"""
        self._validate_image_params(image_type, depth_url)
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)
        return self.submit_task_async("/open-api/open-apis/app/perception/check", data, callback, timeout)

    def split_image_async(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                         depth_url: Optional[str] = None,
                         callback: Optional[Callable[[Dict, Exception], None]] = None,
                         timeout: int = 30) -> str:
        """Async version of split_image"""
        self._validate_image_params(image_type, depth_url)
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)
        return self.submit_task_async("/open-api/open-apis/app/perception/split", data, callback, timeout)

    def props_describe_async(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                            questions: Union[str, List[str]], depth_url: Optional[str] = None,
                            callback: Optional[Callable[[Dict, Exception], None]] = None,
                            timeout: int = 30) -> str:
        """Async version of props_describe"""
        self._validate_image_params(image_type, depth_url)
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)
        if isinstance(questions, list):
            data["questions"] = ','.join(questions)
        else:
            data["questions"] = questions
        return self.submit_task_async("/open-api/open-apis/app/perception/props-describe", data, callback, timeout)

    def angle_prediction_async(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                              depth_url: Optional[str] = None,
                              callback: Optional[Callable[[Dict, Exception], None]] = None,
                              timeout: int = 30) -> str:
        """Async version of angle_prediction"""
        self._validate_image_params(image_type, depth_url)
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)
        return self.submit_task_async("/open-api/open-apis/app/perception/angle-prediction", data, callback, timeout)

    def key_point_prediction_async(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                                  depth_url: Optional[str] = None,
                                  callback: Optional[Callable[[Dict, Exception], None]] = None,
                                  timeout: int = 30) -> str:
        """Async version of key_point_prediction"""
        self._validate_image_params(image_type, depth_url)
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)
        return self.submit_task_async("/open-api/open-apis/app/perception/key-point-prediction", data, callback, timeout)

    def grab_point_prediction_async(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                                   depth_url: Optional[str] = None,
                                   callback: Optional[Callable[[Dict, Exception], None]] = None,
                                   timeout: int = 30) -> str:
        """Async version of grab_point_prediction"""
        self._validate_image_params(image_type, depth_url)
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)
        return self.submit_task_async("/open-api/open-apis/app/perception/grab-point-prediction", data, callback, timeout)

    def full_perception_async(self, image_type: str, image_url: str, object_names: Union[str, List[str]],
                             questions: Union[str, List[str]], depth_url: Optional[str] = None,
                             callback: Optional[Callable[[Dict, Exception], None]] = None,
                             timeout: int = 30) -> str:
        """Async version of full_perception"""
        self._validate_image_params(image_type, depth_url)
        data = self._prepare_request_data(image_type, image_url, object_names, depth_url)
        if isinstance(questions, list):
            data["questions"] = ','.join(questions)
        else:
            data["questions"] = questions
        return self.submit_task_async("/open-api/open-apis/app/perception/full", data, callback, timeout)
