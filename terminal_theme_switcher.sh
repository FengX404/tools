#!/bin/bash
# 根据系统外观模式自动切换 Terminal 主题

LIGHT_PROFILE="Clear Light"
DARK_PROFILE="Clear Dark"

# 检测当前系统外观
if defaults read -g AppleInterfaceStyle &>/dev/null; then
    TARGET="$DARK_PROFILE"
else
    TARGET="$LIGHT_PROFILE"
fi

# 设置 Terminal 默认配置
defaults write com.apple.Terminal "Default Window Settings" "$TARGET"
defaults write com.apple.Terminal "Startup Window Settings" "$TARGET"

# 通知 Terminal 刷新（如果正在运行）
osascript -e "
tell application \"Terminal\"
    set default settings to settings set \"$TARGET\"
    repeat with w in every window
        repeat with t in every tab of w
            try
                set current settings of t to settings set \"$TARGET\"
            end try
        end repeat
    end repeat
end tell
" 2>/dev/null

echo "$(date): 已切换到 $TARGET"
