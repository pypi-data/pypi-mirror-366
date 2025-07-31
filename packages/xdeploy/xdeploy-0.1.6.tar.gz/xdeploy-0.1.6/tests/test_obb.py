from pathlib import Path

import numpy as np

from xdeploy.obb import YOLO11OBB, YOLOv8OBB


def test_yolov8_obb():
    model_path = "models/yolov8n-obb.onnx"
    detector = YOLOv8OBB(model_path=model_path)

    # Load test image
    image_path = "images/demo_obb.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolov8_obb.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0


def test_yolo11_obb():
    model_path = "models/yolo11n-obb.onnx"
    detector = YOLO11OBB(model_path=model_path)

    # Load test image
    image_path = "images/demo_obb.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolo11_obb.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0
