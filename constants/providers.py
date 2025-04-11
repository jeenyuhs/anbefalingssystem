from enum import IntFlag

class Providers(IntFlag):
    NONE = 1 << 0

    DISNEYPLUS = 1 << 1
    PRIME = 1 << 2
    NETFLIX = 1 << 3
    PEACOCK = 1 << 4
    MAX = 1 << 5
    PLUTO = 1 << 6
    PLEX = 1 << 7
    SKYSHOWTIME = 1 << 8
    GOOGLEPLAY = 1 << 9
    APPLETV = 1 << 10
    VIAPLAY = 1 << 11

    @property
    def as_dict(self) -> dict["Providers", str]:
        return {
            self.DISNEYPLUS: "Disney+",
            self.PRIME: "Amazon Prime",
            self.NETFLIX: "Netflix",
            self.PEACOCK: "Peacock",
            self.MAX: "Max",
            self.PLUTO: "Pluto",
            self.PLEX: "Plex",
            self.SKYSHOWTIME: "SkyShowtime",
            self.GOOGLEPLAY: "Google Play Movies",
            self.APPLETV: "Apple TV+"
        }
    
    @classmethod
    def from_names(cls, names: list[str]) -> "Providers":
        providers = cls.NONE

        for provider, name in providers.as_dict.items():
            if name in names:
                providers |= provider

        return providers