from zerospeech.datasets import DatasetsDir
from .settings import get_settings
from .out import console
from .networkio import update_repo_index


st = get_settings()


def init():
    """ Initialize environment for application """
    st.APP_DIR = st.APP_DIR.resolve()

    if not st.APP_DIR.is_dir():
        console.log(f"setting up application directory @ {st.APP_DIR}")
        st.APP_DIR.mkdir(exist_ok=True, parents=True)

    if not st.dataset_path.is_dir():
        st.dataset_path.mkdir(exist_ok=True, parents=True)

    if not st.repository_index.is_file():
        update_repo_index()


def _main():
    """ Main Function """
    # Initialize environment
    init()
    cli = ...
    cli()


def main():
    """ Main function for testing """
    datasets = DatasetsDir.load()
    zr2021 = datasets.get("zerospeech2021_benchmark")
    zr2021.pull(show_progress=True)


if __name__ == '__main__':
    main()
