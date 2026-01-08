class DrawTextBuilder:
    def __init__(self):
        self.options = {}
        self._text = None

    def text(self, text: str):
        self._text = text
        return self
    
    def output(self, label: str):
        self._output_label = label
        return self

    def option(self, option_name: str, option_value: str):
        """General-purpose option"""
        self.options[option_name] = option_value
        return self

    def fontfile(self, path: str):
        return self.option("fontfile", path)

    def fontsize(self, size: int):
        return self.option("fontsize", str(size))

    def fontcolor(self, color: str):
        return self.option("fontcolor", color)

    def borderw(self, width: int):
        return self.option("borderw", str(width))

    def x(self, val):
        return self.option("x", str(val))

    def y(self, val):
        return self.option("y", str(val))

    def centered_x(self):
        return self.x("(w-text_w)/2")
    
    def centered_y(self):
        return self.y("(h-text_h)/2")
    
    def bottom_y(self, px: int):
        return self.y(f"h - text_h - {px}")
    
    def centered(self):
        """Same as calling centered_x and centered_y."""
        self.centered_x()
        self.centered_y()
        return self

    def enable(self, val: str):
        return self.option("enable", f"'{val}'")

    def build(self):
        if self._text is None:
            raise ValueError("DrawTextBuilder: text is required")
        options = ":".join(f"{k}={v}" for k, v in self.options.items())
        out = f"drawtext={options}:text='{self._text}'"
        return out
