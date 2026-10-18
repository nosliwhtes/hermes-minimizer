class PlainRenderer:
    def render(self, name: str) -> str:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        name = name.strip()
        if not name:
            raise ValueError("name must not be blank")
        return f"Hello, {name}!"


class RendererFactory:
    @staticmethod
    def create(style: str) -> PlainRenderer:
        if style != "plain":
            raise ValueError("unsupported style")
        return PlainRenderer()


def render_message(name: str, *, style: str = "plain") -> str:
    renderer = RendererFactory.create(style)
    return renderer.render(name)
