from pathlib import Path

import numpy as np

from xdeploy.detection import RTDETR, YOLOv8, YOLOv10


def test_yolov8():
    model_path = "models/yolov8n.onnx"
    detector = YOLOv8(model_path=model_path)

    # Load test image
    image_path = "images/bus.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolov8.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0


def test_yolov10():
    model_path = "models/yolov10n.onnx"
    detector = YOLOv10(model_path=model_path)

    # Load test image
    image_path = "images/bus.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolov10.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0


def test_rtdetr():
    model_path = "models/rtdetr-l.onnx"
    detector = RTDETR(model_path=model_path)

    # Load test image
    image_path = "images/bus.jpg"

    # Predict
    result = detector.predict(image_path)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_rtdetr.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 0
