# AdguardHome
我很懒如果你愿意帮我那我乐此不疲



## 项目结构

```
仓库根目录/
├── .github/
│   └── workflows/
│       └── auto-commit.yml        # GitHub Actions工作流配置
├── scripts/
│   ├── update_rules.py            # 规则更新脚本
│   └── auto_commit.py             # Git自动提交脚本
├── Ipurities/
│   ├── Black with impurities.txt  # 包含所有原始黑名单规则
│   └── White with impurities.txt  # 包含所有原始白名单规则
├── Black.txt                      # 去重后的黑名单(最终黑名单)
└── White.txt                      # 去重后的白名单(最终白名单)
```
