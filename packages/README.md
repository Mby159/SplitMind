# ⚠️ `packages/` — 陈旧快照，不参与构建

这里的三个子包（`splitmind-core` / `splitmind-providers` / `splitmind-cli`）是**早期版本的副本**，
与仓库根目录的活跃实现 `../splitmind/` 重复。以下为 2026-09-14 实测结论。

## 实测证据

1. **不参与构建**：根 `pyproject.toml` 的 `[tool.setuptools.packages.find]` 写着
   `include = ["splitmind*"]` / `exclude = ["packages*"]` —— 发布 `splitmind` 时这里的代码**不会**被打包。

2. **是子集**（`^class\s+(\w+)` 统计）：

   | 位置 | 类 |
   |---|---|
   | `../splitmind/core/`（活跃） | 26 个，含 `SplitMindEngine`、`ExecutionMode`、`LocalModelInterface` 等 |
   | `packages/core/splitmind_core/`（本目录） | 13 个，全部是活跃版同名的子集 |

3. **`examples/` 里 3 个脚本 import 的是本目录的包，实测直接崩**：

   ```
   $ python examples/comprehensive_test.py
   ModuleNotFoundError: No module named 'splitmind_core'
   $ python examples/providers_test.py
   ModuleNotFoundError: No module named 'splitmind_providers'
   $ python examples/pure_framework_demo.py
   ModuleNotFoundError: No module named 'splitmind_core'
   ```

   注意：即使把 import 改成 `splitmind.*` 也不能直接跑通 —— provider 注册表 API 已经改过
   （旧：`ProviderRegistry().register_provider(name, provider)` / `get_provider()`；
   新：`registry.register(provider)` / `registry.get(name)` / `registry.create_provider(...)`），
   所以这 3 个脚本需要**移植**而不是改个 import。

## 待决定

两个自洽的方向，请选一个（未替你决定）：

- **A. 删除本目录**（`git rm -r packages`），并把 3 个 example 移植到 `splitmind.*` API；
- **B. 反向统一**：让 `packages/` 成为唯一实现，根目录改为薄壳。

在决定之前，本目录**只读**：不要往这里加功能，也不要让新代码 import `splitmind_core` / `splitmind_providers`。
