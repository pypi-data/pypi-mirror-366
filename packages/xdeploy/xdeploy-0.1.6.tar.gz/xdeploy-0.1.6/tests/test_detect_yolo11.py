from pathlib import Path

import numpy as np

from xdeploy.detection import YOLO11
from xdeploy.results import DetectionResult


def test_yolo11():
    model_path = "models/yolo11n.onnx"
    detector = YOLO11(model_path=model_path)

    # Load test image
    image_path = "images/bus.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolo11.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0


def test_yolo11_batch():
    model_path = "models/yolo11n-b2.onnx"
    detector = YOLO11(model_path=model_path)

    # Load test image
    image_path = ["images/bus.jpg", "images/zidane.jpg"]
    save_path = ["results/bus_yolo11.jpg", "results/zidane_yolo11.jpg"]

    # Predict
    result = detector.predict(image_path)
    # Check result
    assert len(result) == 2

    for i, res in enumerate(result):
        res.draw(save_path=save_path[i])

    # 测试一张图像
    image_path = "images/bus.jpg"
    save_path = "results/bus_yolo11.jpg"
    result = detector.predict(image_path)
    assert isinstance(result, DetectionResult)
