# Workspace Git Backup & Sync
# 用法：lobster run git-sync.lobster

name: Workspace Git Backup & Sync

steps:
  - id: check_status
    run: exec --shell "cd ~/.openclaw/workspace && git status --porcelain"
  - id: parse_json
    run: json
  - id: check_changes
    run: where "length > 0"
  - id: add_files
    run: exec --shell "cd ~/.openclaw/workspace && git add ."
  - id: commit
    run: exec --shell "cd ~/.openclaw/workspace && git commit -m 'Lobster auto-sync'"
  - id: push
    run: exec --shell "cd ~/.openclaw/workspace && git push origin main"
  - id: notify
    run: exec --shell "echo '✅ Workspace 同步完成！'"
