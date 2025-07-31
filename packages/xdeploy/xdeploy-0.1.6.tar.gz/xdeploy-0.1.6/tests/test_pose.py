from pathlib import Path

import numpy as np

from xdeploy.pose import YOLO11Pose, YOLOv8Pose


def test_yolov8():
    model_path = "models/yolov8n-pose.onnx"
    detector = YOLOv8Pose(model_path=model_path)

    # Load test image
    image_path = "images/bus.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolov8_pose.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0


def test_yolo11():
    model_path = "models/yolo11n-pose.onnx"
    detector = YOLO11Pose(model_path=model_path)

    # Load test image
    image_path = "images/bus.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolo11_pose.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0
