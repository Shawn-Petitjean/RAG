import argparse
from .ingest import get_files, files_dispatch



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        default="data/input_pub/function_calling_tests.json")
    parser.add_argument("--functions_definition",
                        default="data/input_pub/functions_definition.json")
    parser.add_argument("--output",
                        default="data/output/function_calling_results.json")
    args = parser.parse_args()
    # dir_path = "/home/shapetit/Documents/42/C_4/RAG/vllm-0.10.1"
    # f = get_files(dir_path)
    # data_m = files_dispatch(f)
    # print(len(f))
    # print(list(dir_path.d("*.d")))
    # for dir in dir_path.iterdir():
    #     if not dir.is_file():
    #         print(dir)
    #     if str(dir).endswith(".py") or str(dir).endswith(".md"):


if __name__ == "__main__":
    main()
