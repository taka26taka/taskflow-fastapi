# CakePHP経験者向け Python / FastAPI

| PHP・CakePHP | 本プロジェクト | 役割 |
|---|---|---|
| Controller | `app/api/routes/tasks.py` のAPIRouter | HTTPの入力・出力 |
| Model / Table | `app/models/task.py` のTask | ORMのマッピング。クエリはRepository |
| Validation | `app/schemas/task.py` のPydantic | 型・長さ・必須項目の検証 |
| Serviceクラス | `app/services/task_service.py` | 更新とトランザクション |
| Dependency Injection | `app/api/dependencies.py` のDepends | リクエスト単位のSession注入 |
| PHPUnit | `tests/` のpytest | assertとfixtureによるテスト |
| Composer | pyproject.toml / uv.lock / uv | 依存宣言・固定・導入 |
| Migration | alembic/versions | DBスキーマの履歴 |

## 文法・型ヒント

PHPの `$title` はPythonでは `title`、`null` は `None`、`true` は `True` です。ブロックは波括弧ではなくインデントで表します。文字列の連結には `+`、埋め込みには `f"{task_id}"` を使います。`->` でのメンバー参照は `.`、`$this` は明示的な `self` になります。

```python
# app/services/task_service.py の構造
class TaskService:
    def __init__(self, session: Session) -> None:
        self.session = session
```

`Task | None` はTaskまたはNoneを意味します。`list[Task]` はTaskのリストです。型ヒント自体は実行時の強制ではなく、mypyが静的にチェックします。HTTP入力はPydanticが実行時にも検証します。
`Mapped[str]` はSQLAlchemyの文字列属性、`Priority(StrEnum)` は許可した優先度の列挙です。

## Pydanticと部分更新

`TaskCreate` はtitle必須。`TaskUpdate` は省略を許し、`model_dump(exclude_unset=True)` で送られた項目だけを更新します。`None` が送られた場合は省略とは異なり、期限だけ解除します。CakePHPのEntityへの一括代入と同様に、更新可能なフィールドを明示することが大切です。

## Dependsとセッション

`get_service` が `Depends(get_session)` を宣言すると、FastAPIがSessionを注入します。`get_session` のyield前でSessionを用意し、リクエストが終わるとwithブロックを抜けてcloseします。
SQLAlchemyのSessionはDB接続そのものではなく、ORMオブジェクトとトランザクションの作業単位です。Repositoryはクエリ、Serviceはcommit/rollbackの責務を持ちます。テストでは `app.dependency_overrides` で一時DBを注入します。

## 例外処理

PHPのtry/catchはPythonではtry/exceptです。`raise` はthrowに相当します。

```python
try:
    self.session.commit()
except Exception:
    self.session.rollback()
    raise
```

失敗時にrollbackしてから元の例外を再送出します。存在しないタスクは `TaskNotFound` を送出し、共通ハンドラーで404に変換します。内部エラーの詳細はクライアントに出しません。

## async / await

asyncは主にI/O待ちの間に別の処理へ進む仕組みです。同期関数にasyncを付けるだけでは非同期になりません。このアプリは同期SQLAlchemyを採用し、ルートも通常のdefでFastAPIのスレッドプールに任せています。ブラウザは `await fetch(...)` でAPI応答を待ちます。FastAPIの例外ハンドラーやミドルウェアはフレームワークの非同期インターフェースに合わせています。

## 最初に読む順番

1. schemas/task.py: API入力と型
2. api/routes/tasks.py: URLと処理の対応
3. api/dependencies.py: Sessionの受け渡し
4. services/task_service.py: 更新とトランザクション
5. models/task.py と repositories/task_repository.py: 保存と検索
6. tests/test_tasks_api.py と conftest.py: 自動検証とテストDB

## 公式資料

- [Pythonチュートリアル](https://docs.python.org/ja/3.13/tutorial/)
- [型ヒント](https://docs.python.org/ja/3.13/library/typing.html)
- [例外](https://docs.python.org/ja/3.13/tutorial/errors.html)
- [FastAPI: Pythonの型](https://fastapi.tiangolo.com/python-types/)
- [FastAPI: Depends](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI: asyncの考え方](https://fastapi.tiangolo.com/async/)
- [SQLAlchemy: Session](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
