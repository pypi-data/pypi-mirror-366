import json
from pathlib import Path
from tqdm import tqdm
from contextlib import contextmanager
import threading
import concurrent.futures


def jsonl_reader(path: Path):
    with path.open(encoding="utf-8") as fi:
        for line in tqdm(fi):
            yield json.loads(line)


def dump_line(data):
    return json.dumps(data, ensure_ascii=False)


@contextmanager
def jsonl_writer(path: Path):
    write_lock = threading.Lock()
    with path.open("a", encoding="utf-8") as fo:

        def _writer(data):
            with write_lock:
                fo.write(dump_line(data) + "\n")

        yield _writer


def jsonl_write_list(path: Path, lst):
    with path.open("a", encoding="utf-8") as fo:
        for obj in lst:
            fo.write(dump_line(obj) + "\n")


def jsonl_map(input_path: Path, output_path: Path, func, num_threads=32):
    futures = []

    # read through output first to find missing jobs
    if not output_path.is_file():
        output_path.touch()

    completed_obj_ids = set()
    for data in jsonl_reader(output_path):
        if "id" in data and "output" in data and data["output"]:
            completed_obj_ids |= {data["id"]}

    def process_obj(obj):
        obj["output"] = func(obj)
        return obj

    with jsonl_writer(output_path) as write:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            for obj in jsonl_reader(input_path):
                if "id" not in obj or obj["id"] not in completed_obj_ids:
                    futures.append(executor.submit(process_obj, obj))
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Mapping over jsonl"):
                result = future.result()
                if result is not None and not isinstance(result, Exception):
                    write(result)
