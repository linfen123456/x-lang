---
doc_id: DOC-TOOLS-TEST-RUNNER
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-02-014, XLF-03-002, XLF-11-004, XLF-11-013, XLF-12-020]
---
# `xtest` 测试运行器

> 状态：草案｜Owner：`role/tooling-team`

## TestPlan 与报告

`TestPlan` 字段为 `workspace:PathBuf`、`filters:Vec<String>`、`kinds:Unit|Conformance|CompileFail|Doc|Integration|Fuzz|Bench`、`target:TargetSpecId`、`jobs:u16`、`timeout_ms:u64`、`retry:u8`、`seed:u64`、`isolation:Isolated|Shared`、`offline:bool`。前置是测试清单/target/profile 合法；后置是每 case 的 `TestResult{id,status,duration_ms,stdout_path,stderr_path,artifacts,attempts}`。

发现按 manifest/命名/属性确定排序；默认每 case 独立临时目录、端口、时钟、随机种子和环境，`Shared` 必须显式标记。并行只在资源 lease 允许时执行；取消停止派发并优雅终止子进程树。失败不会无限重试：默认 0，允许最多 2 次且报告所有 attempt 和 flaky suspicion。

## 资源、诊断与负向测试

默认单 test 5 min、进程 64、内存 1 GiB、输出 64 MiB、artifact 2 GiB。被测程序主动超出其测试预算属于测试失败，返回 2；运行器或宿主无法提供声明资源属于环境失败，返回 3；用户取消或统一 deadline 到期返回 4；状态均记录为 `resource_exhausted`、`environment_failed`、`cancelled` 或 `timed_out`，不得只靠退出码猜测。编译失败/期望诊断比较 code/span/message pattern，不依赖本地化全文。安全测试必须覆盖路径、命令、秘密和插件。

负向集覆盖 test panic、超时、取消、孤儿进程、端口冲突、磁盘满、随机种子异常、坏快照、并发共享状态、网络隔离和错误期望。`TEST-TOOLS-RUNNER-001` 验证任意顺序/并行，`TEST-TOOLS-RUNNER-002` 验证 flaky 不能被重试掩盖，`TEST-TOOLS-RUNNER-003` 验证最小复现和 artifact retention。

## 版本与回滚

JUnit/JSON/文本报告 schema minor 只追加字段；工具版本和 TargetSpec fingerprint 写入报告。回归时 `--jobs 1 --retry 0 --seed <old>` 重放，恢复上一 runner/schema，保留失败输入、命令、环境指纹与日志。
