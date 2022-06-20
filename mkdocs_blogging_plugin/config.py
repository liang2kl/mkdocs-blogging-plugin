class BloggingConfig:
    dirs: list
    size: int
    sort: dict
    paging: bool
    show_total: bool
    template: str
    theme: dict
    full_content: bool

    def __init__(self, config: dict):
        self.dirs = config.get("dirs", [])
        self.size = config.get("size", 10)
        self.sort = config.get("sort", {"from": "new", "by": "creation"})
        self.paging = config.get("paging", True)
        self.show_total = config.get("show_total", True)
        self.template = config.get("template")
        self.theme = config.get("theme")    
        self.full_content = config.get("full_content", False)