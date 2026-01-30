import Config
import Dotenvy

source!([
  Path.absname(".env", File.cwd!()),
  System.get_env()
])

config :sniper,
  github_webhook_secret: env!("GITHUB_WEBHOOK_SECRET", :string?)
