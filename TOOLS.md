# 工具详细说明

本文档记录所有工具的详细使用说明。

---

## clean_empty_dirs

递归清理空目录。

### 功能说明

扫描指定目录及其子目录，删除所有空目录或只包含空目录/忽略项的目录树。

**核心逻辑：**
1. 从最深层目录开始检查（自底向上）
2. 如果目录是空的，或只包含空目录/忽略项，则删除
3. 递归向上处理，确保嵌套的空目录都能被清理

**自动忽略：**
- `.DS_Store` 文件不视为有效内容，包含它的目录仍可被删除
- 符号链接目录和文件不参与空目录判断，不会被删除

### 使用方法

```bash
# 基本用法 - 扫描当前目录
python clean_empty_dirs.py

# 扫描指定目录
python clean_empty_dirs.py /path/to/project

# 限制扫描深度
python clean_empty_dirs.py --depth 3

# 忽略特定目录名称
python clean_empty_dirs.py --ignore .workbuddy

# 忽略多个目录名称（用逗号分隔）
python clean_empty_dirs.py -i .git,.workbuddy

# 结合目录、深度和忽略参数
python clean_empty_dirs.py /path/to/project --depth 3 --ignore .workbuddy

# 查看帮助信息
python clean_empty_dirs.py --help
```

### 参数说明

| 参数 | 简写 | 说明 |
|------|------|------|
| `[directory]` | - | 要扫描的目录，默认为当前目录 |
| `--depth <层数>` | - | 限制扫描的目录层数 |
| `--ignore <名称>` | `-i` | 忽略的目录名称，多个用逗号分隔 |
| `--help` | `-h` | 显示帮助信息 |

### 使用场景

**场景 1：清理项目空目录**
```
项目构建后可能留下空目录结构：
parent/
  └── child1/
      └── child2/
          └── child3/  (空)

运行脚本后，child3、child2、child1 会被依次删除
```

**场景 2：忽略特定目录**
```
某些目录如 .git、.workbuddy 需要保留：
project/
  ├── .git/
  ├── src/  (有文件)
  └── empty_dir/
      └── .workbuddy/

使用 --ignore .git,.workbuddy 后：
- .git 及其子目录会被跳过，project 不会被删除
- empty_dir 只包含 .workbuddy，会被删除（连同 .workbuddy 一起）
```

**场景 3：清理含 .DS_Store 的空目录**
```
macOS 系统会自动生成 .DS_Store 文件：
project/
  └── empty_dir/
      └── .DS_Store

脚本会自动忽略 .DS_Store，empty_dir 仍会被删除
```

### 注意事项

- 脚本只删除**空目录**或**只包含空目录/忽略项的目录**
- 包含任何非忽略文件的目录不会被删除
- 使用 `--ignore` 参数时，忽略的目录及其子目录不会被扫描
- 只包含忽略目录的目录会被视为空目录并删除（连同忽略目录一起）
- 符号链接目录和文件会被跳过，不参与判断
- 建议先在测试环境运行，确认效果后再在生产环境使用

### 示例输出

```
扫描目录: /path/to/project
忽略目录名称: .git, .workbuddy
--------------------------------------------------
已删除空目录: /path/to/project/level1/level2/level3
已删除空目录: /path/to/project/level1/level2
已删除空目录: /path/to/project/level1
--------------------------------------------------
清理完成，共删除 3 个空目录
```

---

<!-- 新工具说明模板 -->

<!--
## tool_name

工具简要说明。

### 功能说明

详细功能说明。

### 使用方法

```bash
# 使用示例
python tool_name.py [参数]
```

### 参数说明

| 参数 | 说明 |
|------|------|
| ... | ... |

### 使用场景

场景说明...

### 注意事项

注意事项...

### 示例输出

```
示例输出...
```

---
-->
