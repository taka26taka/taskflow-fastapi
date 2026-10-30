# 将来のCloudflare公開手順

現時点ではローカル専用です。この文書の作成に伴う契約・課金・DNS変更・トンネル作成は行っていません。

## 公開の条件

アプリに認証・認可を実装するか、Cloudflare Accessで到達を制限します。Tunnelは経路を作るだけで、認証の代わりにはなりません。最初から誰でもアクセスできるURLを作らないでください。

## 導入順序

1. Cloudflare管理のドメインと対象ホスト名を準備し、費用・利用プラン・現在の仕様を公式資料で確認します。
2. SQLiteのバックアップを用意し、公開機には本アプリ以外の秘密や不要なサービスを置かないようにします。
3. Zero TrustでAccessのSelf-hostedアプリを作り、対象ホスト名に本人のメールまたはIdPだけを許可するポリシーを設定します。Bypassや全員許可のルールを作らないよう確認します。
4. `cloudflared` のNamed Tunnelを作成し、対象ホスト名をローカルの `http://localhost:8000` へ結びます。cloudflaredを別コンテナに置くなら同じネットワークの `http://app:8000` を使います。トークンはGitやコマンド履歴に残さず、シークレットとして管理します。
5. ホストの8000番をインターネットに開けず、Tunnel経由だけにします。ルーターのポート転送も不要です。
6. HTTPS、DNS、Accessの対象を確認してから起動します。未ログイン・不許可ユーザーで `/`、`/api/tasks`、`/docs`、`/health` の全パスが拒否されること、許可ユーザーで利用できることを別ブラウザで確認します。
7. 利用プランで可能なWAF・Rate Limitingを検討し、APIの正常利用が遮断されないことを確認します。Accessとアプリ側認証の代替にはしません。
8. SQLiteの整合性ある定期バックアップ（SQLite backup APIなど）、更新・復元手順、ログ保存期間を設定します。利用後はAccessとTunnelを停止し、不要な資格情報を失効させます。

公開前にはCloudflareの最新の公式資料で設定・プランを再確認してください。

- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)
- [Access Self-hosted applications](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/)
- [WAF](https://developers.cloudflare.com/waf/)
- [Rate Limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/)
