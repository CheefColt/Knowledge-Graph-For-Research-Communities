class Hello:
    hp = 0
    def __init__(self, hp):
        self.hp = hp
        print(hp)
        print(self.hp)
        print(Hello.hp)

obj = Hello(10)
