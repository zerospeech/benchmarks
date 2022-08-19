from .cmd import (
    CommandTree, CLI, LIST_OF_COMMANDS
)
from .networkio import update_repo_index
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

    if not st.repository_index.is_file():
        update_repo_index()


def build_cli(cmd_name):
    """ Builds the CLI object to parse command line arguments """
    tree = CommandTree(cmd_name)
    tree.add_cmds(*LIST_OF_COMMANDS)

    return CLI(
        tree,
        description="A command line tool to help with the use of the Zerospeech Benchmarks.",
        usage=f"{cmd_name} <command> [<args>]"
    )


def main():
    """ Main Function """
    cli = build_cli("zr")
    cli.run()


if __name__ == '__main__':
    main()
