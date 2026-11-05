import psutil

target_process_name = "AutoHotkey64.exe"
target_substring = "Colemak-and-more.ahk"
extra_process_name = "Colemak-and-more.exe"  # дополнительный процесс

for proc in psutil.process_iter(['name', 'cmdline']):
    try:
        proc_name = proc.info['name']
        
        # Проверяем либо основной процесс с подстрокой, либо дополнительный
        if proc_name != target_process_name and proc_name != extra_process_name:
            continue

        # Для AutoHotkey дополнительно проверяем подстроку в командной строке
        if proc_name == target_process_name:
            cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
            if target_substring not in cmdline:
                continue

        print(f"Нашёл процесс PID={proc.pid} ({proc_name}), закрываю...")
        proc.terminate()
        # Если нужно принудительно завершить, раскомментируйте строку ниже:
        # proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        # Процесс мог завершиться до проверки или нет прав — просто пропускаем
        continue

print("Готово.")
