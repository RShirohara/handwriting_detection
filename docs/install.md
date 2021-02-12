# Installation

On Jetpack 4.4.1.

## Requires and Dependencies

Includes `tensorflow` and `object-detection` dependency.

### System Packages

```bash
$ sudo apt update && sudo apt upgrade
$ sudo apt install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran libffi-dev openssl-dev protobuf-compiler libxslt1-dev
```

### Python Packages

- poetry

  ```bash
  $ pip3 install poetry
  ```

ほとんどのパッケージ依存はPoetryによって自動解決される。

- cython
- numpy == 1.18.5
- future == 0.18.2
- mock == 3.0.5
- h5py == 2.10.0
- Keras-Preprocessing == 1.1.1
- Keras-Applications == 1.0.8
- scipy == 1.4.1
- gast == 0.2.2
- pillow == 8.1.0
- kiwisolver == 1.3.1
- pycocotools
- tensorflow == [1.15.4+nv20.12](https://developer.download.nvidia.com/compute/redist/jp/v44/tensorflow/tensorflow-1.15.4+nv20.12-cp36-cp36m-linux_aarch64.whl)
- [object-detection](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf1.md)
- google-cloud-vision
- google-cloud-texttospeech
- pydub

#### object-detection

`wheels`以下に`object-detection-0.1-py3-none-any-whl`がない場合。

[tensorflow/models](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf1.md)

```bash
$ git clone https://github.com/tensorflow/models
$ cd models/research
# Compile protos.
$ protoc object_detection/protos/*.proto --python_out=.
$ cp object_detection/packages/tf1/setup.py .
$ python3 setup.py sdist bdist_wheel
$ cp dist/object_detection-0.1-py3-none-any.whl ../../handwriting_detection/wheels/
```

## By poetry

```bash
$ git clone https://github.com/RShirohara/handwriting_detection
$ cd handwriting_detection
$ poetry install
```
