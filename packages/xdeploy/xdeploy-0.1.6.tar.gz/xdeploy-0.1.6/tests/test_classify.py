from pathlib import Path

import numpy as np

from xdeploy.classification import YOLOv8CLS


def test_yolov8_cls():
    model_path = "models/yolov8n-cls.onnx"
    detector = YOLOv8CLS(model_path=model_path)

    # Load test image
    image_path = "images/bus.jpg"

    # Predict
    result = detector.predict(image_path, topk=5)

    # Draw result
    save_path = image_path.replace("images", "results")
    save_path = save_path.replace(".jpg", "_yolov8_cls.jpg")
    image = result.draw(save_path=save_path)

    # Check result
    assert len(result) > 0
    assert Path(save_path).exists()

    # Load empty image
    empty_image = np.ones_like(image) * 114
    result = detector.predict(empty_image)
    # Check result
    assert len(result) == 1
