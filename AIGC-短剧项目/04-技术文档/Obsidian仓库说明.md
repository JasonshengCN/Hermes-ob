---
tags: [配置, 技术文档]
created: 2026-05-26
---

# ⚙️ Obsidian 仓库说明

## 仓库路径
```
/home/jason/Documents/Obsidian Vault/
├── AIGC-短剧项目/         ← 本项目笔记
├── .obsidian/              ← Obsidian 配置
└── 其他笔记...
```

## 与项目目录的联动

本仓库与 `/home/jason/aigc-douyin-project/` 通过双向同步脚本联动：

- **→ 同步到 Obsidian**：`~/sync-to-obsidian.sh`
  - 把 `prompt-engineering/` 和成品图片同步到 Obsidian 仓库
- **← 同步回项目**：`~/sync-from-obsidian.sh`
  - 把 Obsidian 里的笔记改动同步回项目目录

## 自动同步

通过定时任务实现每日同步（如果开启）：
```
0 8 * * * /home/jason/sync-to-obsidian.sh
```

## 使用方式

在 Obsidian 桌面端打开此仓库即可。
所有笔记使用 Markdown + [[双向链接]]，支持图谱视图。
