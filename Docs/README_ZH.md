<p align="center">
  <img src="banner-promptiq.jpg" alt="PromptIQ" width="750">
</p>

<h1 align="center">PromptIQ</h1>

<p align="center">
  <strong>智能提示词工程工具包<br>
  版本控制 + 四阶段AI评估 + A/B测试 + 自动优化 — 全在终端完成</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/promptiq/"><img src="https://img.shields.io/pypi/v/promptiq?color=blueviolet&style=for-the-badge"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/许可证-MIT-22c55e?style=for-the-badge"></a>
</p>

---

## 💀 问题所在

你花了几个小时调优一个提示词。它终于完美运行了。
你做了一个小改动。
一切都崩溃了。

没有历史记录。没有回滚。没有差异对比。**那个有效的版本永远消失了。**

---

## ✦ PromptIQ 是什么？

PromptIQ 是一个面向 LLM 提示词的版本控制系统 — 内置真正的智能。

一条命令完成所有这些：

```bash
promptiq commit chatbot system.txt -m "改进语调" --judge --test-cases inputs.json
```

1. ✅ 用语义版本号（`v1.2.0`）和哈希保存版本
2. ✅ 在5个维度上评估提示词文本
3. ✅ 在真实输入上运行提示词并评估实际输出
4. ✅ 与上一版本对比并声明获胜者
5. ✅ 针对你的具体弱点生成改进版本
6. ✅ 以 JSON 格式本地存储 — 无需云端，无需账户

---

## ⚡ 安装

```bash
# 使用 Claude（推荐）
pip install "promptiq[anthropic]"
export ANTHROPIC_API_KEY=sk-ant-...

# 使用 OpenAI
pip install "promptiq[openai]"
export OPENAI_API_KEY=sk-...
```

---

## 🚀 快速开始

```bash
# 提交版本
promptiq commit chatbot system.txt -m "初稿"

# 提交 + 完整四阶段评估
promptiq commit chatbot system.txt -m "改进版" --judge --test-cases inputs.json

# 查看带质量分数的历史记录
promptiq log chatbot

# 两个版本之间的词级差异对比
promptiq diff chatbot 1.0.0 1.1.0

# A/B 测试两个版本
promptiq ab chatbot 1.0.0 1.1.0 --test-cases inputs.json

# 获取AI改进版本
promptiq improve chatbot

# 导出 Markdown 更新日志
promptiq export chatbot
```

---

## 🧠 四阶段评估系统

```
阶段 1 ── 静态分析    评估提示词文本本身
阶段 2 ── 输出评估    在LLM上运行，评估真实输出
阶段 3 ── 版本对比    与上一版本正面对决
阶段 4 ── 自动优化    针对弱点重写，附变更列表
```

### 评估维度

| 维度 | 衡量内容 |
|---|---|
| 清晰度 | 无歧义？两位工程师会做出相同解读吗？ |
| 具体性 | 指令是否具体可操作？ |
| 简洁性 | 没有冗余和填充词？ |
| 指令质量 | 有效引导模型行为？（权重 1.5x） |
| 鲁棒性 | 处理边缘情况和故障模式？（权重 1.5x） |

---

## 📖 所有命令

```bash
promptiq commit <名称> <文件> -m "消息" [--judge] [--test-cases 文件.json]
promptiq log <名称>
promptiq diff <名称> <ref_a> <ref_b>
promptiq judge <文件> [--test-cases 文件.json]
promptiq improve <名称>
promptiq ab <名称> <ref_a> <ref_b> --test-cases 文件.json
promptiq status <名称>
promptiq checkout <名称> <ref>
promptiq ls
promptiq export <名称> [--format markdown|json|scores]
promptiq branch create|switch|ls <名称>
```

---

## 🗄️ 存储方式

```
~/.promptiq/
└── prompts/
    ├── chatbot.json
    └── summarizer.json
```

纯 JSON 文件。任何编辑器都可读。无数据库。无厂商锁定。

---

## 📄 许可证

MIT — 使用它，Fork 它，基于它构建，发布它。

---

<p align="center">
  <em>提示词工程不应该靠猜测。<br>
  每次改变都应该可以量化。每个版本都应该可以改进。<br>
  这就是 PromptIQ 存在的意义。</em>
</p>
