import os
from pathlib import Path
import stat
import subprocess
from textual import log, on, events
from pathlib import Path
from pprint import pprint
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Label, Tree, Button, Input, SelectionList, Pretty, Footer, Header
from textual.screen import ModalScreen

#rom rich.pretty import Pretty
from typing import Union, TypedDict
from textual.containers import Vertical, Horizontal, Container, Grid
from textual.message import Message
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets.selection_list import Selection
from textual.events import Mount, Click

from art import *


#setup ascii art

art = text2art("CHMpy")
# art = "miaw"


class Data_format(TypedDict):
    type: str
    data: dict[str, list]
    sub: dict[str, "Data_format"]

Data_model = dict[str, Data_format]

class Message_tree_view(Message):
    # print("dapet pesang kagn")
    def __init__(self, path, max_branch, max_depth):
        super().__init__()
        self.path = path
        self.max_branch = max_branch
        self.max_depth = max_depth

class Chmod_converter(Static):
    """class to convert the list of permission like user [write,execute] into chmod format like 666"""
    def __init__(self, data):
        print("masuk def innit chmod converter")
        super().__init__()
        self.data = data
        self.chmod_val: int

    def converter(self, perm):
        """function to convert the permission into chmod format"""
        mapping = {"read": 4, "write":2, "execute":1}
        return sum(mapping[p] for p in perm if p in mapping )
    
    def apply_converter(self):
        print("on apply converter chmod converter")
        data = self.data["perm"]

        if data["owner"]:
            owner = data["owner"]
        else:
            owner = []

        if data["group"]:
            group = data["group"]
        else:
            group = []

        if data["others"]:
            other = data["others"]
        else:
            other = []

        owner_chmod = self.converter(owner)   
        group_chmod = self.converter(group)
        other_chmod = self.converter(other)
        filepath = Path(self.data["name"])

        self.chmod_val = int(f"{owner_chmod}{group_chmod}{other_chmod}", 8)
        os.chmod(filepath, self.chmod_val)
        print(f"Os chmod {self.chmod_val}")
    
    def on_mount(self):
        print("on mount chmod converter")
        self.apply_converter()



class Button_perm_list(ModalScreen):
    """The class of modalscreen to cahnge the permission of the file and the user/group we want to edit via overlay"""
    def __init__(self, role, perms):
        super().__init__()
        self.role = role
        self.perms = perms
        if "read" in self.perms:
            self.read = True
        else:
            self.read = False
        if "write" in self.perms:
            self.write = True
        else:
            self.write = False
        if "execute" in self.perms:
            self.execute = True
        else:
            self.execute = False
        
        print(f"this is the double modal: {self.role} {self.perms}")
        #this is the double modal: owner ['read', 'write']


    def compose(self):
            print(f"data of the selection list:{self.perms}")
            yield Vertical(
                Label(f"Edit permission for: {self.role} {self.perms}"),
                Pretty([self.perms], id="pretty"),

                SelectionList(
                    Selection(prompt="read", value="read", initial_state=self.read),
                    Selection(prompt="write", value="write", initial_state=self.write),
                    Selection(prompt="execute", value="execute", initial_state=self.execute)
                    # *[
                    #     Selection(prompt=perm, value=perm, initial_state=perm)
                    #     for perm in ["read", "write", "execute"]
                    #     if perm in self.perms
                    # ],
                ),
                Horizontal(
                    Button("Save", id="save_button", variant="success"),
                    Button("Cancel", id="cancel", variant="warning"),
                    id="container_butten_perm_list_button"
                ),
                id="selection"
            )

    def on_mount(self):
        
        self.query_one("#selection").border_title =f"Edit permision{self.role}"
        self.query_one("#pretty").border_title= "Perm list"
        
    #@on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_perm(self, event: SelectionList.SelectedChanged) -> None:
        self.query_one(Pretty).update(self.query_one(SelectionList).selected)
        self.perms = self.query_one(SelectionList).selected

    @on(Button.Pressed)
    def save(self, event: Button.Pressed):
        if event.button.id == "save_button":
            self.dismiss([self.perms, self.role])
        else:
            self.dismiss()

    async def on_click(self, event: Click):
        """function to close the overlay/modal screen when click outside"""
        close = self.query_one("#selection")
        if not close.region.contains(int(event.screen_x), int(event.screen_y)):
            self.dismiss([self.perms, self.role])
            event.stop()

class Tree_ModelScreen(ModalScreen):
    """Classes of modalscreen to show overlay of setting of the node of the tree user pressed"""
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.perm = data["perm"]
        print(f'slf data tree modal screen: {self.data}, {self.perm}')
        # {'name': 'mmain2.py', 'file_type': 'file', 'perm': {'owner': ['read', 'write'], 'group': ['read', 'write'], 'others': ['read', 'write']}},
        # {'owner': ['read', 'write'], 'group': ['read', 'write'], 'others': ['read', 'write']}

    def on_mount(self):
        # self.capture_mouse(True)
        None


    def compose(self):
        yield Vertical(
            Label(f"Tree Model : {self.data['name']}", id="title_modal1"),
            *[Button(f'{k}: {v}', id=k) for k, v in self.perm.items()],
            Button(f"save", id="save", variant="success"),
            Button(f"cancel", id="cancel", variant="warning"),
            id="tree_model"
        )
        #ini keknya error karena kan i itu dictionary tapi nanti ajalah
    
    def save_data(self, data):
        if not data:
            return
        print(f"data is saves{data}") #data is saves[['read', 'write', 'execute'], 'owner']
        role = data[1]
        print(self.data) #{'name': 'main4.py', 'file_type': 'file', 'perm': {'owner': ['read', 'write'], 'group': ['read', 'write'], 'others': ['read', 'write']}, 'owner': ['read', 'write','execute']}
        self.data["perm"][role] = data[0]
        print(self.data)

    @on(Button.Pressed)
    async def perm_button(self, event: Button.Pressed):
        role = event.button.id
        print("mausk kedengar button")
        print(role)
        print(role)
        if role == 'save' or role == 'cancel':
            print("masuk if pertama")
            # self.dismiss()
            if role == "cancel":
                print("pressed cancel button but cant dismmiss")
                self.dismiss()
            else:
                print("pressed save button")
                self.app.mount(Chmod_converter(self.data), after=self)
                self.dismiss() ######################################################################
        
        else:
            perms = self.perm.get(role)
            print(f'perms {perms}')
            if perms:
                # widget = self.Button_perm_list(perms)
                print('keknya bisa masuk perms sih')
                self.app.push_screen(Button_perm_list(role, perms), self.save_data)
                #self.app.push_screen(Tree_ModelScreen(data))
            print("kagak ada perms cuyy")


    async def on_click(self, event: Click):
        """function to close the overlay/modal screen when click outside"""
        close = self.query_one("#tree_model")
        if not close.region.contains(int(event.screen_x), int(event.screen_y)):
            self.dismiss(0)
            event.stop()

class Message_dir_data(Message): 
    # print("message dir daata get")
    def __init__(self, data):
        super().__init__()
        self.data = data

class Launch_app(Static):

    CSS = """
    Launch_app {
        height: auto;
        min-height: 15;
    }

    #lauch_app_container {
        align: center top;
    }

    #settings_row {
        height: auto;
        margin-top: 1;
        align: center top;
    }

    .settings_group {
        width: 1fr;
        margin-right: 1;
    }

    .settings_group:last-child {
        margin-right: 0;
    }

    .settings_label {
        text-style: bold;
        margin-bottom: 1;
    }

    #settings_row Input {
        width: 100%;
    }
    
    Input.-valid {
        border: tall $success 60%;
    }
    Input.-valid:focus {
        border: tall $success;
    }
    Input.-invalid {
        border: tall $error 60%;
    }
    Input.-invalid:focus {
        border: tall $error;
    }
    
    """
        
    def __init__(self):
        super().__init__()
        self.path: Path =  Path(".")
        self.data: Data_model = {}

    def on_mount(self):
        None

    def _validate_all_inputs(self) -> bool:
        """Validate all inputs and return True if all are valid"""
        all_valid = True
        
        # Validate directory input
        dir_input = self.query_one("#dir_input_user", Input)
        dir_validator = dir_input.validators[0]
        dir_result = dir_validator.validate(dir_input.value)
        self._update_input_validation(dir_input, dir_result)
        if not dir_result.is_valid:
            all_valid = False
            
        # Validate max branch input
        branch_input = self.query_one("#input_max_branch", Input)
        branch_validator = branch_input.validators[0]
        branch_result = branch_validator.validate(branch_input.value)
        self._update_input_validation(branch_input, branch_result)
        if not branch_result.is_valid:
            all_valid = False
            
        # Validate max depth input
        depth_input = self.query_one("#input_max_depth", Input)
        depth_validator = depth_input.validators[0]
        depth_result = depth_validator.validate(depth_input.value)
        self._update_input_validation(depth_input, depth_result)
        if not depth_result.is_valid:
            all_valid = False
            
        return all_valid

    def _update_input_validation(self, input_widget: Input, result: ValidationResult) -> None:
        """Update input styling based on validation result"""
        if not result.is_valid:
            input_widget.remove_class("-valid")    
            input_widget.add_class("-invalid")
            input_widget.border_subtitle = result.failure_descriptions[0] if result.failure_descriptions else "Invalid"
        else:
            input_widget.remove_class("-invalid") 
            input_widget.add_class("-valid")
            input_widget.border_subtitle = ""

    def _process_input(self, input_widget: Input) -> None:
        if not self._validate_all_inputs():
            return
        
        max_branch = self.query_one("#input_max_branch", Input).value
        max_depth = self.query_one("#input_max_depth", Input).value
        input_value = input_widget.value.strip()
        
            
        self.app.post_message(Message_tree_view(
            path=Path(input_value),
            max_branch=int(max_branch),
            max_depth=int(max_depth)
        ))

    @on(Input.Changed, "#dir_input_user, #input_max_branch, #input_max_depth")
    def on_input_changed(self, event: Input.Changed) -> None:
        """validate inpute as they change"""
        self._validate_all_inputs()

    @on(Input.Submitted, "#dir_input_user")
    def on_dir_submitted(self, event: Input.Submitted) -> None:
        self._process_input(event.input)

    @on(Button.Pressed, "#show_dir_button")
    def on_dir_pressed(self, event: Button.Pressed) -> None:
        input_widget = self.query_one("#dir_input_user", Input)
        self._process_input(input_widget)

    def set_data_dir(self, data):
        self.data = data

    def compose(self):
        with Vertical(id="lauch_app_container"):
            yield Label("Edit file permission", id="title_label")
            
            with Horizontal(id="container_main_lauch_app_button_input"):
                yield Button("Load", id="show_dir_button", variant="default")
                yield Input(
                    id="dir_input_user",
                    placeholder="Enter directory path...",
                    validators=[Validator_tree_view()],
                )
            
            with Horizontal(id="settings_row"):
                with Vertical(classes="settings_group"):
                    yield Label("Max items per dir:", classes="settings_label")
                    yield Input(
                        id="input_max_branch",
                        value="20",
                        type="integer",
                        validators=[Validator_max_branch()],
                        # validate_on=["changed", "blur"]
                    )
                with Vertical(classes="settings_group"):
                    yield Label("Max depth:", classes="settings_label")
                    yield Input(
                        id="input_max_depth",
                        value="3",
                        type="integer",
                        validators=[Validator_max_depth()],
                        # validate_on=["changed", "blur"]
                    )

class Show_dir(Static):
    # print("go show dir")
    def __init__(self, path: Path = None, max_depth: int = 3, max_branch: int = 20):
        super().__init__()
        self.data : Data_model = {}
        self.chmod_file: str
        self.perm_dict: dict = {}
        self.data_type: str
        self.max_depth = max_depth
        self.max_branch = max_branch

        # For main tree part
        mode = path.stat().st_mode
        permissions = stat.filemode(mode)
        perm_dict, file_type = self.get_permissions(permissions)
        root_perms = {role: perm_dict[role]["data"] for role in perm_dict}


        self.tree_perm: Tree = Tree(
            str(path), 
            data={
                "name": path,
                "file_type": file_type, ############################################################
                "perm": root_perms
            })
        self.path: Path = path or Path('.')
        self.tree_perm.root.expand()

    def show_tree(self, data_dict=None, parent_node=None):
        print("masuk show tree function")
        if data_dict is None:
            data_dict = self.data  
        if parent_node is None:
            # self.tree_perm.root.data = hehrehehrehr
            parent_node = self.tree_perm.root  
        
        print(f'data dict : {data_dict}')
        for key, value in data_dict.items():
            if value["type"] == "file":
                parent_node.add_leaf(
                    f'{key}', 
                    data={
                        "name": key,
                        "file_type": value["type"],
                        "perm": value["data"]
                    }
                )
            else:
                new_branch = parent_node.add(
                    f'{key}',
                    data={
                        "name": key,
                        "file_type": value["type"],
                        "perm": value["data"]
                    }
                    )
                if value.get("sub"):  
                    self.show_tree(value["sub"], new_branch)


    def get_permissions(self, chmod_str: str):
        """
        Function that return perm_dict and data_type of the fiven chmod_file like (drwxrwx).

        What it do is to translate those chmod format into human readeble list like this
        {
            "owner": {"chmod": "rwx", "data": ["read", "write", "execute"]},
            "group": {"chmod": "rwx", "data": ["read", "write", "execute"]},
            "others": {"chmod": "rwx", "data": ["read", "write", "execute"]},
        }
        """
        print("masuk get permissions")
        chmod = chmod_str
        data_type = chmod[0]
        if data_type == 'd':
            data_type = 'directory'
        elif data_type == '-':
            data_type = 'file'

        owner = chmod[1:4]
        group = chmod[4:7]
        others = chmod[7:10]

        perm_dict = {
            'owner': {
                'chmod':owner,
                'data': []
            },
            'group': {
                'chmod':group,
                'data': []
            }, 
            'others': {
                'chmod': others,
                'data': []
            }
        }


        for u in ['owner', 'group', 'others']:

            y = perm_dict[u]["chmod"]
            for i in range(len(y)):

                if y[i] == 'r':
                    perm_dict[u]["data"].append('read')
                elif y[i] == 'w':
                    perm_dict[u]["data"].append('write')
                elif y[i] == 'x':
                    perm_dict[u]["data"].append('execute') 

        self.perm_dict = perm_dict
        self.data_type = data_type
        print("woi ini")
        print(perm_dict, data_type)
        return perm_dict, data_type

    def version_2(self):
        """function to return the dicttionary of the dir tree of the given path"""
        print("masuk version 2")

        def tree(dir_get, parent_dict, current_depth=0, max_depth=self.max_depth, max_branch=self.max_branch):
            if current_depth > max_depth:
                return
            
            try:
                dir = Path(dir_get)
            except Exception as e:
                print(f"Error creating Path: {e}")
                return
                
            # Skip hidden directories except current directory ('.')
            if dir.name.startswith(".") and dir.name != "." or dir.name in {"__pycache__", ".venv", "venv", ".git"}:
                return
            
            counts = 0

            try:
                for subdir in dir.iterdir():
                    if counts >= max_branch:
                        break
                    if subdir.name.startswith("."):
                        continue
                    
                    try:
                        mode = subdir.stat().st_mode
                        permissions = stat.filemode(mode)
                        data_get, file_type = self.get_permissions(permissions)

                        # Create node data
                        node = {
                            "type": file_type,
                            "sub": {},
                            "data": {role: data_get[role]["data"] for role in data_get}
                        }

                        parent_dict[subdir.name] = node

                        if subdir.is_dir():
                            tree(subdir, node["sub"], current_depth + 1, max_depth, max_branch)
                        counts += 1
                    except Exception as e:
                        print(f"Skipping {subdir}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error traversing directory: {e}")

        tree(self.path, self.data)

    @on(Tree.NodeSelected)
    def on_node_selected(self, event: Tree.NodeSelected):
        """function to show popup/everlay when a node is clicked for setting and cahnging permission"""
        # if event.node.data["name"]

        data = event.node.data
        if data == None:
            print("no data at node somehow")
        print(f"data node {data}")
        path = data["name"]
        file_type = data["file_type"]
        self.log(f"You selected a {file_type} file at {path}")
        self.app.push_screen(Tree_ModelScreen(data)) ######################################################

    def on_mount(self):
        try:
            if hasattr(self, 'path') and self.path and self.path.exists():
                self.version_2()
                self.show_tree()
            else:
                print("Path not set or does not exist")
        except Exception as e:
            print(f"Error initializing Show_dir: {e}")

    def compose(self):
        with Container(id="treelist"):
            yield self.tree_perm

        

class Validator_tree_view(Validator):
    """class to validate the input sent before they gonna be processed to the next class"""
    # print("validator masuk")
    # def __init__(self, data):
    #     super().__init__()
    #     self.data = data
    #     self.dir_data = {}
    def validate(self, value: str) -> ValidationResult:
        if self.is_valid(value):
            return self.success()
        else:
            return self.failure("Invalid directory path")
        
    # def get_data_dir(self, input_data):
    #     self.data = input_data

    @staticmethod
    def is_valid(value: str) -> bool:  
        if not value or value.isspace():  
            return False
        
        try:
            path = Path(value).expanduser().resolve()
            return path.exists() and path.is_dir()
        except (OSError, ValueError):  # Handle path errors
            return False

    # def on_mount(self):
    #     self.show_

class Validator_max_branch(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            num_value = int(value)  
            if self.is_valid(num_value):
                return self.success()
            else:
                return self.failure("Value must be a positive integer")
        except ValueError:
            return self.failure("Must be a valid integer")
        

    @staticmethod
    def is_valid(value: int) -> bool:  
        if not value: 
            return False
        
        try:
            if value < 0 or value == 0:
                return False
            

            return True
        except TypeError: 
            return False

class Validator_max_depth(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            num_value = int(value)  
            if self.is_valid(num_value):
                return self.success()
            else:
                return self.failure("Value must be a positive integer")
        except ValueError:
            return self.failure("Must be a valid integer")
        

    @staticmethod
    def is_valid(value: int) -> bool:  
        if not value: 
            return False
        
        try:
            if value < 0 or value == 0:
                return False
            

            return True
        except TypeError: 
            return False

class Main_app(App):
    CSS_PATH = "main.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True, show=False),
        Binding("ctrl+x", "quit", "Quit", priority=True)
    ]

    def compose(self) -> ComposeResult:
        yield Label(art, id="ascii")
        with Container(id="main_body"):
            yield Launch_app()  
            yield Vertical(id="main_container")
        yield Label("made by SP", id="owner")
        yield Footer()
        yield Header()
        

    def on_mount(self):
        self.container = self.query_one("#main_container", Vertical)
        self.theme = "nord"

    @on(Message_tree_view)
    def show_dir_view(self, message: Message_tree_view) -> None:
        print("dapet pesan masuk main apps")
        print(message.path)
        print("done??")

        self.container.remove_children()

        show_dir_widget = Show_dir(
            path=message.path,
            max_depth=message.max_depth,
            max_branch=message.max_branch   
            )

        self.container.mount(show_dir_widget)

#function to start the App externaly:

def main():
    """function to start the app"""
    app = Main_app()
    app.run()


if __name__ == "__main__":
    app = Main_app()
    app.run()
