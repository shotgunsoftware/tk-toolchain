import subprocess


def main():
    subprocess.check_call(["pytest", "--cov"])
    subprocess.check_call(["tk-docs"])

if __name__ == "__main__":
    main()
