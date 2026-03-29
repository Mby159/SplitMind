# SplitMind 治理模型

## 概述

SplitMind 采用 **BDFL（Benevolent Dictator For Life）+ 维护小组** 的治理模式，确保项目的稳定发展和社区参与。

## 治理结构

### 1. BDFL（项目负责人）
- **角色**：项目的最终决策者
- **职责**：
  - 制定项目愿景和路线图
  - 最终决策重大技术和架构问题
  - 批准核心贡献者
  - 维护项目的长期健康发展
- **当前担任者**：Mby159

### 2. 维护小组（Core Maintainers）
- **角色**：项目的核心维护者
- **职责**：
  - 日常代码审查和合并
  - 解决技术问题和 bug
  - 指导新贡献者
  - 维护文档和示例
- **如何成为维护者**：
  - 持续贡献高质量代码
  - 积极参与代码审查
  - 展示对项目的深度理解
  - 得到 BDFL 和现有维护者的认可

### 3. 贡献者（Contributors）
- **角色**：所有为项目做出贡献的人
- **职责**：
  - 提交代码、文档或创意
  - 参与讨论和反馈
  - 帮助其他用户
- **如何成为贡献者**：
  - 提交 Pull Request
  - 报告 Issue
  - 改进文档
  - 参与社区讨论

## 决策流程

### 1. 日常决策
- 维护小组可以独立做出日常决策
- 决策应记录在相关 Issue 或 PR 中

### 2. 重大决策
- 涉及架构变更、API 变更或重大功能的决策
- 流程：
  1. 提出 RFC（Request For Comments）
  2. 社区讨论（至少 1 周）
  3. 维护小组审议
  4. BDFL 最终决策

### 3. 争议解决
- 优先通过讨论达成共识
- 如无法达成共识，由 BDFL 做出最终决定

## 贡献指南

### 代码贡献
1. Fork 项目仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add some amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 开启 Pull Request

### 代码审查
- 所有 PR 至少需要 1 名维护者审查
- PR 应通过所有 CI 检查
- 鼓励建设性的代码审查意见

### 行为准则
- 尊重所有贡献者
- 保持专业和友好
- 专注于技术讨论
- 遵守项目的 [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)

## 版本发布

### 发布流程
1. 维护小组决定发布版本
2. 更新 CHANGELOG.md
3. 标记版本（`git tag -a v0.1.0 -m 'Release v0.1.0'`）
4. 推送标签（`git push origin v0.1.0`）
5. GitHub Actions 自动构建和发布

### 版本号规范
- 遵循语义化版本（Semantic Versioning）
- MAJOR.MINOR.PATCH
  - MAJOR：不兼容的 API 变更
  - MINOR：向后兼容的功能新增
  - PATCH：向后兼容的问题修复

## 社区建设

### 沟通渠道
- GitHub Issues：问题报告和功能请求
- GitHub Discussions：社区讨论
- 未来可能添加：Discord/Slack 等实时沟通

### 社区活动
- 定期发布路线图更新
- 收集用户反馈
- 鼓励社区贡献
- 认可优秀贡献者

## 可持续性

### 维护保障
- 建立自动化流程（Dependabot、CI/CD）
- 关键依赖建立备份
- 文档化所有重要决策

### 风险规避
- 避免单一维护者瓶颈
- 培养新的维护者
- 保持代码质量和可维护性

## 修改治理模型

如需修改本治理模型，需遵循重大决策流程，并获得 BDFL 的最终批准。

---

**最后更新**：2026-03-30
