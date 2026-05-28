import argparse
<<<<<<< HEAD
from .ingest import get_files, files_dispatch
=======
from .ingest import get_files
>>>>>>> refs/remotes/origin/master


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--input",
    #                     default="data/input_pub/function_calling_tests.json")
    # parser.add_argument("--functions_definition",
    #                     default="data/input_pub/functions_definition.json")
    # parser.add_argument("--output",
    #                     default="data/output/function_calling_results.json")
    # args = parser.parse_args()
    dir_path = "/home/shapetit/Documents/42/C_4/RAG/vllm-0.10.1"
    f = get_files(dir_path)
<<<<<<< HEAD
    data_m = files_dispatch(f)
=======
    for file in f:
        print(file)
    print(len(f))
>>>>>>> refs/remotes/origin/master
    # print(list(dir_path.d("*.d")))
    # for dir in dir_path.iterdir():
    #     if not dir.is_file():
    #         print(dir)
    #     if str(dir).endswith(".py") or str(dir).endswith(".md"):


if __name__ == "__main__":
    main()
