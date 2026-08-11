import os
import subprocess
import time
import sys
from pathlib import Path

ahk_compiler = r"C:\Program Files\AutoHotkey\Compiler\Ahk2Exe.exe"
script_dir = Path(__file__).parent.resolve()

scripts = [
    {
        "ahk": script_dir / "colemak-and-more.ahk",
        "icon": script_dir / "icon.ico",
    },
    {
        "ahk": script_dir / "inactive-state.ahk",
        "icon": script_dir / "inactive.ico",
    },
]

if not os.path.isfile(ahk_compiler):
    print(f"Ошибка: Ahk2Exe не найден по пути {ahk_compiler}")
    exit(1)

total_tasks = len(scripts)
completed_tasks = 0
bar_length = 20

def update_progress(current, total):
    percent = int((current / total) * 100) if total > 0 else 0
    filled_length = int(bar_length * percent // 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # \r возвращает курсор в начало строки, перезаписывая её
    sys.stdout.write(f"\rСтатус: [{bar}] {percent}% ({current}/{total})")
    sys.stdout.flush()

update_progress(0, total_tasks)

for item in scripts:
    completed_tasks += 1
    
    if not item["ahk"].exists():
        print(f"\nПредупреждение: файл {item['ahk']} не найден, пропускаем.")
        update_progress(completed_tasks, total_tasks)
        continue
    
    if not item["icon"].exists():
        print(f"\nПредупреждение: иконка {item['icon']} не найдена, компиляция без иконки.")
        icon_arg = []
    else:
        icon_arg = ["/icon", str(item["icon"])]

    cmd = [
        ahk_compiler,
        "/gui",
        "/in", str(item["ahk"])
    ] + icon_arg

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Ожидание завершения процесса:
    while process.poll() is None:
        time.sleep(0.1) # - Уменьшение нагрузки процессора

    stdout, stderr = process.communicate()
    
    update_progress(completed_tasks, total_tasks)

print("\nВсе задачи завершены.")

