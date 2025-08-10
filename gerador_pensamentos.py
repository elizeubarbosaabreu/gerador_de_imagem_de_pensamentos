"""
Gerador de Imagens de Pensamentos (compatível com Pillow >=10)
Arquivo: gerador_pensamentos.py
Descrição: Aplicativo gráfico (tkinter) que recebe um pensamento, nome do pensador e uma imagem de fundo,
produz uma imagem final 1080x1920 com o fundo desfocado e o texto sobreposto. Inclui rodapé com @elizeu.dev.

Dependências:
  pip install pillow
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageFilter, ImageDraw, ImageFont

OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
OUTPUT_FILENAME = "pensamento_gerado.png"
DEFAULT_FONT_SIZES = {
    'title': 64,
    'author': 40,
    'footer': 28,
}
FONT_PATHS_TO_TRY = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

def find_font(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

FONT_PATH = find_font(FONT_PATHS_TO_TRY)

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap_text_for_font(draw, text, font, max_width):
    words = text.split()
    lines, line = [], words[0] if words else ""
    for w in words[1:]:
        test = f"{line} {w}"
        if get_text_size(draw, test, font)[0] <= max_width:
            line = test
        else:
            lines.append(line)
            line = w
    lines.append(line)
    return lines

def create_image(thought, author, bg_path, output_path=OUTPUT_FILENAME):
    bg = Image.open(bg_path).convert('RGB')
    bg_ratio = bg.width / bg.height
    target_ratio = OUTPUT_WIDTH / OUTPUT_HEIGHT
    if bg_ratio > target_ratio:
        new_height = OUTPUT_HEIGHT
        new_width = int(bg_ratio * new_height)
    else:
        new_width = OUTPUT_WIDTH
        new_height = int(new_width / bg_ratio)
    bg_resized = bg.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - OUTPUT_WIDTH) // 2
    top = (new_height - OUTPUT_HEIGHT) // 2
    bg_cropped = bg_resized.crop((left, top, left + OUTPUT_WIDTH, top + OUTPUT_HEIGHT))
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=10))
    canvas = Image.new('RGB', (OUTPUT_WIDTH, OUTPUT_HEIGHT))
    canvas.paste(bg_blurred)
    draw = ImageDraw.Draw(canvas)
    if FONT_PATH:
        title_font = ImageFont.truetype(FONT_PATH, DEFAULT_FONT_SIZES['title'])
        author_font = ImageFont.truetype(FONT_PATH, DEFAULT_FONT_SIZES['author'])
        footer_font = ImageFont.truetype(FONT_PATH, DEFAULT_FONT_SIZES['footer'])
    else:
        title_font = author_font = footer_font = ImageFont.load_default()
    margin_x, margin_y_top, margin_y_bottom = 80, 160, 220
    text_area_width = OUTPUT_WIDTH - 2 * margin_x
    text_area_height = OUTPUT_HEIGHT - margin_y_top - margin_y_bottom
    rectangle = Image.new('RGBA', (text_area_width + 40, text_area_height + 40), (0, 0, 0, 120))
    canvas.paste(rectangle, (margin_x - 20, margin_y_top - 20), rectangle)
    max_title_size, min_title_size, wrapped_lines = 110, 30, None
    for size in range(max_title_size, min_title_size - 1, -2):
        font = ImageFont.truetype(FONT_PATH, size) if FONT_PATH else ImageFont.load_default()
        lines = wrap_text_for_font(draw, thought, font, text_area_width - 40)
        total_height = sum([get_text_size(draw, line, font)[1] + 8 for line in lines])
        if total_height <= text_area_height - 120:
            wrapped_lines, title_font = lines, font
            break
    if wrapped_lines is None:
        title_font = ImageFont.truetype(FONT_PATH, min_title_size) if FONT_PATH else ImageFont.load_default()
        wrapped_lines = wrap_text_for_font(draw, thought, title_font, text_area_width - 40)
    line_height = get_text_size(draw, 'Ay', title_font)[1] + 8
    total_text_height = line_height * len(wrapped_lines)
    current_y = margin_y_top + (text_area_height - total_text_height) // 2
    for line in wrapped_lines:
        w, _ = get_text_size(draw, line, title_font)
        x = (OUTPUT_WIDTH - w) // 2
        draw.text((x + 2, current_y + 2), line, font=title_font, fill=(0, 0, 0, 180))
        draw.text((x, current_y), line, font=title_font, fill=(255, 255, 255))
        current_y += line_height
    author_text = f"— {author}"
    aw, ah = get_text_size(draw, author_text, author_font)
    ax, ay = (OUTPUT_WIDTH - aw) // 2, current_y + 20
    draw.text((ax + 1, ay + 1), author_text, font=author_font, fill=(0, 0, 0, 180))
    draw.text((ax, ay), author_text, font=author_font, fill=(240, 240, 240))
    footer_text = "@elizeu.dev"
    fw, fh = get_text_size(draw, footer_text, footer_font)
    fx, fy = (OUTPUT_WIDTH - fw) // 2, OUTPUT_HEIGHT - 60
    draw.text((fx + 1, fy + 1), footer_text, font=footer_font, fill=(0, 0, 0, 180))
    draw.text((fx, fy), footer_text, font=footer_font, fill=(255, 255, 255))
    canvas.save(output_path, format='PNG')
    return output_path

class App:
    def __init__(self, root):
        self.root, self.bg_path = root, None
        root.title('Gerador de Pensamentos - @elizeu.dev')
        root.geometry('720x480')
        tk.Label(root, text='Pensamento:').pack(anchor='w', padx=10, pady=(10, 0))
        self.text_entry = tk.Text(root, height=8)
        self.text_entry.pack(fill='x', padx=10)
        frame = tk.Frame(root)
        frame.pack(fill='x', padx=10, pady=8)
        tk.Label(frame, text='Nome do pensador:').pack(side='left')
        self.author_var = tk.Entry(frame)
        self.author_var.pack(side='left', fill='x', expand=True, padx=(8, 0))
        frame2 = tk.Frame(root)
        frame2.pack(fill='x', padx=10, pady=8)
        self.bg_label = tk.Label(frame2, text='Nenhuma imagem selecionada')
        self.bg_label.pack(side='left')
        tk.Button(frame2, text='Selecionar imagem de fundo', command=self.select_background).pack(side='right')
        frame3 = tk.Frame(root)
        frame3.pack(fill='x', padx=10, pady=8)
        tk.Button(frame3, text='Gerar imagem', command=self.on_generate).pack(side='left')
        tk.Button(frame3, text='Sair', command=root.quit).pack(side='right')

    def select_background(self):
        path = filedialog.askopenfilename(title='Selecione a imagem de fundo', filetypes=[('Imagens', '*.png *.jpg *.jpeg *.webp'), ('Todos', '*.*')])
        if path:
            self.bg_path = path
            self.bg_label.config(text=os.path.basename(path))

    def on_generate(self):
        thought = self.text_entry.get('1.0', 'end').strip()
        author = self.author_var.get().strip() or 'Anônimo'
        if not thought:
            messagebox.showwarning('Atenção', 'Por favor, insira o pensamento.')
            return
        if not self.bg_path:
            messagebox.showwarning('Atenção', 'Por favor, selecione uma imagem de fundo.')
            return
        save_path = filedialog.asksaveasfilename(defaultextension='.png', initialfile=OUTPUT_FILENAME, filetypes=[('PNG', '*.png')], title='Salvar imagem como')
        if not save_path:
            return
        try:
            result = create_image(thought, author, self.bg_path, output_path=save_path)
            messagebox.showinfo('Sucesso', f'Imagem gerada e salva em:\n{result}')
        except Exception as e:
            messagebox.showerror('Erro', str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
