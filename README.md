# 🐭 Linux 小老鼠闯关（linux_tutor）

一个零依赖的终端小游戏：运行后会出现一只 ASCII 小老鼠，用**字幕**引导你逐条练习 Ubuntu/Linux 最常用的基本指令。内置虚拟文件系统——**敲错、敲砸都不会影响你的真电脑**，放心折腾。

## 玩法（3 步上手）

```bash
# 1. 拿到代码（二选一）
git clone https://github.com/<你的用户名>/linux_tutor.git   # 方式一：克隆仓库
# 或在 GitHub 页面点 Code → Download ZIP 后解压           # 方式二：直接下载

# 2. 进入目录
cd linux_tutor

# 3. 运行
python3 linux_tutor.py        # Ubuntu / macOS
python linux_tutor.py         # Windows（需已安装 Python）
```

> 没装 Python？Ubuntu 上执行 `sudo apt install python3` 即可（一般自带）。

## 玩法说明

- 开局是一只 ASCII 小老鼠，然后逐关出现黄色**字幕框**，例如：

  ```
  ┌──────────────────────────────────────────────────────────┐
  │ 【字幕】请输入：cd ~                                     │
  └──────────────────────────────────────────────────────────┘
  mouse@ubuntu:~$ _
  ```

- 照着字幕敲命令、回车：敲对打 ✔、给讲解、进度条 +1，进入下一关
- 15 关覆盖：`pwd` `ls` `cd ~` `mkdir` `cd` `touch` `echo "..." >` `cat` `cp` `mv` `rm` `cd ..` `rm -r` `whoami` `clear`
- 敲错 3 次会直接亮出答案；输入 `skip` 跳关，`help` 查看帮助，`exit` 退出
- 通关后进入**自由练习模式**，虚拟文件系统随便玩，`exit` 退出

## 安全性

所有命令都在程序内的**虚拟沙箱**里执行，不会触碰你的真实文件系统，Windows 上也能先体验。

## License

MIT
