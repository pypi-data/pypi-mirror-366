# py-qj-robots

[简体中文](https://github.com/QJ-ROBOTS/perception-python-sdk/wiki/%E5%8D%83%E8%AF%80%C2%B7%E6%84%9F%E7%9F%A5%E5%A4%A7%E6%A8%A1%E5%9E%8B) | [EN](https://github.com/QJ-ROBOTS/perception-python-sdk/wiki/QJ-PERCEPTION-MODEL)


QJ Robots Python SDK provides powerful machine vision perception capabilities, supporting object detection, image segmentation, attribute description, angle prediction, keypoint detection, and grasp point prediction for 2D/3D images.

## Requirements

- Python 3.x
- Dependencies: requests>=2.26.0, python-dotenv>=0.19.0

## Installation

```bash
pip install py-qj-robots
```

## Configuration

The following environment variables need to be configured before using the SDK:

- QJ_APP_ID: Application ID
- QJ_APP_SECRET: Application Secret

You can click [here](https://qj-robots.feishu.cn/share/base/form/shrcnzmXqHZsyw5AKi6oIuCKf4J) to obtain your Application ID and Secret.

You can configure these variables in two ways:

1. Create a .env file:
```
QJ_APP_ID=your_app_id
QJ_APP_SECRET=your_app_secret
```

2. Using export command:
```bash
export QJ_APP_ID=your_app_id
export QJ_APP_SECRET=your_app_secret
```

## Quick Start

```python
from dotenv import load_dotenv
from py_qj_robots import Perception
import os

# Load environment variables
load_dotenv()

# Initialize Perception instance
perception = Perception()

# Perform 2D image detection
result = perception.check_image(
    image_type="2D",
    image_url="http://example.com/image.jpg",
    object_names=["bottle", "cup"]
)
print(f"Detection result: {result}")
```

## API Documentation

### Perception Class

#### check_image
Detect target objects in the image.

```python
def check_image(image_type: str, image_url: str, object_names: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict
```

Parameters:
- image_type: Image type, '2D' or '3D'
- image_url: Image URL
- object_names: Names of objects to detect, can be a string or list of strings
- depth_url: Depth image URL (required only when image_type is '3D')

#### split_image
Segment target objects in the image.

```python
def split_image(image_type: str, image_url: str, object_names: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict
```

Return value includes:
- boxes: Bounding box coordinates [x1,y1,x2,y2]
- masks: Mask image URLs and data
- croppedImagesListBbox: Cropped image URLs
- labels: Detected object labels
- scores: Confidence scores

#### props_describe
Get attribute descriptions of objects in the image.

```python
def props_describe(image_type: str, image_url: str, object_names: Union[str, List[str]], questions: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict
```

#### angle_prediction
Predict object angles.

```python
def angle_prediction(image_type: str, image_url: str, object_names: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict
```

#### key_point_prediction
Predict object keypoints.

```python
def key_point_prediction(image_type: str, image_url: str, object_names: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict
```

#### grab_point_prediction
Predict object grasp points.

```python
def grab_point_prediction(image_type: str, image_url: str, object_names: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict
```

#### full_perception
Perform complete perception analysis, including all features.

```python
def full_perception(image_type: str, image_url: str, object_names: Union[str, List[str]], questions: Union[str, List[str]], depth_url: Optional[str] = None) -> Dict
```

Return value includes all perception results:
- angles: Angle information
- boxes: Bounding boxes
- masks: Segmentation masks
- points: Keypoints
- grasps: Grasp points
- answers: Attribute descriptions
- etc.

## More Information

Visit [QJ Robots Official Website](https://www.qj-robots.com/) for more information.