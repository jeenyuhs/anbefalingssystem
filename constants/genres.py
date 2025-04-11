from enum import IntFlag

class Genres(IntFlag):
    NONE = 0
    ACTION = 1 << 0  # 1
    ADVENTURE = 1 << 1  # 2
    ANIMATION = 1 << 2  # 4
    COMEDY = 1 << 3  # 8
    CRIME = 1 << 4  # 16
    DOCUMENTARY = 1 << 5  # 32
    DRAMA = 1 << 6  # 64
    FANTASY = 1 << 7  # 128
    HORROR = 1 << 8  # 256
    MYSTERY = 1 << 9  # 512
    ROMANCE = 1 << 10  # 1024
    SCI_FI = 1 << 11  # 2048
    THRILLER = 1 << 12  # 4096
    WESTERN = 1 << 13  # 8192
    MUSICAL = 1 << 14  # 16384
    BIOGRAPHY = 1 << 15  # 32768
    HISTORY = 1 << 16  # 65536
    WAR = 1 << 17  # 131072
    FAMILY = 1 << 18  # 262144
    SPORT = 1 << 19  # 524288
    SUPERHERO = 1 << 20

    def as_dict(self) -> dict["Genres", str]:
        return {
            self.NONE: "None",
            self.ACTION: "Action",
            self.ADVENTURE: "Adventure",
            self.ANIMATION: "Animation",
            self.COMEDY: "Comedy",
            self.CRIME: "Crime",
            self.DOCUMENTARY: "Documentary",
            self.DRAMA: "Drama",
            self.FANTASY: "Fantasy",
            self.HORROR: "Horror",
            self.MYSTERY: "Mystery",
            self.ROMANCE: "Romance",
            self.SCI_FI: "Sci-Fi",
            self.THRILLER: "Thriller",
            self.WESTERN: "Western",
            self.MUSICAL: "Musical",
            self.BIOGRAPHY: "Biography",
            self.HISTORY: "History",
            self.WAR: "War",
            self.FAMILY: "Family",
            self.SPORT: "Sport",
            self.SUPERHERO: "Superhero"
        }

    @classmethod
    def from_names(cls, names: list[str]) -> "Genres":
        genres = cls.NONE

        for genre, str_value in genres.as_dict().items():
            if str_value in names:
                genres |= genre 

        return genres
