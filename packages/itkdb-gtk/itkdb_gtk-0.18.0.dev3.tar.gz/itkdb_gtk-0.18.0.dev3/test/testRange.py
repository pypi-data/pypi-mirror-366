#!/usr/bin/env python3
"""Tests the range parser."""
def range_to_list(V):
    """Convert a range to a list.

        ch1-ch2 or ch1:ch2 -> [ch1, ch1+1, ch1+2, ..., ch2] or
        ch1:step:ch2 -> [ch1, ch1+sep, ch1+2*step, ..., ch2]
    """
    nfound = 0
    for c in "-:,":
        if c in V:
            nfound += 1
            break

    if nfound == 0:
        return [V]

    out = []
    values = V.split(',')
    for V in values:
        if '-' in V:
            endpoints = list(map(int, V.split('-')))
            endpoints.sort()
            for i in range(endpoints[0], endpoints[1]+1):
                out.append(str(i))
        elif ':' in V:
            endpoints = list(map(int, V.split(':')))
            if len(endpoints) == 2:
                endpoints.sort()
                for i in range(endpoints[0], endpoints[1]+1):
                    out.append(str(i))

            elif len(endpoints) == 3:
                for i in range(endpoints[0], endpoints[2]+1, endpoints[1]):
                    out.append(str(i))

            else:
                print("Wring range specification. {}".format(V))
                continue

        else:
            out.append(V)

    return out

def main():
    r = "1-5"
    print(r, range_to_list(r))

    r = "1:5"
    print(r, range_to_list(r))

    r = "1:2:12"
    print(r, range_to_list(r))


if __name__ == "__main__":
    main()
