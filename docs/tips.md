# 使用時設定等

Linux特有の操作法などは記述しない。  

## bluetooth

JetPack標準では動かない。  
ひと工夫が必要。  

### 1.usermodを使う(安全)

bluetoothでaudio出力を使うためには`$USER`が`lp`グループに所属している必要がある。  

```bash
$ usermod -aG lp $USER
```

で追加 -> 再起動。

### 2.dbus設定を書き換える(非推奨)

参考: https://www.linuxquestions.org/questions/slackware-14/bluetooth-not-working-except-for-root-4175602872/page3.html

`/etc/dbus-1/system.d/bluetooth.conf`の

```conf
  <policy at_console="true">
    <allow send_destination="org.bluez"/>
  </policy>
```

を

```conf
  <policy at_console="false">
    <allow send_destination="org.bluez"/>
  </policy>
```

に書き換える。

## pulseaudio

systemdで自動起動させる。

https://gist.github.com/kafene/32a07cac0373409e31f5bfe981eefb19

## Python

手の検出にTensorFlow Object Detection APIを使用する。  

### Pyenv

JetsonNano標準のPythonは3.6.9。  
3.6.12をインストールするために使用。  

https://github.com/pyenv/pyenv

### Poetry

依存パッケージ管理ツール。  
`./pyproject.toml`に設定が書いてある。  

https://github.com/python-poetry/poetry

### TensorFlow

Pythonバージョンに対応したものを入れる。  
poetryによって自動で入る。  
