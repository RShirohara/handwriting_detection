# HandWriting Detection

## Description

title: 「手書き文字認識による入力方式の開発」

Google Cloud Visionを使用して手書き文字を検出する。  
OpenCVで紙を、TensorFlowで手を検出し、紙の上に手が存在しない状態で紙を撮影する。  
文字が書かれていた場合、Vision OCR APIで文字を検出する。  
検出した文字をPCに送信し、音声読み上げも行う。  

### Demo

`ここにgifをいれる。`

## Working list

[GitHub Projects](https://github.com/RShirohara/handwriting_detection/projects/1)

## Features

- [ ] Hand Detection #1
- [ ] Paper Detection #2
- [ ] Character Detection #3
- [ ] Text to Speak #4
- [ ] Send Character #7

## Requirement

`Working`

- [jetson-utils](https://github.com/dusty-nv/jetson-utils)
- OpenCV 4.1.1 (installed on JetPack-4.4.1)
- [tensorflow 2.3.1+nv20.11](https://docs.nvidia.com/deeplearning/frameworks/install-tf-jetson-platform-release-notes/tf-jetson-rel.html)

## Usage

`Working`

## Installation

`Working`

## Author

- [瀬川龍哉(@RShirohara)](https://github.com/RShirohara)
- [小出樹(@itsukikoide)](https://github.com/itsukikoide)

## License

[The MIT License](./LICENSE)
