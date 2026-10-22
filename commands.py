"""Команды эмулятора."""
from vfs import VFS, Node


class CommandError(Exception):
    """Ошибка выполнения команды."""
    pass


def cmd_ls(vfs: VFS, args: list[str]) -> str:
    path = args[0] if args else "."
    node = vfs.resolve_path(path)

    if not node:
        raise CommandError(f"ls: {path}: No such file or directory")
    if not node.is_dir:
        return node.name

    items = sorted(node.children.keys())
    return "  ".join(items) if items else ""


def cmd_cd(vfs: VFS, args: list[str]) -> str:
    if len(args) != 1:
        raise CommandError("cd: неверное число аргументов")

    path = args[0]
    node = vfs.resolve_path(path)

    if not node:
        raise CommandError(f"cd: {path}: No such file or directory")
    if not node.is_dir:
        raise CommandError(f"cd: {path}: Not a directory")

    vfs.cwd = node
    return ""


def cmd_rev(vfs: VFS, args: list[str]) -> str:
    if not args:
        raise CommandError("rev: не указан аргумент")
    return " ".join(arg[::-1] for arg in args)


def cmd_whoami(vfs: VFS, args: list[str]) -> str:
    if args:
        raise CommandError("whoami: неверное число аргументов")
    return "root"


def cmd_tac(vfs: VFS, args: list[str]) -> str:
    if not args:
        raise CommandError("tac: не указан файл")
    path = args[0]
    node = vfs.resolve_path(path)
    if not node:
        raise CommandError(f"tac: {path}: No such file or directory")
    if node.is_dir:
        raise CommandError(f"tac: {path}: Is a directory")
    lines = node.content.splitlines()
    return "\n".join(reversed(lines))


def cmd_mkdir(vfs: VFS, args: list[str]) -> str:
    if not args:
        raise CommandError("mkdir: не указано имя директории")
    for name in args:
        if "/" in name or name in (".", ".."):
            raise CommandError(f"mkdir: недопустимое имя: {name}")
        if name in vfs.cwd.children:
            raise CommandError(f"mkdir: {name}: File exists")
        new_node = Node(name=name, is_dir=True)
        new_node.parent = vfs.cwd
        vfs.cwd.children[name] = new_node
    return ""


def cmd_rm(vfs: VFS, args: list[str]) -> str:
    if not args:
        raise CommandError("rm: не указан файл")
    for path in args:
        node = vfs.resolve_path(path)
        if not node:
            raise CommandError(f"rm: {path}: No such file or directory")
        if node.parent is None:
            raise CommandError(f"rm: {path}: cannot remove root")
        del node.parent.children[node.name]
    return ""


def cmd_help(vfs: VFS, args: list[str]) -> str:
    return (
        "Доступные команды:\n"
        "  ls [path]      — список файлов и папок\n"
        "  cd <path>      — переход в директорию\n"
        "  mkdir <name>   — создать директорию\n"
        "  rm <path>      — удалить файл или директорию\n"
        "  rev <text>     — перевернуть строку\n"
        "  tac <file>     — вывести файл построчно с конца\n"
        "  whoami         — имя текущего пользователя\n"
        "  echo <text>    — вывести аргументы\n"
        "  help           — этот список\n"
        "  exit           — выход"
    )