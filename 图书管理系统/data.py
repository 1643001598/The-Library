"""书架上的三本书。

注意这里没有任何排版代码：排版是书自己的事（render_page），
这里只负责把真实内容填进 Page 里。
"""

from models import Page, PythonBook, ROS2Book, UbuntuBook


def build_books():
    """造出三本书，返回列表。"""

    python_book = PythonBook(
        isbn="PY-001",
        title="Python 学习手册",
        author="教程组",
        year=2025,
        pages=[
            Page(1, "变量只是名字", [
                "x = 1",
                "y = x",
                "x = 2",
                "print(y)   # 1",
                "赋值不是复制，而是给同一个对象再起一个名字",
            ]),
            Page(2, "切片", [
                's = "python"',
                "print(s[1:4])   # yth",
                "切片含头不含尾：s[start:stop:step]",
                "步长为 -1 时可以倒着取整句",
            ]),
            Page(3, "列表推导式", [
                "squares = [x * x for x in range(5)]",
                "print(squares)   # [0, 1, 4, 9, 16]",
                "推导式 = 一个循环 + 一个表达式 + 一个结果列表",
            ]),
            Page(4, "类与对象", [
                "class Book:",
                "    def __init__(self, title):",
                "        self.title = title",
                "self 就是“这个对象自己”，调用时由解释器自动传入",
            ]),
            Page(5, "异常处理", [
                "try:",
                '    number = int("3.5")',
                "except ValueError:",
                '    print("这不是整数")',
                "只捕获你真正能处理的那几种异常",
            ]),
        ],
    )

    ros2_book = ROS2Book(
        isbn="ROS2-001",
        title="ROS2 实战",
        author="机器人社",
        year=2024,
        pages=[
            Page(1, "节点 node", [
                "ros2 run demo_nodes_cpp talker",
                "一个节点只负责一件事，节点之间通过接口通信",
            ]),
            Page(2, "话题 topic", [
                "ros2 topic list",
                "ros2 topic echo /chatter",
                "发布者持续发，订阅者按需收，是一对多的广播",
            ]),
            Page(3, "服务 service", [
                'ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"',
                "服务是请求—应答，调用方会阻塞等待结果",
            ]),
            Page(4, "launch 与参数", [
                "ros2 launch my_pkg bringup.launch.py",
                "参数写在 yaml 里，launch 文件负责一次性拉起多个节点",
            ]),
            Page(5, "colcon 构建", [
                "colcon build --symlink-install",
                "source install/setup.bash",
                "改了代码要先重新构建，再 source 才生效",
            ]),
        ],
    )

    ubuntu_book = UbuntuBook(
        isbn="UBT-001",
        title="Ubuntu 从入门到入土",
        author="运维组",
        year=2023,
        pages=[
            Page(1, "apt 装软件", [
                "sudo apt update",
                "sudo apt install git",
                "先更新索引再安装，否则可能装到旧版本",
            ]),
            Page(2, "文件与权限", [
                "ls -l",
                "chmod +x run.sh",
                "r 读、w 写、x 执行，三位一组分别对应所有者、组、其他人",
            ]),
            Page(3, "systemd 服务", [
                "systemctl status ssh",
                "systemctl enable --now ssh",
                "enable 管开机自启，start 管当前这次运行",
            ]),
            Page(4, "ssh 远程登录", [
                "ssh user@192.168.1.10",
                "ssh-keygen -t ed25519",
                "把公钥放到服务器上，就不用每次输密码了",
            ]),
            Page(5, "磁盘与分区", [
                "df -h",
                "lsblk",
                "sudo mount /dev/sdb1 /mnt",
                "卸载用 umount，卸载前先退出该目录",
            ]),
        ],
    )

    return [python_book, ros2_book, ubuntu_book]
