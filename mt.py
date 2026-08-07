from sys import argv

type DeltaFunc = dict[tuple[str, str], tuple[str, str, str]]


class TuringMachine:
    tape: dict[int, str]

    def __init__(
        self,
        delta: DeltaFunc,
    ):
        self.delta = delta
        self.state = "0"
        self.tape = {}
        self.head = 0

    def __call__(self, w: str) -> None:
        w = w.replace(" ", "_")
        for i, c in enumerate(w):
            self.tape[i] = c

        while not self.state.startswith("halt"):
            # print(self)
            if self.head not in self.tape:
                self.tape[self.head] = "_"
            c = self.tape[self.head]
            if (self.state, c) not in self.delta:
                c = "*"
            if (self.state, c) not in self.delta:
                return
            new_symbol, new_move, new_state = self.delta[(self.state, c)]
            if new_state != "*":
                self.state = new_state
            if new_symbol != "*":
                self.tape[self.head] = new_symbol
            match new_move:
                case "r":
                    self.head += 1
                case "l":
                    self.head -= 1

    def __str__(self) -> str:
        ret = ""
        printed_state = False
        for k, v in sorted(self.tape.items()):
            if v == "_":
                continue
            if self.head == k:
                ret += f"<{self.state}>"
                printed_state = True
            ret += v
        if printed_state == False:
            if self.head < min(self.tape.keys()):
                ret = f"<{self.state}>" + ret
            else:
                ret += f"<{self.state}>"
        return ret


def main() -> None:
    assert len(argv) >= 2
    path = argv[1]
    w = ""
    try:
        w = argv[2]
    except:
        pass
    delta: DeltaFunc = {}

    with open(path) as f:
        source_code = f.read()
        lines = source_code.split("\n")
        lines = filter(lambda x: x != "" and not x.startswith(";"), lines)
        for line in lines:
            state, symbol, new_symbol, move, next_state, *_ = line.split(" ")
            assert len(symbol) == 1
            assert len(new_symbol) == 1
            assert move in {"r", "l", "*"}
            delta[(state, symbol)] = (new_symbol, move, next_state)

    M = TuringMachine(delta)
    M(w)
    print(M)


if __name__ == "__main__":
    main()
