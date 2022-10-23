class Flag:
    def __init__(self, value: int):
        self.value = value

    def __get__(self, obj, objtype=None):
        return self.value & obj.value == self.value

    def __set__(self, obj, value):
        obj.value |= self.value

class GuildFlags:
    beta_info_commands_enabled = Flag(1 << 0)

    def __init__(self, value=0):
        self.value = value