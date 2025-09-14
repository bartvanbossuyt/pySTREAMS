import pygame

class InequalityMatrix:
    def __init__(self, name, side_length, labels, valuelist, pos=(50, 50)):
        self.name = name
        self.side = side_length
        self.labels = list(labels)
        self.n = len(labels)
        self.valuelist = valuelist
        self.pos = pos

        font_size = int(self.side * 0.28)

        # Forceer segoeuisemilight (fallback naar default als niet aanwezig)
        chosen_font = "segoeuisemilight" if "segoeuisemilight" in pygame.font.get_fonts() else pygame.font.get_default_font()
        print(f"✅ Font geselecteerd: {chosen_font}")

        self.font_regular = pygame.font.SysFont(chosen_font, font_size, bold=False, italic=False)
        self.font_italic = pygame.font.SysFont(chosen_font, font_size, bold=False, italic=True)

    def draw(self, surface):
        x0, y0 = self.pos
        grid_left = x0 + self.side
        grid_top = y0 + self.side
        grid_width = self.side * self.n
        grid_height = self.side * self.n

        for row in range(self.n + 1):
            for col in range(self.n + 1):
                rect = pygame.Rect(
                    x0 + col * self.side,
                    y0 + row * self.side,
                    self.side,
                    self.side
                )

                text = None
                color = (255, 255, 255)

                # Labels en kleuren
                if row == 0 and col == 0:
                    text = self.name
                elif row == 0 and col > 0:
                    text = self.labels[col - 1]
                elif col == 0 and row > 0:
                    text = self.labels[row - 1]
                elif row == col and row > 0:
                    color = (230, 230, 230)
                elif col > row and row > 0:
                    value = self.valuelist[row - 1][col - 1]
                    if value == -1:
                        color = (255, 0,0)
                    elif value == 0:
                        color = (255, 255, 0)
                    elif value == 1:
                        color = (0, 255,0 )

                # Vul cel met kleur
                pygame.draw.rect(surface, color, rect)

                # Render de tekst
                if text:
                    self._draw_mixed_text(surface, text, rect)

        # Matrix border
        border_rect = pygame.Rect(grid_left, grid_top, grid_width, grid_height)
        pygame.draw.rect(surface, (0, 0, 0), border_rect, 1)

    def _draw_mixed_text(self, surface, text, rect):
        """Tekst centreren, k/t/l cursief, subscripts omzetten naar unicode"""
        subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        rendered_chars = []
        i = 0

        while i < len(text):
            ch = text[i]
            if ch == "_" and i + 1 < len(text) and text[i+1].isdigit():
                digits = ""
                j = i + 1
                while j < len(text) and text[j].isdigit():
                    digits += text[j]
                    j += 1
                render_ch = digits.translate(subscripts)
                font = self.font_regular
                i = j - 1
            else:
                render_ch = ch
                
                font = self.font_italic if ch in "abcdefghktl" else self.font_regular

            img = font.render(render_ch, True, (0, 0, 0))
            rendered_chars.append(img)
            i += 1

        total_width = sum(img.get_width() for img in rendered_chars)
        x = rect.centerx - total_width // 2
        y = rect.centery

        for img in rendered_chars:
            surface.blit(img, (x, y - img.get_height() // 2))
            x += img.get_width()
