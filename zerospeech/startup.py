from .cmd import (
    CommandTree, CLI, LIST_OF_COMMANDS
)
from .networkio import update_repo_index, check_update_repo_index
from .out import console
from .settings import get_settings

st = get_settings()


def init():
    """ Initialize environment for application """
    st.APP_DIR = st.APP_DIR.resolve()

    if not st.APP_DIR.is_dir():
        console.log(f"setting up application directory @ {st.APP_DIR}")
        st.APP_DIR.mkdir(exist_ok=True, parents=True)

    if not st.dataset_path.is_dir():
        st.dataset_path.mkdir(exist_ok=True, parents=True)

    if not st.checkpoint_path.is_dir():
        st.checkpoint_path.mkdir(exist_ok=True, parents=True)

    if not st.samples_path.is_dir():
        st.samples_path.mkdir(exist_ok=True, parents=True)

    if check_update_repo_index():
        update_repo_index()


def main():
    """ Main Function """
    cli = CLI(
        CommandTree("zrc"),
        description="A command line tool to help with the use of the Zerospeech Benchmarks.",
        usage=f"zrc <command> [<args>]"
    )
    cli.run()


if __name__ == '__main__':
    main()
