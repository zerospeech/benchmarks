import abc
import argparse
import sys
import uuid
from collections import namedtuple
from typing import Optional, Type

from treelib import Tree, Node

from ..out import console, void_console

NAMESPACE_SEP = ":"
LIST_OF_COMMANDS = []


class CMD(abc.ABC):
    COMMAND = "<cmd_name>"
    NAMESPACE = "<cmd-path>"
    quiet: bool = False

    def __init__(self, root):
        self._unique_id = f"{uuid.uuid4()}"
        self.__check_presets__()

        prog = f"{root} {self.NAMESPACE}{NAMESPACE_SEP}{self.COMMAND}"
        if self.NAMESPACE == '':
            prog = f"{root} {self.COMMAND}"

        self.parser = argparse.ArgumentParser(
            prog=prog,
            usage=f"{prog}[{NAMESPACE_SEP}subcommand] [<args>]",
            formatter_class=argparse.RawTextHelpFormatter
        )
        # load description
        if self.long_description:
            self.parser.description = self.long_description
        else:
            self.parser.description = self.short_description

    @classmethod
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        # append to global list for autodiscover
        LIST_OF_COMMANDS.append(cls)

    def __check_presets__(self):
        """ Verify that subclass sets default parameters """
        assert self.COMMAND != "<cmd_name>", "Command not set in class"
        assert self.NAMESPACE != "<cmd-path>", "Command path not set in class"

    @property
    def short_description(self):
        return self.__doc__

    @property
    def console(self):
        if self.quiet:
            return void_console
        return console

    @property
    def long_description(self):
        return self.run.__doc__

    @property
    def label(self):
        return f"{self.COMMAND}:\t{self.short_description}"

    def add_epilog(self, child_info):
        # todo check if this works
        self.parser.epilog = child_info

    @property
    def name(self) -> str:
        return self.COMMAND

    @property
    def id(self) -> str:
        return self._unique_id

    def run_cmd(self, argv=None):
        """ """
        self.init_parser(self.parser)
        # todo add argument completion
        # argcomplete.autocomplete(parser)
        argv = argv if argv is not None else sys.argv[1:]
        args = self.parser.parse_args(argv)
        # if quiet mode is set propagate it
        self.quiet = getattr(args, 'quiet', False)
        # run command
        self.run(args)

    @abc.abstractmethod
    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    @abc.abstractmethod
    def run(self, argv: argparse.Namespace):
        pass


class CommandTree:
    __RootNodeLabel = namedtuple('__RootNodeLabel', 'label')
    help_commands = ['help', 'list', 'commands', '--help', '-h']
    autocomplete = '__all_cmd__'
    autocomplete_fn = '__auto_fn__'
    path_separator = NAMESPACE_SEP

    def is_help_cmd(self, cmd):
        """ Check if command is in help list """
        return cmd in self.help_commands

    def is_auto_fn(self, cmd):
        """ Check if command is autocomplete_fn """
        return cmd == self.autocomplete_fn

    def is_autocomplete(self, cmd):
        """Check if command is autocomplete """
        return cmd == self.autocomplete

    def __init__(self, root_cmd: str, auto_discover: bool = True):
        self.root_cmd = root_cmd
        self.__cmd_tree = Tree()
        self.__cmd_tree.create_node('.', 0, data=self.__RootNodeLabel(label='.'))
        if auto_discover:
            self.add_cmds(*LIST_OF_COMMANDS)

    def find_cmd(self, path: str) -> Optional[Node]:
        """ Find a cmd in the tree """
        current_node = 0
        for tag in path.split(self.path_separator):
            if current_node is None:
                # todo allow empty nodes ?
                return None
            current_node = next((x.identifier for x in self.__cmd_tree.children(current_node) if x.tag == tag), None)
        return self.__cmd_tree.get_node(current_node)

    def add_cmd(self, cmd_class: Type[CMD]):
        """ Add a CMD to the current tree """
        cmd = cmd_class(self.root_cmd)
        father_node = self.find_cmd(cmd.NAMESPACE)
        if father_node is None:
            father_node = self.__cmd_tree.get_node(self.__cmd_tree.root)

        self.__cmd_tree.create_node(
            tag=f"{cmd.name}",
            identifier=cmd.id,
            data=cmd,
            parent=father_node.identifier
        )

    def add_cmds(self, *cmd_items):
        for cmd in cmd_items:
            self.add_cmd(cmd)

    def has_children(self, _id):
        return self.__cmd_tree.children(_id)

    def show(self, root=None) -> str:
        if root:
            return self.__cmd_tree.subtree(root).show(data_property="label", stdout=False)
        else:
            return self.__cmd_tree.show(data_property="label", stdout=False)

    def build_epilogs(self):
        """ Iterate over all nodes and append epilog to help message"""
        for node in self.__cmd_tree.all_nodes():
            if node.identifier == 0:
                continue
            if not self.has_children(node.identifier):
                continue

            epilog = "---\n" \
                     "list of available sub-commands : \n\n" \
                     f"{self.show(root=node.identifier)}"
            node.data.add_epilog(epilog)

    def get_all_paths(self):
        paths_as_list = []
        paths_as_str = []
        tree = self.__cmd_tree
        for leaf in tree.all_nodes():
            paths_as_list.append([tree.get_node(nid).tag for nid in tree.rsearch(leaf.identifier)][::-1])

        for item in paths_as_list:
            if '.' in item:
                item.remove('.')
            paths_as_str.append(f"{self.path_separator}".join(item))

        if '' in paths_as_str:
            paths_as_str.remove('')

        paths_as_str.extend(self.help_commands)
        paths_as_str.append(self.autocomplete)
        paths_as_str.append(self.autocomplete_fn)
        return paths_as_str


class CLI:
    """ The Command Line Interface Builder Class """
    path_separator = NAMESPACE_SEP

    def __init__(self, cmd_tree: CommandTree, *, description: str = "", usage: str = ""):
        """
        :param cmd_tree:
        :param description:
        :param usage:
        """
        self.cmd_tree = cmd_tree
        # Build the tree epilogs
        self.cmd_tree.build_epilogs()

        # Help epilog
        epilog = "---\n" \
                 "list of available commands : \n\n" \
                 f"{cmd_tree.show()}"

        self.parser = argparse.ArgumentParser(
            description=description,
            usage=usage,
            epilog=epilog,
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.parser.add_argument('command', help='Subcommand to run')

    def run(self):
        """ Run the Command Line Interface """
        args = self.parser.parse_args(sys.argv[1:2])

        # check if help is asked
        if self.cmd_tree.is_help_cmd(args.command):
            self.parser.print_help()
            sys.exit(0)

        # check if requesting cmd list for autocomplete
        if self.cmd_tree.is_autocomplete(args.command):
            print(" ".join(self.cmd_tree.get_all_paths()))
            sys.exit(0)

        # check if requesting auto complete bash function
        if self.cmd_tree.is_auto_fn(args.command):
            # print(BASH_AUTOCOMPLETE_FN)
            sys.exit(0)

        cmd_node = self.cmd_tree.find_cmd(args.command)
        if cmd_node is None or cmd_node.identifier == 0:
            print(f'Unrecognized command {args.command}\n', file=sys.stderr)
            self.parser.print_help()
            sys.exit(1)

        cmd = cmd_node.data
        if not isinstance(cmd, CMD):
            print(f'Unrecognized command {args.command}\n', file=sys.stderr)
            self.parser.print_help()
            sys.exit(2)

        # call sub-command
        cmd.run_cmd(argv=sys.argv[2:])
