---
name: video2txt
description: 將本地視頻或音頻文件轉寫為 SRT/ASS 字幕文件和 TXT 純文本文件，並自動進行語音辨識修正
metadata: { "openclaw": { "emoji": "video", "requires": { "bins": ["python3"] } } }
---

# video2txt 技能

## 描述

將本地視頻或音頻文件轉寫為 SRT 字幕文件、ASS 字幕文件和 TXT 純文本文件，並由 Claude AI 自動審閱修正語音辨識錯誤。

## 功能

- 提取視頻/音頻中的語音內容
- 生成帶時間戳的 SRT 字幕文件
- 生成帶時間戳的 ASS 字幕文件（黑色字體、白色描邊）
- 生成純文本 TXT 文件
- 支持多種視頻和音頻格式
- 默認使用中文識別，自動轉換為繁體中文
- **AI 語音辨識修正**：自動檢測並修正同音字誤判、專有名詞錯誤、斷詞錯誤等

## 完整流程

使用此技能時，請依序執行以下兩個階段：

### 第一階段：生成字幕

```bash
python video_to_text.py --input <視頻/音頻文件路徑>
```

- **後台執行**：調用此腳本時，務必使用 `background: true` 參數
- 腳本會輸出三個文件：`.srt`、`.ass`、`.txt`

### 第二階段：AI 語音辨識修正

字幕生成完成後，**必須**執行以下修正流程：

1. **讀取 .txt 文件**：使用 Read 工具讀取生成的純文本文件全部內容

2. **審閱並標記錯誤**：逐段檢查文字，找出以下類型的語音辨識錯誤：
   - **同音字誤判**：如「書→樹」「賺→正」「續費→蓄廢」「噪聲→造生」
   - **專有名詞錯誤**：如「EMBA→NBA」「愛因斯坦→安姨斯坦」「居里夫人→距離夫人」
   - **斷詞錯誤**：如「微積分→危機分」「非暴力溝通→飛胞裏溝通」「暢銷書→唱銷出」
   - **嚴重語意偏差**：如「過程當中→共產黨中」「大猩猩→大清醒」
   - **台灣用語/地名/食物**：如「蚵仔煎→歐阿娟」「蔡瀾→蔡蘭」

3. **生成修正 JSON 文件**：將所有修正寫入 `corrections.json`，存放在與字幕相同的目錄下
   ```json
   [
     {"old": "原始錯誤文字", "new": "修正後文字"},
     {"old": "危機分", "new": "微積分"},
     {"old": "飛胞裏溝通", "new": "非暴力溝通"}
   ]
   ```

4. **執行修正腳本**：
   ```bash
   python fix_subtitles.py --corrections <corrections.json路徑> --srt <srt路徑> --ass <ass路徑>
   ```

### 完整示例

```bash
# 第一階段：生成字幕（後台執行）
python video_to_text.py --input "D:\videos\meeting.mp4"

# 第二階段：Claude 讀取 txt → 審閱 → 生成 corrections.json → 執行修正
python fix_subtitles.py --corrections "D:\videos\corrections.json" --srt "D:\videos\meeting.srt" --ass "D:\videos\meeting.ass"
```

## 參數說明

### video_to_text.py

| 參數 | 說明 | 默認值 |
|------|------|--------|
| `--input` | 輸入文件路徑（必需） | - |
| `--output-dir` | 輸出目錄 | 輸入文件目錄 |
| `--output-path` | 輸出文件基礎路徑 | - |
| `--model-dir` | 模型下載目錄 | 當前目錄/models |
| `--model-size` | Whisper 模型大小 | base |
| `--language` | 識別語言 (auto/zh/en) | zh |
| `--device` | 推理設備 (cpu/cuda) | cpu |
| `--compute-type` | 計算類型 | int8 |
| `--beam-size` | 解碼束大小 (1-5) | 2 |
| `--no-vad-filter` | 禁用 VAD 過濾 | false |

### fix_subtitles.py

| 參數 | 說明 | 默認值 |
|------|------|--------|
| `--corrections` | 修正對照表 JSON 文件路徑（必需） | - |
| `--srt` | 要修正的 SRT 文件路徑 | - |
| `--ass` | 要修正的 ASS 文件路徑 | - |

## 依賴

- faster-whisper >= 1.1.0
- av >= 12.0.0
- opencc-python-reimplemented >= 0.1.7
- ffprobe/ffmpeg
- Whisper 模型文件（首次運行自動下載）

## 安裝

1. 確保 Python 3.11 或 3.12 環境
2. 安裝依賴：`python -m pip install -r requirements.txt`
3. 首次運行會自動下載 Whisper 模型到 models 目錄

## 輸出文件

- `<輸入文件名>.srt` - 帶時間戳的 SRT 字幕文件
- `<輸入文件名>.ass` - 帶時間戳的 ASS 字幕文件
- `<輸入文件名>.txt` - 純文本文件
- `corrections.json` - 語音辨識修正對照表（修正階段生成）

## 注意事項

- 首次運行需要下載 Whisper 模型，可能需要幾分鐘時間
- 建議使用 Python 3.11 或 3.12，避免與 faster-whisper 的兼容性問題
- 中文識別會自動轉換為繁體中文
- 為了減少用戶等待焦慮，每間隔10秒左右報告一次處理進度
- beam-size 默認為 2，如需調整可手動指定 --beam-size 參數
- **語音辨識修正是必要步驟**，Whisper 對中文的辨識經常有同音字錯誤，修正可大幅提升字幕品質
