# AdguardHome
我很懒如果你愿意帮我那我乐此不疲

黑名单:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/Black.txt

白名单:
https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/White.txt



## 项目结构

```
仓库根目录/
├── .github/
│   └── workflows/
│       └── auto-commit.yml        # GitHub Actions工作流配置
├── scripts/
│   └── adguard_rules_merger.py    # 规则更新脚本
├── Black.txt                      # 去重后的黑名单(最终黑名单)
└── White.txt                      # 去重后的白名单(最终白名单)
```
