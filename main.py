"""Эмулятор оболочки ОС с VFS. Вариант №12. Этап 5."""
import argparse

from commands import (
    CommandError,
    cmd_cd,
    cmd_help,
    cmd_ls,
    cmd_mkdir,
    cmd_rev,
    cmd_rm,
    cmd_tac,
    cmd_whoami,
)
from parser import parse
from vfs import VFS


def execute(vfs: VFS, line: str) -> bool:
    """Выполняет одну команду. Возвращает False, если нужно выйти."""
    tokens = parse(line)
    if not tokens:
        return True

    cmd, args = tokens[0], tokens[1:]
    try:
        if cmd == "exit":
            return False
        elif cmd == "ls":
            print(cmd_ls(vfs, args))
        elif cmd == "cd":
            print(cmd_cd(vfs, args))
        elif cmd == "echo":
            print(" ".join(args))
        elif cmd == "rev":
            print(cmd_rev(vfs, args))
        elif cmd == "whoami":
            print(cmd_whoami(vfs, args))
        elif cmd == "tac":
            print(cmd_tac(vfs, args))
        elif cmd == "mkdir":
            print(cmd_mkdir(vfs, args))
        elif cmd == "rm":
            print(cmd_rm(vfs, args))
        elif cmd == "help":
            print(cmd_help(vfs, args))
        else:
            raise CommandError(f"{cmd}: команда не найдена")
    except CommandError as e:
        print(f"Ошибка: {e}")
        return False
    return True


def repl(vfs: VFS, script_path: str | None = None):
    """Цикл REPL. Если передан script_path — выполняет его."""
    if script_path:
        run_script(vfs, script_path)
        return

    while True:
        try:
            line = input(f"{vfs.name}:~$ ")
        except EOFError:
            break
        if not execute(vfs, line):
            break


def run_script(vfs: VFS, script_path: str):
    """Выполняет стартовый скрипт. Поддерживает комментарии (#)."""
    print(f"--- Запуск скрипта: {script_path} ---")
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                print(f"{vfs.name}:~$ {line}")
                if not execute(vfs, line):
                    print("--- Скрипт остановлен из-за ошибки ---")
                    return
        print("--- Скрипт успешно завершён ---")
    except FileNotFoundError:
        print(f"Ошибка: файл скрипта '{script_path}' не найден")


def main():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС с VFS")
    parser.add_argument("--vfs", type=str, help="Путь к XML-файлу VFS")
    parser.add_argument("--script", type=str, help="Путь к стартовому скрипту")
    args = parser.parse_args()

    print(f"DEBUG: Запуск эмулятора")
    print(f"DEBUG: VFS path = {args.vfs}")
    print(f"DEBUG: Script path = {args.script}")

    vfs_name = args.vfs.split("/")[-1].split("\\")[-1].replace(".xml", "") if args.vfs else "vfs"
    vfs = VFS(name=vfs_name)

    if args.vfs:
        try:
            vfs.load_from_xml(args.vfs)
            print(f"DEBUG: VFS успешно загружена из {args.vfs}")
        except FileNotFoundError as e:
            print(f"ОШИБКА: {e}")
            return
        except ValueError as e:
            print(f"ОШИБКА: {e}")
            return

        motd = vfs.root.children.get("motd")
        if motd and not motd.is_dir:
            print(f"--- motd ---")
            print(motd.content)
            print(f"------------")

    repl(vfs, script_path=args.script)


if __name__ == "__main__":
    main()