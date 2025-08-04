def parse_requirements(path="requirements.txt") -> list:
    with open(path) as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]
