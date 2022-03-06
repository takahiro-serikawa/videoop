# videoop
python動画操作のお勉強

python3, 要 cv2(opencv), numpy

## タイムラプス

time-lapse.py

複数の静止画像からタイムラプス動画を生成する。

```
usage: time-lapse.py [-h] [-o OUTPUT] [-w WIDTH] [-r FRAME_RATE] [-t TIMESTAMP] files [files ...]

make time-lapse video from image files

positional arguments:
  files                 入力画像、または入力画像が含まれたディレクトリを指定。複数指定可能。
                        ディレクトリが指定されたとき、拡張子 .jpg のものをサブディレクトリを含めて走査しファイル名でソート

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        出力動画のファイル名。
                        省略したとき、先頭の入力ファイルの拡張子を .mov に置き換えたファイル名に出力する。
  -w WIDTH, --width WIDTH
                        出力する動画の解像度を指定。
                        省略したときは、入力画像と同じ
  -r FRAME_RATE, --frame-rate FRAME_RATE
                        出力する動画のフレームレートを指定。  
                        省略したとき 30fps
  -t TIMESTAMP, --timestamp TIMESTAMP
                        動画右下にタイムスタンプを描画するときのフォーマット指定。
                        省略時 yyyy-mm-dd hh:mm AM/PM
                        タイムスタンプを描画したくないときは -t ' ' などとする。
```

### 懸案事項
1. 入力画像フォーマット。現状jpgのみ。opencvで対応しているものなら...
2. デフォルト出力ファイル名。ディレクトリ指定の時、親ディレクトリに出力したほうがよい？
3. タイムスタンプ。現状ファイルのタイムスタンプを描画。EXIFから撮影日時を取得すべきでは？
4. タイムスタンプフォーマット。省略時タイムスタンプ描画しないほうが良いかも。

