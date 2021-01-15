# セットアップ時のやること一覧

## bluetooth

標準では動かない。
ひと工夫が必要。

### 1.usermodを使う(安全)

bluetoothでaudioを使うためにはlpグループに所属している必要がある。

```bash
usermod -aG lp $USER
```

で追加 -> 再起動。

### 2.dbus設定を書き換える(危険?)

参考: https://www.linuxquestions.org/questions/slackware-14/bluetooth-not-working-except-for-root-4175602872/page3.html
`/etc/dbus-1/system.d/bluetooth.conf`の

```conf Before
  <policy at_console="true">
    <allow send_destination="org.bluez"/>
  </policy>
```
を
```conf After
  <policy at_console="false">
    <allow send_destination="org.bluez"/>
  </policy>
```
に書き換える。

## pulseaudio

systemdで自動起動させる。

https://gist.github.com/kafene/32a07cac0373409e31f5bfe981eefb19

## Python絡み

### TensorFlow

