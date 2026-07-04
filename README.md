# serverless-dab-cicd — GitHub Actions で DAB 昇格（サーバーレス / direct エンジン）

このディレクトリの中身が**そのまま新規 repo `takuya-amakawa/serverless-dab-cicd` になる**雛形。
`PR → validate` ／ `main → staging deploy+run` ／ `承認 → prod deploy+run` を GitHub Actions で回す。
**機密（catalog 名 / SP appId / host / secret）はリポジトリに一切置かず**、GitHub Environments の
Secrets から CI 実行時に注入する（＝public でもコードのみ）。認証は SP OAuth secret で M2M。

> 在-Databricks 版（web ターミナル/SP 実行ジョブ）は本テーマ `scripts/60_cicd_job/` 参照。
> こちらはランナー（ネット有）で CLI を導入する **Git 連携版**。手順は ADO へも移植可能。

## レイアウト
```
databricks.yml               # bundle(engine:direct)+targets(staging/prod)。catalog/run_as_sp は値なし＝CI が --var 注入
resources/*.job.yml          # ingest(notebook)/transform(python)/orchestrator(run_job) すべてサーバーレス
src/*.py                     # ジョブが参照するノートブック/スクリプト
.github/workflows/deploy.yml # PR=validate / main=stg deploy+run / 承認=prod deploy+run
```

## パイプライン（`.github/workflows/deploy.yml`）
| トリガ | ジョブ | environment | 動作 |
|---|---|---|---|
| `pull_request`→main | `validate` | staging | `bundle validate -t staging` |
| `push`→main | `deploy-staging` | staging | `bundle deploy -t staging` → `bundle run -t staging orchestrator_job` |
| 〃（stg 成功後） | `deploy-prod` | **prod（承認ゲート）** | `bundle deploy -t prod` → `bundle run -t prod orchestrator_job` |

- CLI は `databricks/setup-cli`（version ピン留め）。`DATABRICKS_BUNDLE_ENGINE=direct`。
- `deploy-prod` は `needs: deploy-staging` かつ `environment: prod`。prod に **required reviewer** を付けると
  stg 成功後に承認待ちで停止し、承認で prod へ進む（**Environments protection は public repo か有料プランが必要**）。
- `catalog` は全コマンドで `--var catalog=${{ secrets.CATALOG }}`、prod は `run_as` 用に `--var run_as_sp=${{ secrets.DATABRICKS_CLIENT_ID }}`（prod の client_id を流用）。

## GitHub Environments Secrets（環境別・値はリポジトリに置かない）
各 environment に同名で別値を設定（`gh secret set <NAME> --env <env> --body -` を stdin で）。
| Secret | 意味 |
|---|---|
| `DATABRICKS_HOST` | 対象WSの URL |
| `DATABRICKS_CLIENT_ID` | 対象WSの SP applicationId（prod では run_as にも流用） |
| `DATABRICKS_CLIENT_SECRET` | 対象WSの SP OAuth secret |
| `CATALOG` | 対象WSの書込先カタログ名 |

- SP=`sp-dab-cicd-deploy`（両WSに別実体）。OAuth secret は
  `databricks -p <ws> service-principal-secrets-proxy create <SCIM id> --lifetime <秒>s` で発行。
- **run を CI に含める**場合、run_as になる SP がカタログに書ける権限（USE/CREATE SCHEMA/CREATE TABLE/MODIFY/SELECT）を要する。
- 秘匿値は端末に materialize せず `gh secret set --body -` を stdin で。ログ/コミット/チャットに残さない。

## 顧客（エアギャップ）への読み替え
- GitHub-hosted runner（ネット有）→ 顧客は各ネットワークに **self-hosted runner**。CLI は Volume/バイナリ配布。
- 各環境のジョブは**自WSへ直接**認証（stg→azurew1 / prod→azurew2）＝ serverless の自WS束縛は無関係。
- secret ローテーションが楽なのは **Azure Key Vault backend**（本 CI では GitHub Secrets を更新）。
- 最終ターゲットが **Azure DevOps** なら、environment approvals はプラン制約なく使える。

<!-- Vg-1: PR→validate 実証用の軽微変更 -->
