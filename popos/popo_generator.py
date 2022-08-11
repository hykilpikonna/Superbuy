#!/usr/bin/env python3
import json
from pathlib import Path
from sys import argv


NUM = 1


def transform_obj(obj: dict) -> str:
    global NUM

    output = {}

    for k, v in obj.items():
        if isinstance(v, dict):
            output[k] = transform_obj(v)

        elif isinstance(v, list):
            if len(v) == 0:
                output[k] = 'list'
            elif isinstance(v[0], dict):
                output[k] = f'list[{transform_obj(v[0])}]'
            else:
                output[k] = f'list[{type(v[0])}]'

        else:
            output[k] = type(v).__name__

    name = f'Type{NUM}'
    NUM += 1

    print(f'class {name}:' + ''.join(f'\n    {k}: {v}' for k, v in output.items()))
    print()

    return name


if __name__ == '__main__':
    file = Path(argv[1])

    obj = json.loads(file.read_text())
    transform_obj(obj)
