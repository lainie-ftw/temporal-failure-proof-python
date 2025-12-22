import time

def print_number(n):
    print(str(n))


def main():
    for counter in range(1, 11):
        print_number(counter)
        if counter < 10:
            time.sleep(3)


if __name__ == "__main__":
    main()
