import tkinter as tk
import random
import math

radius = 30
score = 0  # Счётчик

def update_canvas_size(event):
    """Обновляет размеры холста при изменении размера окна"""
    global canvas_width, canvas_height
    canvas_width = event.width
    canvas_height = event.height

def pulse_text(item_id, scale_start, scale_end, steps, current_step=0):
    """
    Функция для анимации пульсации текста.
    item_id: ID элемента текста на канвасе
    scale_start: начальный масштаб
    scale_end: конечный масштаб
    steps: количество шагов анимации
    current_step: текущий шаг (для рекурсии)
    """
    # Вычисляем текущий масштаб линейной интерполяцией
    progress = current_step / steps
    current_scale = scale_start + (scale_end - scale_start) * progress
    
    # Применяем масштаб к тексту
    # Мы не меняем сам текст, а меняем его координаты/размер через coords или просто перерисовываем,
    # но проще всего использовать itemconfig для шрифта, если бы мы использовали Label.
    # Для Canvas text проще менять координаты ограничивающего прямоугольника или использовать scale.
    # Однако, Canvas.scale меняет координаты всех элементов. 
    # Чтобы анимировать только текст, мы будем пересчитывать координаты текста вручную.
    
    x_center = canvas_width // 2
    y_center = canvas_height // 2
    
    # Базовый размер шрифта (можно вынести в переменную)
    base_font_size = 40
    new_font_size = int(base_font_size * current_scale)
    
    # Обновляем шрифт текста
    canvas.itemconfig(item_id, font=("Arial", new_font_size, "bold"))
    
    # Центрируем текст заново (так как размер изменился, центр мог сместиться визуально)
    # Получаем текущие координаты
    coords = canvas.coords(item_id)
    if coords:
        # coords возвращает (x1, y1, x2, y2) для текста это bounding box
        # Но проще задать новые координаты центра явно, если мы знаем, что текст центрирован
        # В Tkinter Canvas text coords - это координаты точки привязки (обычно верхний левый угол или центр, зависит от anchor)
        # Мы установили anchor=CENTER, поэтому coords возвращает центр.
        canvas.coords(item_id, x_center, y_center)

    if current_step < steps:
        # Планируем следующий кадр анимации
        root.after(20, pulse_text, item_id, scale_start, scale_end, steps, current_step + 1)
    elif current_step == steps and scale_end < scale_start:
        # Если мы дошли до конца уменьшения, можно вернуть базовый размер окончательно
        canvas.itemconfig(item_id, font=("Arial", 40, "bold"))
        canvas.coords(item_id, canvas_width // 2, canvas_height // 2)

def move_circle(event):
    global score
    
    # Получаем текущие координаты круга
    coords = canvas.coords(circle)
    if not coords:
        return
        
    x1, y1, x2, y2 = coords
    
    # Вычисляем центр текущего круга
    current_center_x = (x1 + x2) / 2
    current_center_y = (y1 + y2) / 2

    # Проверяем, находится ли клик внутри круга
    distance = math.sqrt(
        (event.x - current_center_x) ** 2 + 
        (event.y - current_center_y) ** 2
    )

    if distance > radius:
        return  # Если клик вне круга — ничего не делаем

    # 1. Увеличиваем счётчик
    score += 1
    
    # 2. Обновляем текст счётчика
    canvas.itemconfig(score_text, text=str(score))
    
    # 3. Запускаем анимацию пульсации (увеличение до 1.5, уменьшение до 1.0, 15 шагов)
    pulse_text(score_text, 1.0, 1.7, 2)      # Рост
    root.after(40, lambda: pulse_text(score_text, 1.7, 1.0, 3)) # Падение (запускается через 160мс)

    # 4. Перемещаем круг в случайное место
    x = random.randint(radius, canvas_width - radius)
    y = random.randint(radius, canvas_height - radius)

    canvas.coords(circle, x - radius, y - radius, x + radius, y + radius)

# Создаём окно
root = tk.Tk()
root.title("Обучение для mouseless, keynav и прочих альтернатив мыши")

# Получаем ширину и высоту экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Устанавливаем размер окна равным размеру экрана
root.geometry(f"{screen_width}x{screen_height}")

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

# Холст (Canvas) на всё окно
hex_color = rgb_to_hex(251, 243, 219)
canvas = tk.Canvas(root, bg=hex_color)
canvas.pack(fill=tk.BOTH, expand=True)

# Отслеживание размера
canvas.bind("<Configure>", update_canvas_size)

# Рисуем начальный круг
circle = canvas.create_oval(
    screen_width // 2 - radius, 
    screen_height // 2 - radius,
    screen_width // 2 + radius, 
    screen_height // 2 + radius,
    fill="lightGreen"
)

# --- ДОБАВЛЕНО: Создание счётчика ---
# Создаем текст по центру. anchor=CENTER делает так, что координаты (x,y) - это центр текста.
score_text = canvas.create_text(
    screen_width // 2, 
    screen_height // 2, 
    text=str(score), 
    font=("Arial", 40, "bold"), 
    fill="black",
    anchor="center"
)

# Привязываем клик по холсту к перемещению
canvas.bind("<Button-1>", move_circle)

root.mainloop()
