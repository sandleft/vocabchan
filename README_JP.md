# VocabChan 📸

[English](./README.md) · [中文](./README_CN.md) · [日本語](./README_JP.md)

> ホットキーを押すだけ。AIが解析して、Ankiに自動保存。それだけ。

> ⚠️ **Windows版EXEは現在ベータテスト中です。バグが出る可能性があるため、今はPythonソースからの実行を推奨します。**

---

## これは何？

VocabChanは「見ながら学ぶ」人のための語学学習ツールです。

アニメ、ドラマ、ゲーム、YouTubeを見ていて、わからない表現が出てきたらホットキーを一つ押すだけ。スクリーンショット（またはマイク録音、クリップボードのテキスト）を自動でAIに送り、文法解説・単語の意味・発音メモ・使用場面まで全部まとめて返してくれます。そのままAnkiのカードとObsidianのノートに自動保存。ウィンドウを切り替える必要も、コピペする必要もありません。そのまま見続けてください。

---

## できること

- **スクリーンショット解析** — 画面をキャプチャしてAIに解説してもらう
- **音声キャプチャ** — マイクまたはシステム音声を録音して自動文字起こし＋解析
- **OBSビデオリプレイ** — OBSの直近N秒の映像を取得してAIに解析させる
- **クリップボードモード** — テキストをコピーしてワンキーで解析
- **バッチインポート** — 単語リストをまとめて貼り付けて一括処理
- **Anki同期** — 単語・原文・解析内容を含むフラッシュカードを自動生成
- **Obsidian同期** — 記録をすべて構造化ノートとして自動保存
- **間隔反復リマインダー** — 3日・7日・14日前の単語を自動で復習通知
- **単語検索・学習統計** — 過去の記録を検索、学習データの確認、CSV/TXTエクスポート
- **ホットキーで言語切り替え** — 日本語・英語などのテンプレートをいつでも切り替え

### 対応AIプロバイダー
Google Gemini · OpenAI · Claude · DeepSeek · Grok · Qwen · Kimi · Doubao · MiniMax · OpenRouter

### 対応言語
日本語 · 英語 · 中国語 · スペイン語 · フランス語 · ドイツ語 · 韓国語 · イタリア語 · ポルトガル語 · アラビア語 · カスタムテンプレートで追加可能

---

## 使い方

### 必要なもの
- Python 3.10以上
- [Anki](https://apps.ankiweb.net/) + [AnkiConnectプラグイン](https://ankiweb.net/shared/info/2055492159)
- [Obsidian](https://obsidian.md/)
- 上記プロバイダーのうち少なくとも1つのAPIキー
- OBS Studio（ビデオ機能を使う場合のみ）
- 任意：[Faster-Whisper](https://github.com/guillaumekuhn/faster-whisper)（ローカル音声文字起こし）
- 任意：PaddleOCR（ローカルOCR）

### インストール

```bash
git clone https://github.com/あなたのユーザー名/vocabchan
cd vocabchan
pip install -r requirements.txt
```

### 設定

`config.py` を開いて、使いたいAPIキーとパスを入力します：

```python
# 使うプロバイダーのAPIキーを入力
API_KEYS = {
    "google": "your-key-here",
    "openai": "your-key-here",
    # ...
}

# OBS設定（ビデオ機能を使う場合のみ）
OBS_WS_HOST     = "127.0.0.1"
OBS_WS_PASSWORD = "your-obs-password"
OBS_WATCH_DIR   = r"C:/your/obs/recording/path"
```

他の設定はデフォルト値のままで始められます。

### 起動

```bash
python main.py
```

設定UIが自動で開きます。ホットキーの監視はバックグラウンドで同時に起動します。

---

## ホットキー一覧

| キー | 機能 |
|------|------|
| F4 | スクリーンショット＋録音、高速解析 |
| F6 | スクリーンショット＋録音、深度解析 |
| F2 | クリップボードテキスト解析 |
| F7 | 押している間OBS録画 |
| F12 | OBSリプレイバッファ（直近N秒） |
| F8 / F9 | スクリーンショットのみ解析 |
| Alt+Z / X / C | 言語テンプレート切り替え |
| Alt+S | 保存済み単語を検索 |
| Alt+Q | 学習統計を表示 |
| Alt+E | 単語をCSVにエクスポート |
| Alt+W | 単語をTXTにエクスポート |
| Alt+B | クリップボードから一括インポート |
| Alt+R | キャプチャ範囲を選択 |

すべてのホットキーは `config.py` で変更できます。

---

## 注意事項

- APIキーはローカルの `config.py` にのみ保存されます。外部に送信されることはありません
- Ankiの同期にはAnkiが起動中で、AnkiConnectプラグインが有効になっている必要があります
- OBS機能を使うにはOBSの設定でWebSocketサービスを有効にしてください
- ローカルWhisperやOCRを初めて有効にすると、モデルのダウンロードに時間がかかります
- キャプチャした画像や音声は設定したAssetsフォルダに保存され、自動削除はされません

---

## ライセンス

MIT
