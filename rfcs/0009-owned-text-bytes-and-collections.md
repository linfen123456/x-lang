# RFC-0009：拥有型文本、字节与标准集合契约

> 状态：Proposed
> 日期：2026-08-18
> 目标阶段：P2 core/alloc/std
> 依赖：RFC-0006、RFC-0007
> 相关缺口：`GAP-LANG-03`、`GAP-DX-01`、`XLF-09-002`
> 正式产物：接受后生成 `specs/library/text-bytes-and-collections.md`。

## 1. 摘要

本提案区分借用视图与拥有型动态数据，并冻结 `Vec`、`HashMap`、`BTreeMap`、`OrderedMap` 的最小安全契约。集合属于 `alloc/std`，不是编译器内建语法。

## 2. 文本与字节所有权

| 类型 | 所有权 | 不变量 |
|---|---|---|
| `Str` | 动态大小 UTF-8 视图，通常以 `&Str` 使用 | 始终有效 UTF-8，不承诺按字节索引字符 |
| `[T]` | 动态大小连续元素视图，通常以 `&[T]`/`&mut [T]` 使用 | 长度与元素对齐有效 |
| `String` | 拥有型可增长 UTF-8 缓冲区 | 内容始终是有效 UTF-8 |
| `Bytes` | 拥有型不可变字节序列，可共享底层存储 | 不假定 UTF-8 |
| `Vec<T>` | 拥有型可增长连续容器 | `length <= capacity`，元素初始化状态有效 |

从 `String/Bytes/Vec<T>` 创建的借用不能长于拥有者。函数返回 `&Str`、`&[T]` 或集合元素借用时，返回生命周期必须唯一绑定到输入借用或静态存储；局部缓冲区、Temporary 和已移动对象的借用不得逃逸。

涉及分配的构造和增长 API 同时提供普通版本与 `try_*` 版本；普通版本遵循 RFC-0008 的 OOM 策略，`try_*` 返回显式分配错误。

## 3. 集合类型

### 3.1 `HashMap<K, V>`

- 平均常数时间查找目标，不承诺具体算法或最坏复杂度；
- 默认每进程或每实例使用不可预测种子，抵抗不可信键触发的 HashDoS；
- 遍历顺序未指定，不能进入序列化、签名、快照、构建键或共识结果；
- `K` 必须满足稳定的 `Hash + Eq` 一致性契约；键在表内期间不得以破坏 Hash/Eq 的方式变化；
- 不提供模块属性或 Manifest 开关全局替换默认 HashMap 实现。

### 3.2 `BTreeMap<K, V>`

- `K` 满足全序；
- 遍历按键序，查找、插入和删除为对数复杂度目标；
- 用于范围查询和需要键序的内存数据，但序列化仍必须声明格式自己的排序规则。

### 3.3 `OrderedMap<K, V>`

- 保持首次插入顺序；更新值不改变位置，删除后重新插入追加到末尾；
- 用于保留输入顺序、配置和调试体验；
- 插入顺序不是 Canonical JSON 键序。

## 4. 最小 API

```x
impl<K, V> HashMap<K, V> {
    pub fn new() -> HashMap<K, V>;
    pub fn length(self: &Self) -> USize;
    pub fn get(self: &Self, key: &K) -> Option<&V>;
    pub fn get_mut(self: &mut Self, key: &K) -> Option<&mut V>;
    pub fn insert(self: &mut Self, key: K, value: V) -> Option<V>;
    pub fn remove(self: &mut Self, key: &K) -> Option<V>;
    pub fn contains_key(self: &Self, key: &K) -> Bool;
}
```

`BTreeMap` 与 `OrderedMap` 提供等价的所有权形状。`get/get_mut` 不移动值；缺键返回 `None`，不 panic。Index 操作若未来提供，必须显式标记可能 panic，不能替代安全访问 API。

Iterator 借用集合；结构性修改要求独占借用，因此不能在活动 Iterator 上静默使引用失效。`remove` 仅在没有冲突借用时返回拥有型值。

## 5. 字面量与确定性

1.0 不提供 Map Literal。后续可以独立研究：

```x
let headers = map {
    "accept" => "application/json",
};
```

该研究不得使用 `%{}`，不得与 JSON Literal 复用语义，也不能在没有确定 `K/V` 类型时退化为隐式 `Dynamic`。

## 6. 失败、安全与资源边界

- 容量计算溢出必须在分配前失败；
- 来自不可信输入的批量收集 API接受显式大小上限；
- Hash 冲突退化必须可观测并进入安全基准；
- Debug 输出和迭代不得被描述为稳定格式；
- 清空或析构集合按 RFC-0007 恰好一次析构仍拥有的键和值。

## 7. 验收

- compile-pass/fail：`get/get_mut/remove` 的借用、移动和 Iterator 失效规则；
- run-pass：缺键、替换旧值、删除/重插顺序、Drop Trace；
- 属性测试：Hash/Eq 一致性、BTree 全序、OrderedMap 顺序；
- 安全测试：对抗键、容量溢出、大小上限和 OOM；
- 确定性负例：禁止把 HashMap 顺序用于签名、Canonical JSON 或构建键；
- API/诊断 Snapshot：借用逃逸必须指明来源拥有者和失效位置。

