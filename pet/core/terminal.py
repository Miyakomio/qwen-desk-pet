"""终端命令执行：在新终端窗口中运行命令。"""
import subprocess
import sys


def run_in_terminal(command: str) -> bool:
    """在新开的终端窗口执行命令，成功返回 True。

    用户直接调用终端，可自行决定输入的内容与风险。
    """
    if not command or not command.strip():
        return False
    try:
        if sys.platform == "win32":
            flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            # cmd /k 执行后保持窗口打开，方便查看输出
            subprocess.Popen(
                ["cmd", "/k", command.strip()],
                creationflags=flags,
            )
        else:
            # Linux/mac 常见终端
            try:
                subprocess.Popen(
                    ["x-terminal-emulator", "-e", "bash", "-c", command.strip()]
                )
            except FileNotFoundError:
                subprocess.Popen(["bash", "-c", f"echo; {command.strip()}; echo; read -p 'Press Enter to close'"])
        return True
    except Exception:  # noqa: BLE001
        return False
