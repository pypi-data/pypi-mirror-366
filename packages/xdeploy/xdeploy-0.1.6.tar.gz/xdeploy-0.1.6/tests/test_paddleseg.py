import numpy as np

from xdeploy.segmentation.semantic import PaddleSeg

rng = np.random.default_rng(1337)


def test_predict():
    model_path = "path/to/model"
    paddleseg = PaddleSeg(model_path=model_path)

    # Test with single image
    image = rng.integers(0, 255, size=(512, 512, 3), dtype=np.uint8)
    result = paddleseg.predict(image)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 2, 512, 512)

    # Test with multiple images
    images = [rng.integers(0, 255, size=(512, 512, 3), dtype=np.uint8) for _ in range(3)]
    result = paddleseg.predict(images)
    assert isinstance(result, np.ndarray)
    assert result.shape == (3, 2, 512, 512)


def test_preprocess():
    model_path = "path/to/model"
    paddleseg = PaddleSeg(model_path=model_path)

    # Test with single image
    image = rng.integers(0, 255, size=(1024, 1024, 3), dtype=np.uint8)
    result = paddleseg.preprocess(image)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 3, 512, 512)

    # Test with multiple images
    images = [rng.integers(0, 255, size=(1024, 1024, 3), dtype=np.uint8) for _ in range(3)]
    result = paddleseg.preprocess(images)
    assert isinstance(result, np.ndarray)
    assert result.shape == (3, 3, 512, 512)
