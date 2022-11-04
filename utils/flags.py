from typing import Optional, Type


class Flag:
    def __init__(self, value: int):
        self.value = value

    def __get__(self, obj: "GuildFlags", objtype: Optional[Type["GuildFlags"]] = None) -> bool:
        return self.value & obj.value == self.value

    def __set__(self, obj: "GuildFlags", value: bool) -> None:
        if value:
            obj.value |= self.value
        else:
            obj.value &= ~self.value


class GuildFlags:
    beta_info_commands_enabled = Flag(1 << 0)
    beta_new_wikilinks_enabled = Flag(1 << 1)

    def __init__(self, value: int = 0):
        self.value = value

    def __iter__(self):
        for name, value in vars(self.__class__).items():
            if not name.startswith("_"):
                yield name, getattr(self, name)