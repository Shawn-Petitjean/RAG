from .model_init import init_question
import fire
from .interface import Cli


def main():
    fire.Fire(Cli)
    # init_question()
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
