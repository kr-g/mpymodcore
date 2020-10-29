from modext.fiber_stream import FiberChannel, fc_readline


INPUT_FILE = "../boot.py"


def sample():
    """
    read a file and print it
    """

    fc = FiberChannel()

    chk_size = 64
    with open(INPUT_FILE, "rb") as f:
        while True:
            rc = f.read(chk_size)
            if len(rc) == 0:
                break
            fc.put(rc)

    print(len(fc))

    # fake end of transmisson
    fc.hangup()

    if False:
        while fc.more():
            chunk = fc.pop()
            print(chunk)

    if True:
        while fc.more():
            l = fc_readline(fc)
            if l != None:
                print(l)
            else:
                print(">dense")


def sample_stream_proc():
    """
    read a file, start processing data, while continue adding more data.
    """

    fc = FiberChannel()

    cnt = 0
    chk_size = 64
    with open(INPUT_FILE, "rb") as f:
        while True:
            rc = f.read(chk_size)
            if len(rc) == 0:
                break

            # add with line numbers
            fc.put((str(cnt) + ":").encode() + rc)

            cnt += 1
            # steal alreay some data...
            if cnt % 3 == 0:
                chunk = fc.pop()
                print("pop at cnt=", cnt, "->", chunk)

    print(len(fc))

    # fake end of transmisson
    # fc.hangup()
    print("-" * 37)

    while fc.more():
        chunk = fc.pop()
        print(chunk)
