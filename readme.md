# HandWriting Detection

## Description

岩手県立産業技術短期大学校 電子技術科  
2020年度卒業研究「手書き文字認識による入力方式の開発」  

Google Cloud Visionを使用して手書き文字を検出する。  
OpenCVで紙を、TensorFlowで手を検出し、紙の上に手が存在しない状態で紙を撮影する。  
文字が書かれていた場合、Vision OCR APIで文字を検出する。  
検出した文字をPCに送信し、音声読み上げも行う。  

### Demo

`ここにgifをいれる。`

## Working list

[GitHub Projects](https://github.com/RShirohara/handwriting_detection/projects/1)

## Features

- [x] Hand Detection [#1](https://github.com/RShirohara/handwriting_detection/issues/1)
- [x] Paper Detection [#2](https://github.com/RShirohara/handwriting_detection/issues/2)
- [x] Character Detection [#3](https://github.com/RShirohara/handwriting_detection/issues/3)
- [x] Text to Speak [#4](https://github.com/RShirohara/handwriting_detection/issues/4)
- [ ] Send Character [#7](https://github.com/RShirohara/handwriting_detection/issues/7)

## Requirement

- Python 3.6.12

### Python Modules

- opencv-python 4.4.0
- [TensorFlow 1.15.4+nv20.12](https://docs.nvidia.com/deeplearning/frameworks/install-tf-jetson-platform-release-notes/tf-jetson-rel.html)
- [TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection)
- pydub

## Usage

command: `tegaki [-h] [-i INPUT] [-m MAX_SIZE] [-g GOOGLE_CREDS] model`

- poritional:
  - `model`               訓練済みモデルが存在するディレクトリのパス。
- optional:
  - `-h, --help`          Show help.
  - `-i, --input`         入力デバイスのパス。
  - `-m, --max_size`      tasklistの上限値。
  - `-g, --google_creds`  Google Cloud サービスアカウントキーのパス。

## Installation

### Requiment

```bash
$ sudo apt update && sudo apt upgrade
$ sudo apt install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran libffi-dev openssl-dev protobuf-compiler libxslt1-dev
$ pip install poetry
```

### From source

```bash
$ git clone https://github.com/RShirohara/handwriting_detection
$ cd handwriting_detection
$ poetry install
```

Detail(詳細): [docs/install.md](./docs/install.md)

## Author

- [瀬川龍哉(@RShirohara)](https://github.com/RShirohara)
- [小出樹(@itsukikoide)](https://github.com/itsukikoide)

## License

[The MIT License](./LICENSE)
