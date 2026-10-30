# ローカル検証記録

検証日: 2026-10-30（Asia/Tokyo）

## 実行環境

WSL2 / Linux、Python 3.13.18、uv 0.13.6。標準Pythonが3.12だったため、Python 3.13を別途導入しました。依存の正確な版はuv.lockを参照してください。

## 結果

| 実行コマンド | 結果 |
|---|---|
| `uv sync --python 3.13` | 成功、uv.lock生成 |
| `.venv/bin/ruff check .` | 成功 |
| `.venv/bin/ruff format --check .` | 成功 |
| `.venv/bin/mypy app tests` | 成功（22ファイル） |
| `.venv/bin/pytest --cov=app --cov-report=term-missing --cov-report=xml` | 31件成功、98.79% |
| `.venv/bin/alembic upgrade head` | 成功 |
| `.venv/bin/alembic check` | 差分なし |
| `.venv/bin/alembic downgrade base` → `upgrade head` | 空DBへの巻き戻しと再適用に成功 |
| `.venv/bin/pip-audit -r requirements.txt` | 既知の脆弱性なし |
| `node --check app/static/js/app.js` | 成功 |
| `git diff --check` | 成功 |

pytestはAPI・入力境界・存在しないID・統計ルート・並び替え・期限切れ・完了切替・UTC出力・静的画面配信・DB保存・更新日時・削除・rollback・テスト間分離を検証します。

初回のサンドボックス内APIテストはTestClientで停止したため、制限外の実行環境で実行し直して成功を確認しました。
Starletteから、HTTPXベースのTestClientは将来非推奨となる旨の警告が1件あります。指定されたHTTPXでのテストは現在成功しています。将来の更新時に公式の移行方針を確認してください。

## 実ブラウザ

Playwright / Chromium、PC 1440px、スマートフォン相当390pxで確認しました。一時DB `/tmp/taskflow-browser.db` を使用し、本体のDBにサンプルタスクは入れていません。
ブラウザに必要な共有ライブラリと日本語フォントは検証用に一時展開しました。

- 初期の空状態
- 画面から3件の登録、編集、完了チェック
- 完了・未完了フィルター、優先順位順の並び替え
- 削除のキャンセルと確定
- ユーザーが入力したHTML断片がテキストとして表示され、画像要素が作られないこと
- API失敗時のエラー表示
- ブラウザのJavaScript例外がないこと
- 390pxで横方向のはみ出しがないこと

[PC画面](screenshots/desktop.png) / [スマートフォン画面](screenshots/mobile.png)

## 未検証・制約

- Dockerコマンドが「このWSLディストリビューションでは利用できない」と返しました。Docker DesktopのWSL Integration有効化後に `docker compose up --build` の実機検証が必要です。構成ファイルは作成済みで、CIにもコンテナ起動検証を用意しました。
- コードは [taka26taka/taskflow-fastapi](https://github.com/taka26taka/taskflow-fastapi) に公開済みです。GitHub Actionsの結果は [実行履歴](https://github.com/taka26taka/taskflow-fastapi/actions) を参照してください。ローカルでのDocker起動は上記の環境制約により未検証です。
- Cloudflare設定、実機スマートフォンでの操作、別ブラウザでの検証は行っていません。
- 認証はありません。外部公開前のAccessまたは認証・認可が必須です。
