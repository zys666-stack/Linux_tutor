#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux 小老鼠闯关 —— 鼠标(老鼠)带你熟悉 Ubuntu 基本指令
运行方式：
    Ubuntu :  python3 linux_tutor.py
    Windows:  python linux_tutor.py
特性：
    * 开机显示 ASCII 小老鼠
    * 字幕式关卡引导（例如：请输入 cd ~ —— 返回主目录）
    * 内置虚拟文件系统，敲错敲砸都不影响真实电脑
    * 每关有讲解、错误提示，3 次不会可跳过
    * 通关后进入自由练习模式，输入 exit 退出
"""

import os
import sys
import time
import datetime
import random

# ---------- 让 Windows 终端支持 ANSI 颜色 ----------
if os.name == "nt":
    os.system("")

C = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}


def c(text, color):
    return C.get(color, "") + text + C["reset"]


def slow_print(text, delay=0.012):
    for ch in text:
        print(ch, end="", flush=True)
        if delay:
            time.sleep(delay)
    print()


def banner():
    mouse = r"""
      (\_._/)
      ( o o )        "Hi! I'm Little Mouse."
       (  V  )        Let me teach you Linux,
      / |     | \     one command at a time!
     (_/  \__/ \_)
        ^^    ^^
"""
    colors = ["cyan", "magenta", "yellow", "green"]
    for i, line in enumerate(mouse.split("\n")):
        print(c(line.center(60), colors[i % len(colors)]))
        time.sleep(0.08)
    print()
    print(c("=" * 62, "blue"))
    print(c("Linux 小老鼠闯关 · Ubuntu 基本指令训练".center(50), "bold" + "white"))
    print(c("=" * 62, "blue"))
    print(c("提示：内置虚拟文件系统，随便折腾也不会弄坏真电脑。", "dim"))
    print(c("随时可输入 help 查看帮助，skip 跳过当前关，exit 退出。", "dim"))
    print()


MOUSE_HOME = "/home/mouse"  # 虚拟主目录


class VirtualFS:
    def __init__(self):
        # 目录用 dict 表示，文件用 str 表示
        self.root = {
            "home": {
                "mouse": {"welcome.txt": "Hello from Ubuntu!\n"},
                "other": {},
            },
            "etc": {"os-release": 'NAME="Ubuntu"\n'},
            "tmp": {},
            "var": {"log": {}},
        }
        self.cwd = ["home", "mouse"]

    # ---------- 路径工具 ----------
    def resolve(self, path):
        """把用户输入的路径解析成绝对路径分量列表（不保证存在）。"""
        if path in ("~", "~/"):
            parts = ["home", "mouse"]
        elif path.startswith("~/"):
            parts = ["home", "mouse"] + path[2:].split("/")
        elif path.startswith("/"):
            parts = path[1:].split("/")
        else:
            parts = self.cwd + path.split("/")
        out = []
        for p in parts:
            if p in ("", "."):
                continue
            if p == "..":
                if out:
                    out.pop()
                continue
            out.append(p)
        return out

    def node_at(self, parts):
        node = self.root
        for p in parts:
            if not isinstance(node, dict) or p not in node:
                return None
            node = node[p]
        return node

    def is_dir(self, parts):
        return isinstance(self.node_at(parts), dict)

    def abspath(self, parts=None):
        parts = parts if parts is not None else self.cwd
        return "/" + "/".join(parts) if parts else "/"

    def prompt(self):
        short = "~" if self.abspath().startswith(MOUSE_HOME) else self.abspath()
        rest = self.abspath()[len(MOUSE_HOME):] if short == "~" else ""
        return c("mouse@ubuntu", "green") + c(":", "white") + c(short + rest, "blue") + c("$ ", "white")

    # ---------- 命令实现（返回输出文本；抛 ValueError 作为错误） ----------
    def run(self, line):
        line = line.strip()
        if not line:
            return ""
        tokens = line.split()
        cmd, args = tokens[0], tokens[1:]

        if cmd == "pwd":
            return self.abspath()

        if cmd == "ls":
            target = self.resolve(args[-1]) if args and not args[-1].startswith("-") else self.cwd
            node = self.node_at(target)
            if node is None:
                raise ValueError("ls: cannot access '%s': No such file or directory" % args[-1])
            if isinstance(node, str):
                return args[-1]
            entries = sorted(node.keys())
            flags = [a for a in args if a.startswith("-")]
            if "-a" in flags or "-la" in flags or "-al" in flags:
                entries = ["."] + [".."] + entries
            return "  ".join((e + "/" if isinstance(node[e], dict) else e) for e in entries) if entries else "(空目录)"

        if cmd == "cd":
            target = args[0] if args else "~"
            parts = self.resolve(target)
            if self.node_at(parts) is None:
                raise ValueError("cd: no such file or directory: %s" % target)
            if not self.is_dir(parts):
                raise ValueError("cd: not a directory: %s" % target)
            self.cwd = parts
            return ""

        if cmd == "mkdir":
            if not args:
                raise ValueError("mkdir: missing operand")
            for name in args:
                parts = self.resolve(name)
                parent = self.node_at(parts[:-1])
                if parent is None or not isinstance(parent, dict):
                    raise ValueError("mkdir: cannot create directory '%s': No such file or directory" % name)
                if parts[-1] in parent:
                    raise ValueError("mkdir: cannot create directory '%s': File exists" % name)
                parent[parts[-1]] = {}
            return ""

        if cmd == "touch":
            if not args:
                raise ValueError("touch: missing file operand")
            for name in args:
                parts = self.resolve(name)
                parent = self.node_at(parts[:-1])
                if parent is None or not isinstance(parent, dict):
                    raise ValueError("touch: cannot touch '%s': No such file or directory" % name)
                if parts[-1] not in parent:
                    parent[parts[-1]] = ""
            return ""

        if cmd == "echo":
            # 支持 echo xxx > file / echo "xxx" > file
            if ">" in args:
                i = args.index(">")
                text = " ".join(args[:i]).strip('"')
                if i + 1 >= len(args):
                    raise ValueError("bash: syntax error near unexpected token `newline'")
                fname = args[i + 1]
                parts = self.resolve(fname)
                parent = self.node_at(parts[:-1])
                if parent is None or not isinstance(parent, dict):
                    raise ValueError("bash: %s: No such file or directory" % fname)
                parent[parts[-1]] = text + "\n"
                return ""
            return " ".join(args).strip('"')

        if cmd == "cat":
            if not args:
                raise ValueError("cat: missing operand")
            out = []
            for name in args:
                node = self.node_at(self.resolve(name))
                if node is None:
                    raise ValueError("cat: %s: No such file or directory" % name)
                if isinstance(node, dict):
                    raise ValueError("cat: %s: Is a directory" % name)
                out.append(node)
            return "\n".join(out).rstrip("\n")

        if cmd == "cp":
            if len(args) < 2:
                raise ValueError("cp: missing destination file operand")
            src = self.node_at(self.resolve(args[0]))
            if src is None:
                raise ValueError("cp: cannot stat '%s': No such file or directory" % args[0])
            import copy as _copy
            dst_parts = self.resolve(args[1])
            if self.is_dir(dst_parts):
                dst_parts = dst_parts + [args[0].rstrip("/").split("/")[-1]]
            parent = self.node_at(dst_parts[:-1])
            if parent is None or not isinstance(parent, dict):
                raise ValueError("cp: cannot create '%s': No such file or directory" % args[1])
            parent[dst_parts[-1]] = _copy.deepcopy(src)
            return ""

        if cmd == "mv":
            if len(args) < 2:
                raise ValueError("mv: missing destination file operand")
            src_parts = self.resolve(args[0])
            src_parent = self.node_at(src_parts[:-1])
            if src_parent is None or src_parts[-1] not in src_parent:
                raise ValueError("mv: cannot stat '%s': No such file or directory" % args[0])
            node = src_parent.pop(src_parts[-1])
            dst_parts = self.resolve(args[1])
            if self.is_dir(dst_parts):
                dst_parts = dst_parts + [src_parts[-1]]
            dst_parent = self.node_at(dst_parts[:-1])
            if dst_parent is None or not isinstance(dst_parent, dict):
                raise ValueError("mv: cannot move to '%s': No such file or directory" % args[1])
            dst_parent[dst_parts[-1]] = node
            return ""

        if cmd == "rm":
            flags = [a for a in args if a.startswith("-")]
            names = [a for a in args if not a.startswith("-")]
            recursive = any(f.strip("-") and ("r" in f or "R" in f) for f in flags)
            if not names:
                raise ValueError("rm: missing operand")
            for name in names:
                parts = self.resolve(name)
                parent = self.node_at(parts[:-1])
                if parent is None or parts[-1] not in parent:
                    raise ValueError("rm: cannot remove '%s': No such file or directory" % name)
                if isinstance(parent[parts[-1]], dict) and not recursive:
                    raise ValueError("rm: cannot remove '%s': Is a directory (use -r)" % name)
                del parent[parts[-1]]
            return ""

        if cmd == "rmdir":
            if not args:
                raise ValueError("rmdir: missing operand")
            for name in args:
                parts = self.resolve(name)
                parent = self.node_at(parts[:-1])
                node = self.node_at(parts)
                if node is None:
                    raise ValueError("rmdir: failed to remove '%s': No such file or directory" % name)
                if not isinstance(node, dict):
                    raise ValueError("rmdir: failed to remove '%s': Not a directory" % name)
                if node:
                    raise ValueError("rmdir: failed to remove '%s': Directory not empty" % name)
                del parent[parts[-1]]
            return ""

        if cmd == "clear":
            print("\033[2J\033[H", end="")
            return ""

        if cmd == "whoami":
            return "mouse"

        if cmd == "date":
            return datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")

        if cmd == "help":
            return (
                "可用指令：pwd  ls  cd  mkdir  touch  echo  cat  cp  mv  rm  rmdir\n"
                "         clear  whoami  date  help  skip(闯关模式)  exit\n"
                "特殊路径：~ 主目录   .. 上一级   / 根目录"
            )

        raise ValueError("%s: command not found（输入 help 查看可用指令）" % cmd)


# ---------- 关卡设计 ----------
LESSONS = [
    dict(cmds=["pwd"],
         caption="pwd",
         explain="pwd = print working directory，打印当前所在目录。迷路时先敲它！"),
    dict(cmds=["ls", "ls -a"],
         caption="ls",
         explain="ls = list，列出当前目录里的文件和文件夹（带 / 结尾的是目录）。加 -a 还能看到隐藏文件哦。"),
    dict(cmds=["cd ~", "cd"],
         caption="cd ~",
         explain="cd = change directory。~ 代表主目录（home），所以 cd ~ 就是\"回家\"。只敲 cd 也可以回家。"),
    dict(cmds=["mkdir cheese"],
         caption="mkdir cheese",
         explain="mkdir = make directory，新建一个名为 cheese 的文件夹。老鼠要屯奶酪啦！"),
    dict(cmds=["cd cheese"],
         caption="cd cheese",
         explain="cd + 目录名 = 钻进这个文件夹。现在 pwd 一下，你会看到 /home/mouse/cheese。"),
    dict(cmds=["touch note.txt"],
         caption="touch note.txt",
         explain="touch 用来创建一个空文件。注意：文件夹用 mkdir，文件用 touch，别搞混！"),
    dict(cmds=['echo "i love linux" > note.txt', "echo i love linux > note.txt"],
         caption='echo "i love linux" > note.txt',
         explain="echo 是\"复读机\"，> 表示把内容写进文件。这句的意思是：把引号里的话写进 note.txt。"),
    dict(cmds=["cat note.txt"],
         caption="cat note.txt",
         explain="cat 用来查看文件内容。刚才写进去的话，现在被打印出来啦。"),
    dict(cmds=["cp note.txt note_backup.txt"],
         caption="cp note.txt note_backup.txt",
         explain="cp = copy，复制文件。第一个是原件，第二个是副本名。重要文件要备份，好习惯！"),
    dict(cmds=["mv note.txt done.txt"],
         caption="mv note.txt done.txt",
         explain="mv = move，既能\"移动\"也能\"改名\"——这里就是改名：note.txt 变成了 done.txt。"),
    dict(cmds=["rm note_backup.txt"],
         caption="rm note_backup.txt",
         explain="rm = remove，删除文件。注意：rm 删掉就没了，Linux 没有回收站，下手前想清楚！"),
    dict(cmds=["cd .."],
         caption="cd ..",
         explain=".. 代表上一级目录。cd .. 就是\"往回退一步\"。cd ../.. 就是退两步。"),
    dict(cmds=["rm -r cheese", "rm -r cheese/"],
         caption="rm -r cheese",
         explain="删除文件夹要加 -r（recursive，递归），连里面的东西一起删。这是最危险的指令之一！"),
    dict(cmds=["whoami", "date"],
         caption="whoami",
         explain="whoami 告诉你现在是谁（mouse）；date 显示当前时间。最后清个屏：clear，你就毕业啦！"),
    dict(cmds=["clear"],
         caption="clear",
         explain="clear 清空屏幕，世界清清爽爽。恭喜通关！"),
]


def show_caption(text):
    bar = c("┌" + "─" * 58 + "┐", "yellow")
    body = c("│ ", "yellow") + c("【字幕】请输入：", "bold" + "white") + c(text, "bold" + "yellow") + c(" │", "yellow")
    print(bar)
    print(body)
    print(c("└" + "─" * 58 + "┘", "yellow"))


def free_mode(fs):
    print()
    print(c("自由练习模式！虚拟文件系统随便玩，输入 exit 退出。", "bold" + "green"))
    print()
    while True:
        try:
            line = input(fs.prompt()).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line in ("exit", "quit", "logout"):
            break
        try:
            out = fs.run(line)
            if out:
                print(out)
        except ValueError as e:
            print(c(str(e), "red"))
    print()
    print(c(r"   (\_._/)   Byeee~ 每天敲一遍，两周后你就是终端老手！", "magenta"))


def main():
    random.seed()
    banner()
    fs = VirtualFS()
    total = len(LESSONS)

    for i, lesson in enumerate(LESSONS, 1):
        print(c("— 第 %d/%d 关 —" % (i, total), "cyan" + "dim"))
        slow_print(c("小老鼠：", "magenta") + "这一关我们学 " + c(lesson["caption"], "bold" + "cyan"))
        show_caption(lesson["caption"])
        tries = 0
        while True:
            try:
                line = input(fs.prompt()).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                print(c("下次再一起来玩哦！Byeee~", "magenta"))
                return
            if not line:
                continue
            if line in ("exit", "quit"):
                print(c("Byeee~ 记得每天回来敲一遍！", "magenta"))
                return
            if line == "skip":
                print(c("(已跳过) " + lesson["explain"], "dim"))
                break
            if line == "help":
                print(fs.run("help"))
                continue
            # 判定是否命中本关目标
            normalized = " ".join(line.split())
            hit = any(normalized == " ".join(t.split()) for t in lesson["cmds"])
            try:
                out = fs.run(line)
                if out:
                    print(out)
            except ValueError as e:
                print(c(str(e), "red"))
                tries += 1
                continue
            if hit:
                print(c("✔ 正确！", "bold" + "green"))
                slow_print(c("讲解：", "cyan") + lesson["explain"], 0.008)
                bar = "█" * int(20 * i / total) + "░" * (20 - int(20 * i / total))
                print(c("进度 [%s] %d/%d" % (bar, i, total), "green" + "dim"))
                print()
                time.sleep(0.2)
                break
            tries += 1
            if tries >= 3:
                print(c("提示：本关目标就是—— " + lesson["caption"], "yellow"))
            else:
                print(c("命令没问题，但试试字幕里说的那条指令？", "dim"))

    print()
    print(c("★ 通关！你已经掌握了 Ubuntu 最常用的 15 个基本操作 ★", "bold" + "yellow"))
    time.sleep(0.3)
    free_mode(fs)


if __name__ == "__main__":
    main()
