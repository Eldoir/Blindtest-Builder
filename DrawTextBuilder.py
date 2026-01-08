class DrawTextBuilder:
    def __init__(self):
        self.options = {}
        self._text = None
        self._output_label = None

    def fontfile(self, path: str):
        self.options["fontfile"] = path
        return self

    def text(self, text: str):
        self._text = text
        return self

    def fontsize(self, size: int):
        self.options["fontsize"] = str(size)
        return self

    def fontcolor(self, color: str):
        self.options["fontcolor"] = color
        return self

    def borderw(self, width: int):
        self.options["borderw"] = str(width)
        return self

    def x(self, val):
        self.options["x"] = str(val)
        return self

    def y(self, val):
        self.options["y"] = str(val)
        return self

    def centered(self):
        self.x("(w-text_w)/2")
        self.y("(h-text_h)/2")
        return self

    def output(self, label: str):
        self._output_label = label
        return self

    def build(self):
        if self._text is None:
            raise ValueError("DrawTextBuilder: text is required")
        options = ":".join(f"{k}={v}" for k, v in self.options.items())
        out = f"drawtext={options}:text='{self._text}'"
        if self._output_label:
            out += f"[{self._output_label}]"
        return out
