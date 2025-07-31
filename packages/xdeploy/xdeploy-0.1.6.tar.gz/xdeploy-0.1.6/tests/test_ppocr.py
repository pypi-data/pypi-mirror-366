from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from xdeploy.ocr import PPOCRv4
from xdeploy.results import OCRResult


@pytest.fixture(scope="module")
def ocr_net():
    det_model = "models/ch_PP-OCRv4_det_infer.onnx"
    rec_model = "models/ch_PP-OCRv4_rec_infer.onnx"
    return PPOCRv4(det_model, rec_model)


@pytest.fixture(scope="module")
def test_image():
    image_path = "images/text_det.jpg"
    return np.array(Image.open(image_path))


@pytest.fixture(scope="module")
def test_image_path():
    return "images/text_det.jpg"


def test_load_model(ocr_net: PPOCRv4):
    assert ocr_net.det_net is not None
    assert ocr_net.rec_net is not None


def test_predict_array(ocr_net: PPOCRv4, test_image: np.ndarray):
    result = ocr_net.predict(test_image)
    save_path = "results/ppocr_pipeline_1.jpg"
    result.draw(save_path=save_path)

    assert isinstance(result, OCRResult)
    assert len(result) > 0
    assert Path(save_path).exists()


def test_predict_path(ocr_net: PPOCRv4, test_image_path: str):
    result = ocr_net.predict(test_image_path)
    save_path = "results/ppocr_pipeline_2.jpg"
    result.draw(save_path=save_path)

    assert isinstance(result, OCRResult)
    assert len(result) > 0
    assert Path(save_path).exists()


def test_empty_image(ocr_net: PPOCRv4, test_image: np.ndarray):
    empty_image = np.zeros_like(test_image)
    result = ocr_net.predict(empty_image)

    assert isinstance(result, OCRResult)
    assert len(result) == 0
