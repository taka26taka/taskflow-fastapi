# 設計

小規模な同期SQLAlchemyアプリです。リクエストごとのSessionをDependsで作り、終了時に閉じます。アプリ起動時にcreate_allは実行せず、スキーマの正はAlembicに置きます。

## 責務

- `api/routes/tasks.py`: HTTPの入出力とステータス。statsをIDルートより先に宣言。
- `schemas/task.py`: 作成・部分更新・レスポンスの型、余分な項目・空白タイトル・不正値の拒否。
- `services/task_service.py`: 対象確認、作成・更新・削除の単位でcommit。例外時rollback。
- `repositories/task_repository.py`: SQLの構築と集計。commitしない。
- `models/task.py`: SQLAlchemyの型付き列、DB制約、UTC時刻、期限判定。

ServiceはHTTP例外に依存せず `TaskNotFound` を送出します。main.pyが404へ変換します。その他の予期しない例外は汎用500を返します。
読み取りのトランザクションはSessionのclose時に解放します。書き込みではcommit完了後の値をrefreshして返します。SQLiteは個人利用向けであり、多数の同時更新は想定していません。

## 日時

SQLiteのDATETIMEにはタイムゾーンがないため、UTCに統一したnaive datetimeを保存します。API出力時にUTCを付与します。updated_atはORMのonupdateで更新します。空PATCHや同値の更新ではSQL UPDATEが発生せず、更新日時は変わりません。
期限はDATE。`due_date < 日本時間の今日` かつ未完了が期限切れです。日付の変更に合わせて次回API取得で再計算します。

## 選択したトレードオフ

同期DB処理には同期のルート関数を使い、FastAPIのスレッドプールへ任せます。不要なasync化、汎用Repository基底、独自DIコンテナは追加していません。
初期版は全件取得です。データ量が増えたらページネーション・索引・必要に応じたPostgreSQL移行を検討します。

## テスト

HTTPXベースのTestClientで公開APIを検証します。各テストが独立したtmp_path内のSQLiteを持ち、get_sessionを置き換えます。サービスでは保存・更新時刻・削除・DB制約失敗後のrollback・commit失敗時の削除rollbackを検証します。

参考: [FastAPIのDBとDI](https://fastapi.tiangolo.com/tutorial/sql-databases/)、[SQLAlchemyのSessionとトランザクション](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)。
