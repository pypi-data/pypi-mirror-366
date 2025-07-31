import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from json_repair import repair_json


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.claude-switch'
        self.config_file = self.config_dir / 'config.json'
        self.env_file = self.config_dir / 'env.sh'
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self._create_default_config()

    def _create_default_config(self):
        """创建默认配置"""
        default_config = {
            "version": "2.0",
            "configs": {
                "default": {
                    "base_url": "https://api.anthropic.com",
                    "api_keys": [],
                    "auth_tokens": [],
                    "note": "默认配置",
                    "active_auth": -1,
                    "active_key": -1
                }
            },
            "active": "default"
        }
        self._save_config(default_config)

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 版本兼容处理
            if config.get('version') != '2.0':
                config = self._migrate_config(config)

            return config
        except FileNotFoundError:
            self._create_default_config()
            return self._load_config()
        except json.JSONDecodeError as e:
            # 如果配置文件格式错误，尝试修复
            return self._handle_json_error(e)

    def _handle_json_error(self, error: json.JSONDecodeError) -> Dict[str, Any]:
        """处理JSON格式错误，尝试修复配置文件"""
        import shutil
        
        # 备份原始损坏文件
        backup_file = self.config_file.with_suffix('.json.backup')
        shutil.copy2(self.config_file, backup_file)
        
        try:
            # 读取文件内容
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试修复JSON
            repaired_content = repair_json(content)
            
            # 验证修复后的JSON是否有效
            try:
                config = json.loads(repaired_content)
                
                # 保存修复后的配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(repaired_content)
                os.chmod(self.config_file, 0o600)
                
                # 检查版本并迁移
                if config.get('version') != '2.0':
                    config = self._migrate_config(config)
                
                print(f"✅ 配置文件JSON格式已自动修复")
                print(f"📁 原始损坏文件已备份到: {backup_file}")
                return config
                
            except json.JSONDecodeError as repair_error:
                # 修复失败，显示详细错误信息
                error_msg = self._format_json_error_message(error, content)
                print(f"❌ 配置文件JSON格式错误，无法自动修复")
                print(f"📁 原始损坏文件已备份到: {backup_file}")
                print(f"\n错误详情:\n{error_msg}")
                print(f"\n修复尝试失败:\n{repair_error}")
                print(f"\n请手动修复配置文件或删除备份文件后重试")
                raise SystemExit(1)
                
        except Exception as repair_error:
            # 修复过程中出现其他错误
            print(f"❌ 尝试修复配置文件时发生错误: {repair_error}")
            print(f"📁 原始损坏文件已备份到: {backup_file}")
            print(f"\n请手动修复配置文件或删除备份文件后重试")
            raise SystemExit(1)
    
    def _format_json_error_message(self, error: json.JSONDecodeError, content: str) -> str:
        """格式化JSON错误信息"""
        lines = content.splitlines()
        error_line = lines[error.lineno - 1] if error.lineno <= len(lines) else ""
        
        error_info = [
            f"错误位置: 第 {error.lineno} 行, 第 {error.colno} 列",
            f"错误类型: {error.msg}",
            f"错误行内容: {error_line}",
            f"错误位置标记: {' ' * (error.colno - 1)}^"
        ]
        
        return "\n".join(error_info)

    def _migrate_config(self, old_config: Dict[str, Any]) -> Dict[str, Any]:
        """迁移旧配置到新格式"""
        # 如果已经是新格式，直接返回
        if "version" in old_config and old_config["version"] == "2.0":
            return old_config

        new_config = {
            "version": "2.0",
            "configs": {},
            "active": old_config.get("active", "default")
        }

        # 如果旧配置已经是新格式（有configs字段）
        if "configs" in old_config and isinstance(old_config["configs"], dict):
            # 直接复制现有配置
            new_config["configs"] = old_config["configs"].copy()

            # 确保每个配置都有必需的字段
            for name, config in new_config["configs"].items():
                if isinstance(config, dict):
                    # 确保必需字段存在
                    config.setdefault("base_url", "https://api.anthropic.com")
                    config.setdefault("api_keys", [])
                    config.setdefault("auth_tokens", [])
                    config.setdefault("note", "")
                    config.setdefault("active_auth", -1)
                    config.setdefault("active_key", -1)

                    # 迁移旧字段到新字段
                    if "api_key" in config and config["api_key"]:
                        if config["api_key"] not in config["api_keys"]:
                            config["api_keys"].append(config["api_key"])
                        del config["api_key"]

                    if "auth_token" in config and config["auth_token"]:
                        if config["auth_token"] not in config["auth_tokens"]:
                            config["auth_tokens"].append(config["auth_token"])
                        del config["auth_token"]
        else:
            # 迁移旧格式到新格式
            for name, config in old_config.get("configs", {}).items():
                api_keys = [config.get("api_key", "")] if config.get(
                    "api_key") else []
                auth_tokens = [config.get("auth_token", "")] if config.get(
                    "auth_token") else []

                new_config["configs"][name] = {
                    "base_url": config.get("base_url", "https://api.anthropic.com"),
                    "api_keys": api_keys,
                    "auth_tokens": auth_tokens,
                    "note": config.get("note", ""),
                    "active_auth": 0 if auth_tokens else -1,
                    "active_key": 0 if api_keys and not auth_tokens else -1
                }

        # 备份旧配置
        backup_file = self.config_file.with_suffix('.json.migration-backup')
        import shutil
        shutil.copy2(self.config_file, backup_file)

        self._save_config(new_config)
        return new_config

    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        os.chmod(self.config_file, 0o600)

    def get_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有配置"""
        config = self._load_config()
        return config.get('configs', {})

    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定配置"""
        configs = self.get_configs()
        return configs.get(name)

    def get_current_config_name(self) -> Optional[str]:
        """获取当前配置名"""
        config = self._load_config()
        return config.get('active')

    def get_current_active_credentials(self) -> Optional[Dict[str, str]]:
        """获取当前激活的凭据"""
        current_name = self.get_current_config_name()
        if not current_name:
            return None

        config = self.get_config(current_name)
        if not config:
            return None

        result = {"base_url": config["base_url"],
                  "auth_token": "", "api_key": ""}

        # 优先使用auth_token
        if config["active_auth"] >= 0 and config["active_auth"] < len(config["auth_tokens"]):
            token_value = config["auth_tokens"][config["active_auth"]]
            # 如果包含名称，只取凭据部分
            if '|' in token_value:
                result["auth_token"] = token_value.split('|', 1)[0]
            else:
                result["auth_token"] = token_value
        elif config["active_key"] >= 0 and config["active_key"] < len(config["api_keys"]):
            key_value = config["api_keys"][config["active_key"]]
            # 如果包含名称，只取凭据部分
            if '|' in key_value:
                result["api_key"] = key_value.split('|', 1)[0]
            else:
                result["api_key"] = key_value

        return result

    def add_config(self, name: str, base_url: str, note: str = "") -> bool:
        """添加新配置"""
        if not name:
            return False

        config = self._load_config()
        if name in config["configs"]:
            return False

        # 确保不覆盖现有配置
        existing_configs = config.get("configs", {})
        existing_configs[name] = {
            "base_url": base_url,
            "api_keys": [],
            "auth_tokens": [],
            "note": note,
            "active_auth": -1,
            "active_key": -1
        }

        # 只更新configs部分，保持其他配置不变
        config["configs"] = existing_configs
        self._save_config(config)
        return True

    def add_credential(self, config_name: str, credential_type: str, value: str) -> bool:
        """添加凭据到配置"""
        if credential_type not in ["api_key", "auth_token"]:
            return False

        config = self._load_config()
        if config_name not in config["configs"]:
            return False

        target_list = "api_keys" if credential_type == "api_key" else "auth_tokens"
        if value not in config["configs"][config_name][target_list]:
            config["configs"][config_name][target_list].append(value)

            # 如果是第一个凭据，自动激活
            if len(config["configs"][config_name][target_list]) == 1:
                if credential_type == "api_key":
                    config["configs"][config_name]["active_key"] = 0
                    config["configs"][config_name]["active_auth"] = -1
                else:
                    config["configs"][config_name]["active_auth"] = 0
                    config["configs"][config_name]["active_key"] = -1

        self._save_config(config)
        return True

    def set_active_config(self, name: str) -> bool:
        """设置激活的配置"""
        config = self._load_config()
        if name not in config["configs"]:
            return False

        config["active"] = name
        self._save_config(config)
        return True

    def set_active_credential(self, config_name: str, credential_type: str, index: int) -> bool:
        """设置激活的凭据"""
        config = self._load_config()
        if config_name not in config["configs"]:
            return False

        target_list = "api_keys" if credential_type == "api_key" else "auth_tokens"
        if index < 0 or index >= len(config["configs"][config_name][target_list]):
            return False

        if credential_type == "api_key":
            config["configs"][config_name]["active_key"] = index
            config["configs"][config_name]["active_auth"] = -1
        else:
            config["configs"][config_name]["active_auth"] = index
            config["configs"][config_name]["active_key"] = -1

        self._save_config(config)
        return True

    def remove_config(self, name: str) -> bool:
        """删除配置"""
        config = self._load_config()
        if name not in config["configs"] or len(config["configs"]) <= 1:
            return False

        del config["configs"][name]

        if config["active"] == name:
            config["active"] = next(iter(config["configs"]))

        self._save_config(config)
        return True

    def remove_credential(self, config_name: str, credential_type: str, index: int) -> bool:
        """删除凭据"""
        config = self._load_config()
        if config_name not in config["configs"]:
            return False

        target_list = "api_keys" if credential_type == "api_key" else "auth_tokens"
        if index < 0 or index >= len(config["configs"][config_name][target_list]):
            return False

        del config["configs"][config_name][target_list][index]

        # 调整激活索引
        active_attr = "active_key" if credential_type == "api_key" else "active_auth"
        if config["configs"][config_name][active_attr] >= len(config["configs"][config_name][target_list]):
            config["configs"][config_name][active_attr] = max(
                0, len(config["configs"][config_name][target_list]) - 1)

        self._save_config(config)
        return True

    def init_shell(self) -> str:
        """初始化shell集成，支持动态路径发现和多种安装方式"""
        shell_config_map = {
            'bash': '.bashrc',
            'zsh': '.zshrc',
            'fish': '.config/fish/config.fish'
        }

        shell = os.environ.get('SHELL', '').split('/')[-1]
        if shell not in shell_config_map:
            shell = 'bash'  # 默认bash

        shell_config = Path.home() / shell_config_map[shell]

        # 动态发现cs命令路径的函数
        def find_cs_command():
            import shutil
            # 备选查找 claude-switch 命令
            claude_switch_path = shutil.which('claude-switch')
            if claude_switch_path:
                return claude_switch_path
            
            # 优先查找 cs 命令
            cs_path = shutil.which('cs')
            if cs_path:
                return cs_path
                
            # 如果都找不到，返回 claude-switch 作为默认值
            return 'claude-switch'

        cs_command = find_cs_command()

        wrapper_content = f'''# Claude Switch Auto-activation
# 自动生成的配置文件，请勿手动修改
# Generated by claude-switch v1.0.1

# 动态查找cs命令的函数
_find_cs_command() {{
    if command -v claude-switch >/dev/null 2>&1; then
        echo "claude-switch"
    elif command -v cs >/dev/null 2>&1; then
        echo "cs"
    else
        return 1
    fi
}}

# 创建cs命令包装
claude_switch() {{
    local real_cs
    real_cs=$(_find_cs_command)
    
    # 检查命令是否存在
    if [[ $? -ne 0 ]] || ! command -v "$real_cs" >/dev/null 2>&1; then
        echo "❌ 找不到 claude-switch 命令"
        echo "请确保已正确安装:"
        echo "  pip install claude-switch"
        echo "  # 或"
        echo "  pipx install claude-switch"
        echo ""
        echo "如果已安装但仍出现此错误，请检查 PATH 环境变量设置"
        return 1
    fi
    
    case "$1" in
        use|select|"")
            "$real_cs" "$@"
            exit_code=$?
            if [[ $exit_code -eq 0 ]]; then
                source {self.env_file}
                echo "✅ 环境变量已自动生效"
            elif [[ $exit_code -eq 2 ]]; then
                # 用户取消操作，不显示环境变量生效消息
                :
            fi
            ;;
        *)
            "$real_cs" "$@"
            ;;
    esac
}}

# 设置别名
alias cs='claude_switch'
alias csu='claude_switch use'
alias csc='claude_switch current'
alias css='source {self.env_file}'

# 自动source配置文件
source {self.env_file} 2>/dev/null || true

# 验证安装
if ! _find_cs_command >/dev/null 2>&1; then
    echo "⚠️  警告: 找不到 claude-switch 命令"
    echo "请运行以下命令安装: pip install claude-switch"
fi
'''

        wrapper_file = self.config_dir / 'cs-wrapper.sh'
        with open(wrapper_file, 'w') as f:
            f.write(wrapper_content)

        source_line = f'source {wrapper_file}'

        try:
            # 检查当前是否可以找到命令
            cs_found = find_cs_command() != 'cs'
            
            if shell_config.exists():
                with open(shell_config, 'r') as f:
                    content = f.read()
                if source_line not in content:
                    with open(shell_config, 'a') as f:
                        f.write(
                            f'\n# Claude Switch - 自动环境变量生效\n{source_line}\n')
                    
                    success_msg = f"✅ 已添加配置到 {shell_config}"
                    if cs_found:
                        success_msg += f"\n✅ 检测到 claude-switch 命令: {cs_command}"
                    else:
                        success_msg += "\n⚠️  尚未检测到 claude-switch 命令，请确保已安装"
                    
                    success_msg += f"\n📁 Shell 配置文件: {wrapper_file}"
                    success_msg += "\n🔄 请重启终端或运行: source ~/.claude-switch/cs-wrapper.sh"
                    success_msg += "\n\n🚀 快速开始:"
                    success_msg += "\n  cs add      # 添加配置"
                    success_msg += "\n  cs          # 选择配置"
                    success_msg += "\n  cs --help   # 查看帮助"
                    
                    return success_msg
                else:
                    return f"✅ Shell 集成已存在，配置文件: {wrapper_file}"
            else:
                with open(shell_config, 'w') as f:
                    f.write(f'\n# Claude Switch - 自动环境变量生效\n{source_line}\n')
                
                success_msg = f"✅ 已创建配置文件 {shell_config}"
                if cs_found:
                    success_msg += f"\n✅ 检测到 claude-switch 命令: {cs_command}"
                else:
                    success_msg += "\n⚠️  尚未检测到 claude-switch 命令，请确保已安装"
                
                success_msg += f"\n📁 Shell 配置文件: {wrapper_file}"
                success_msg += "\n🔄 请重启终端或运行: source ~/.claude-switch/cs-wrapper.sh"
                
                return success_msg
                
        except Exception as e:
            return f"❌ 初始化失败: {e}\n💡 请检查文件权限或手动添加配置"

    def update_env_file(self):
        """更新环境变量文件"""
        credentials = self.get_current_active_credentials()
        if not credentials:
            return

        with open(self.config_dir / 'env.sh', 'w') as f:
            f.write('# Claude Switch Environment Variables\n')
            f.write('# This file is auto-generated by claude-switch\n')
            f.write('# Run: source ~/.claude-switch/env.sh\n')
            f.write('# Or use: eval $(cs current --export)\n\n')
            f.write(f'export ANTHROPIC_BASE_URL="{credentials["base_url"]}"\n')
            f.write(
                f'export ANTHROPIC_AUTH_TOKEN="{credentials["auth_token"]}"\n')
            f.write(f'export ANTHROPIC_API_KEY="{credentials["api_key"]}"\n')

    def print_current_export(self) -> str:
        """打印当前配置的环境变量设置命令"""
        credentials = self.get_current_active_credentials()
        if not credentials:
            return ""

        commands = []
        commands.append(
            f'export ANTHROPIC_BASE_URL="{credentials["base_url"]}"')
        commands.append(
            f'export ANTHROPIC_AUTH_TOKEN="{credentials["auth_token"]}"')
        commands.append(f'export ANTHROPIC_API_KEY="{credentials["api_key"]}"')
        return "\n".join(commands)
