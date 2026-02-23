name: git-sync
description: Workspace Git Backup & Sync

steps:
  - exec --shell "cd ~/.openclaw/workspace && git status --porcelain"
  - json
  - exec --shell "if [ -z \"$(cat)\" ]; then echo '✅ Workspace 配置已是最新'; exit 0; fi"
  - exec --shell "cd ~/.openclaw/workspace && git add ."
  - exec --shell "cd ~/.openclaw/workspace && git commit -m 'Lobster sync: $(date +%Y-%m-%d)'"
  - exec --shell "cd ~/.openclaw/workspace && git push origin main"
  - exec --shell "echo '✅ Workspace 同步完成！'"
