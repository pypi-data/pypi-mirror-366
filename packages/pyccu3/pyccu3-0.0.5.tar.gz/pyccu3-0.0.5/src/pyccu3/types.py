from datetime import datetime


class PartyDate:
    def __init__(self, value):
        self.value: datetime = datetime.strptime(value, "%Y_%m_%d %H:%M")

    def __str__(self) -> str:
        return self.value.strftime("%Y_%m_%d %H:%M")
