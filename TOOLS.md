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

## terminal_theme_switcher

根据 macOS 系统外观模式自动切换 Terminal 主题。

### 功能说明

检测 macOS 当前的外观模式（浅色/深色），自动将 Terminal.app 的主题切换为对应的配置。

**核心逻辑：**
1. 通过 `defaults read -g AppleInterfaceStyle` 检测系统外观模式
2. 深色模式使用 `Clear Dark` 主题，浅色模式使用 `Clear Light` 主题
3. 更新 Terminal 的默认窗口配置和启动配置
4. 通过 AppleScript 通知正在运行的 Terminal 刷新所有窗口和标签页

**适用场景：**
- macOS 系统外观模式切换时自动同步 Terminal 主题
- 配合 launchd 或其他自动化工具实现自动切换

### 使用方法

```bash
# 直接运行脚本
./terminal_theme_switcher.sh

# 添加到 PATH 后运行
terminal_theme_switcher.sh
```

### 配置说明

脚本内置两个主题配置，可根据需要修改：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LIGHT_PROFILE` | Clear Light | 浅色模式使用的主题名称 |
| `DARK_PROFILE` | Clear Dark | 深色模式使用的主题名称 |

**修改主题名称：**
```bash
# 编辑脚本开头的变量
LIGHT_PROFILE="你的浅色主题名称"
DARK_PROFILE="你的深色主题名称"
```

### 使用场景

**场景 1：手动切换**
```bash
# 当系统切换外观模式后，手动运行脚本同步 Terminal
./terminal_theme_switcher.sh
```

**场景 2：自动切换（配合 launchd）**
```xml
<!-- ~/Library/LaunchAgents/com.user.terminal-theme.plist -->
<key>ProgramArguments</key>
<array>
    <string>/path/to/terminal_theme_switcher.sh</string>
</array>
```

**场景 3：集成到其他脚本**
```bash
# 在 .zshrc 或其他配置中调用
if [[ "$TERM_PROGRAM" == "Apple_Terminal" ]]; then
    /path/to/terminal_theme_switcher.sh
fi
```

### 注意事项

- 仅适用于 macOS 自带的 Terminal.app，不支持 iTerm2 或其他终端
- 主题名称必须与 Terminal 中已存在的主题配置完全匹配
- 需要在 Terminal 的偏好设置中预先创建对应的主题配置
- 脚本会同时更新默认配置和所有已打开的窗口/标签页

### 示例输出

```
2026年5月28日 10:30:00: 已切换到 Clear Dark
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
