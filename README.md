# videoop
python動画操作のお勉強

python3, 要 cv2(opencv), numpy

## タイムラプス

time-lapse.py

インターバル撮影された、複数の静止画像からタイムラプス動画を生成する。

```
usage: time-lapse.py [-h] [-o OUTPUT] [-w WIDTH] [-r FRAME_RATE] [-t TIMESTAMP] [--flash-adjust] files [files ...]

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
  --flash-adjust        フラッシュ使用時のフレームごとの光量のばらつきを均一化してちらつきを軽減する。
```

### 懸案事項
1. 入力画像フォーマット。現状jpgのみ。opencvで対応しているものなら...
2. デフォルト出力ファイル名。ディレクトリ指定の時、親ディレクトリに出力したほうがよい？
3. タイムスタンプ。現状ファイルのタイムスタンプを描画。EXIFから撮影日時を取得すべきでは？
4. タイムスタンプフォーマット。省略時タイムスタンプ描画しないほうが良いかも。

## 手振れ補正

anti-shake.py

動画の手振れを補正する。

```
usage: anti-shake.py [-h] [-o OUTPUT] [-w WIDTH] [-t TRACKING] [--select-roi] [-D] video

movie shake stabilize

positional arguments:
  video                 入力動画

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                       出力動画のファイル名。
                       省略したとき、入力ファイル名の拡張子の前に -a を挿入
  -w WIDTH, --width WIDTH
                        出力する動画の解像度を指定。
  --tracking TRACKING
                        位置補正範囲 画像サイズに対するパーセント指定
  --select-roi          動画の最初の一コマを表示してマウスでテンプレートを指定
  --DEBUG           デバッグ。
                    生成したテンプレート画像、相関値マップ、補正後画像(マッチ位置)をそれぞれ表示してキー待ち。
                    Ctrl-C, ESCで中断
                    s で、キー待ちを行うかをトグル
                    d デバッグモードを抜け、処理を継続
```

### 懸案事項
1. 処理速度
2. 画像によっては追従性に問題あり


## 動画編集

video-cut.py

時間指定によるカット、クロップなどの編集を行う。
音声は失われる。

```
usage: video-cut.py [-h] [-o OUTPUT] [-w WIDTH] [-l LENGTH] [-s START] [-e END] [-r FRAME_RATE]
                    [--rotate ROTATE] [--crop CROP] [--alpha ALPHA] [--beta BETA]
                    video

Edit the video. Change resolutioncut, out for specified time.

positional arguments:
  video                 入力動画

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        出力動画のファイル名。
                        省略したとき、入力ファイル名の拡張子の前に -cut を挿入
  -w WIDTH, --width WIDTH
                        出力する動画の解像度を指定。
                        省略したときは、入力画像と同じ
  -l LENGTH, --length LENGTH
                        出力動画の長さ [秒]
  -s START, --start START
                        入力動画の先頭から指定秒数をカット [秒]
  -e END, --end END      [秒]
  -r FRAME_RATE, --frame-rate FRAME_RATE
                        フレームレートを変更する。
  --crop CROP           座標を指定して切り出しを行う。 x,y,width,height
                        整数値 [画素]
                        小数 入力動画の縦横それぞれに対する比率で指定
                        %指定
  --rotate ROTATE       回転。角度を[度]で指定。
  --alpha ALPHA         各画素に指定係数をかける。
  --beta BETA           各画素にbetaを足す。
```
