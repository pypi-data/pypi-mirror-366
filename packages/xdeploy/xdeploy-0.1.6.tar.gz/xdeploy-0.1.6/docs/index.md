# xdeploy 项目

xdeploy 是一款视觉 AI 模型部署框架，支持目标检测、人脸识别、光学字符识别（OCR）和图像分割等任务。该项目提供了灵活的后端支持和模型接口，使您能够轻松部署各种深度学习模型。

## 支持的推理后端

- ONNX Runtime
- OpenVino
- TensorRT

## 安装

### 常规安装

```sh
uv add xdeploy
```

### 添加 TensorRT 支持

```sh
uv add "xdeploy[tensorrt]"
```

## 支持的算法

|  任务场景  |    模型     | 部署 | 训练文档 |
| :--------: | :---------: | :--: | :------: |
|  目标检测  |   YOLOv8    |  ✔️  |    -     |
|  目标检测  |   YOLOv10   |  ✔️  |    -     |
|  目标检测  |   YOLO11    |  ✔️  |    -     |
|  目标检测  |   RT-DETR   |  ✔️  |    -     |
|   旋转框   | YOLOv8-OBB  |  ✔️  |    -     |
|   旋转框   | YOLO11-OBB  |  ✔️  |    -     |
|  图像分类  | YOLOv8-CLS  |  ✔️  |    -     |
|  图像分类  | YOLO11-CLS  |  ✔️  |    -     |
|  实例分割  | YOLOv8-SEG  |  ✔️  |    -     |
|  实例分割  | YOLO11-SEG  |  ✔️  |    -     |
|   关键点   | YOLOv8-Pose |  ✔️  |    -     |
|   关键点   | YOLO11-Pose |  ✔️  |    -     |
|  图像分割  |  PaddleSeg  |  ✔️  |    -     |
|    OCR     |   PPOCRv4   |  ✔️  |    -     |
| 语音转文字 |      -      |  ❌  |    -     |
| 文字转语音 |      -      |  ❌  |    -     |
