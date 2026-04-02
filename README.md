# video2txt

將本地視頻或音頻文件轉寫為 SRT / ASS 字幕文件和 TXT 純文本文件，並透過 AI 自動修正語音辨識錯誤。

## 功能

- 使用 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 進行語音辨識
- 輸出 SRT、ASS（黑字白描邊）、TXT 三種格式
- 支援多種視頻格式（mp4、mkv、mov、avi、flv、wmv、webm、m4v）及音頻格式（mp3、wav、m4a、aac、flac、ogg）
- 中文辨識自動轉換為繁體中文（透過 OpenCC）
- AI 輔助修正同音字誤判、專有名詞錯誤、斷詞錯誤等常見語音辨識問題

## 安裝

**環境需求：** Python 3.11 或 3.12

```bash
pip install -r requirements.txt
```

依賴套件：
- `faster-whisper` >= 1.1.0
- `av` >= 12.0.0
- `opencc-python-reimplemented` >= 0.1.7

另需系統安裝 ffmpeg / ffprobe（用於取得媒體時長）。首次執行時會自動下載 Whisper 模型。

## 使用方式

### 第一階段：生成字幕

```bash
python scripts/video_to_text.py --input <視頻或音頻檔案路徑>
```

執行後會在輸入檔案的同目錄下產生：

| 檔案 | 說明 |
|------|------|
| `<檔名>.srt` | SRT 字幕檔 |
| `<檔名>.ass` | ASS 字幕檔 |
| `<檔名>.txt` | 純文字逐字稿 |

### 第二階段：AI 語音辨識修正

1. 審閱生成的 `.txt` 檔案，找出語音辨識錯誤
2. 將修正對照寫入 `corrections.json`：
   ```json
   [
     {"old": "危機分", "new": "微積分"},
     {"old": "飛胞裏溝通", "new": "非暴力溝通"}
   ]
   ```
3. 執行修正腳本：
   ```bash
   python scripts/fix_subtitles.py --corrections corrections.json --srt <srt路徑> --ass <ass路徑>
   ```

## 參數說明

### video_to_text.py

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--input` | 輸入檔案路徑（必填） | — |
| `--output-dir` | 輸出目錄 | 輸入檔案所在目錄 |
| `--output-path` | 輸出檔案基礎路徑 | — |
| `--model-dir` | 模型下載目錄 | `scripts/models` |
| `--model-size` | Whisper 模型大小 | `base` |
| `--language` | 辨識語言（auto / zh / en） | `zh` |
| `--device` | 推論設備（cpu / cuda） | `cpu` |
| `--compute-type` | 計算類型 | `int8` |
| `--beam-size` | 解碼 beam 大小（1–5） | `2` |
| `--no-vad-filter` | 停用 VAD 過濾 | 未啟用 |

### fix_subtitles.py

| 參數 | 說明 |
|------|------|
| `--corrections` | 修正對照表 JSON 檔案路徑（必填） |
| `--srt` | 要修正的 SRT 檔案路徑 |
| `--ass` | 要修正的 ASS 檔案路徑 |

至少需提供 `--srt` 或 `--ass` 其中之一。

## 注意事項

- 首次執行需下載 Whisper 模型，視網路狀況可能需要數分鐘
- 建議使用 Python 3.11 或 3.12 以避免 faster-whisper 相容性問題
- Whisper 對中文辨識常有同音字錯誤，建議務必執行第二階段的 AI 修正
