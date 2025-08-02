import json
from github import Github
from github.GithubException import GithubException, UnknownObjectException, BadCredentialsException
from datetime import datetime
from ast import literal_eval
import pandas as pd


class GitSys():
    def __init__(self, token:str, full_repo_name:str):
        '''
        ### GitSys (toke : str, full_repo_name : str) -> None
        
        This function allows you to access your server on GitHub. To do so, you need to provide your token and repository.
        '''
        self.CONTENT = []
        self.token = token
        self.FullRepoName = full_repo_name
        self.error = False
        agora = datetime.now()
        formatado = agora.strftime("%d/%m/%Y %H:%M:%S")
        try:
            self.GH = Github(login_or_token=token)
            self.repo = self.GH.get_repo(full_repo_name)
            print(f'[{formatado}] Successfully connected to GitHub!')
            self.CONTENT.append(f'[{formatado}] Successfully connected to GitHub!')
            self.error = True
        except BadCredentialsException:
            print(f"[{formatado}] Invalid GitHub token.")
            self.CONTENT.append("[{formatado}] Invalid GitHub token.")
        except UnknownObjectException:
            print(f"[{formatado}] Repository '{full_repo_name}' not found (404).")
            self.CONTENT.append(f"[{formatado}] Repository '{full_repo_name}' not found (404).")
            self.error = True
        except GithubException as e:
            print(f"[{formatado}] GitHub Error ({e.status}): {e.data.get('message', str(e))}")
            self.CONTENT.append(f"[{formatado}] GitHub Error ({e.status}): {e.data.get('message', str(e))}")
        except Exception as e:
            print(f"[{formatado}] Unexpected error: {str(e)}")
            self.CONTENT.append(f"[{formatado}] Unexpected error: {str(e)}")
        
        
    def get(self):
        '''
        ### GitSys.get ( NaN ) -> Repo
        
        This function already returns the repository in the correct format, in case you don't want to write it all over again.'''
        return self.GH.get_repo(str(self.FullRepoName))
    
    def get_error(self):
        '''
        error (404) -> True
        conect -> True
        error (all) not (404) -> False
        '''
        return self.error
    
    def nota(self, save=True, _print=False):
        '''
        ### GitSys.nota (save : bool = True, _print
        ###  : bool = False) -> str : Nota
        
        Inside your server, there will be a file called NOTA.json. It logs all the changes made by the server, which can be useful for checking what is happening with the server.'''
        self.repo = self.GH.get_repo(self.FullRepoName)
        path = 'NOTA.json'
        message = 'Update NOTA.json'
        try:
                file = self.repo.get_contents(path)

                existing_content = file.decoded_content.decode('utf-8')
                try:
                    existing_list = json.loads(existing_content)
                    if not isinstance(existing_list, list):
                        existing_list = []
                except json.JSONDecodeError:
                    existing_list = []
                

                combined_list = existing_list + self.CONTENT


                formatted_content = json.dumps(combined_list, indent=4, ensure_ascii=False)
                if save == True:
                    self.repo.update_file(
                        path=path,
                        message=message,
                        content=formatted_content,
                        sha=file.sha
                    )
        except GithubException as e:
                if e.status == 404:
                    formatted_content = json.dumps(self.CONTENT, indent=4, ensure_ascii=False)
                    self.repo.create_file(path, message, formatted_content)
                else:
                    now = datetime.now()
                    formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                    print(f"[{formatted}] [ERR0r] Error Nota: {e}")
                    return []
                
        if _print == True:
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"\n[{formatted}] Final content of '{path}':")
            for item in combined_list:
                print(f"- {item}")
                
        return tuple([combined_list],)
    
    class REPO:
        def __init__(self, master:str, repo_name:str):
            '''
            ### GitSys.REPO (master : gitsys = GitSys, repo_name : str) -> None
            
            Connects to a repository other than the one in use, allowing you to delete, edit, and perform other actions.
            '''
            self.master = master
            self.GH = master.GH
            self.repo_name = repo_name

        def create_repo(self, description: str = 'Create Repo (PYTHON)', private: bool = True):
            '''
            ### GitSys.REPO.create_repo (description : str, private : bool) -> str : repo_name
            
            Allows you to create a repository with the name you specified in REPO
            '''
            user = self.GH.get_user()
            repo = user.create_repo(self.repo_name, description=description, private=private)
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Repository '{self.repo_name}' created: {repo.html_url}")
            self.master.CONTENT.append(f"[{formatted}] Repository '{self.repo_name}' created: {repo.html_url}")
            self.master.nota()
            return repo

        def delete_repo(self):
            '''
            GitSys.REPO.delete_repo ( NaN ) -> None
            
            We can also delete a repository.'''
            try:
                user = self.GH.get_user()
                full_name = f"{user.login}/{self.repo_name}"
                repo = self.GH.get_repo(full_name)
                repo.delete()
                now = datetime.now()
                formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                print(f"[{formatted}] Repository '{full_name}' deleted successfully.")
                self.master.CONTENT.append(f"[{formatted}] Repository '{full_name}' deleted successfully.")
                self.master.nota()
            except Exception as e:
                now = datetime.now()
                formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                print(f"[{formatted}] Error deleting repository: {e}")
                self.master.CONTENT.append(f"[{formatted}] Error deleting repository: {e}")
                self.master.nota()
            
        def edit_repo(self, new_name=None, new_description=None, private=None):
            '''
            GitSys.REPO.edit_repo (new_name : str, new_descriptin : str, private : bool) -> str : new_name
            
            We can also edit a repository, if it already exists.'''
            try:
                user = self.GH.get_user()
                full_name = f"{user.login}/{self.repo_name}"
                repo = self.GH.get_repo(full_name)
                repo.edit(
                    name=new_name or repo.name,
                    description=new_description if new_description is not None else repo.description,
                    private=private if private is not None else repo.private
                )
                now = datetime.now()
                formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                print(f"[{formatted}] Repository '{full_name}' edit successfully.")
                self.master.CONTENT.append(f"[{formatted}] Repository '{full_name}' edit successfully.")
                self.master.nota()
                return new_name
            except Exception as e:
                now = datetime.now()
                formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                print(f"[{formatted}] Error edit repository: {e}")
                self.master.CONTENT.append(f"[{formatted}] Error edit repository: {e}")
                self.master.nota()
                
    class GitFiles:
        def __init__(self, master, repo):
            '''
            GitSys.GitFiles (master : gitsys = GitSys, repo : str) -> None
            
            We can edit files, create, delete, download, and more — an easy way to manage your files in the repository.
            '''
            self.repo = repo
            self.master = master

        def create_file(self, path: str, content: str, message: str = "Creating file"):
            '''
             GitSys.GitFiles.create_file( path : str, content : str, menssage : str ) -> None
            
            With this function, you can create a file in the repository and upload any file type supported by GitHub.'''
            self.repo.create_file(path, message, content)
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] File '{path}' created successfully.")
            self.master.CONTENT.append(f"[{formatted}] File '{path}' created successfully.")

            
        def create_folder(self, path: str, message: str = "Creating folder"):
            '''
            GitSys.GitFiles.create_folder( path : str, menssage : str ) -> None
            
            With this function, you can create a folder in the repository and include any content supported by GitHub.'''
            self.repo.create_file(f'{path}/gitkeep', message, '')
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Folder '{path}' created successfully.")
            self.master.CONTENT.append(f"[{formatted}] Folder '{path}' created successfully.")

            
        def upload_file(self, local_path: str, repo_path: str, message: str = "File upload"):
            '''
            GitSys.GitFiles.upload_file ( local_path : str, repo_path : str, menssagae : str ) -> None
            
            We can upload a file from our computer to GitHub.'''
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.repo.create_file(repo_path, message, content)
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] File '{local_path}' uploaded as '{repo_path}'.")
            self.master.CONTENT.append(f"[{formatted}] File '{local_path}' uploaded as '{repo_path}'.")

            
        def download_file(self, repo_path: str, local_path: str):
            '''
            GitSys.GitFiles.download_file ( local_path : str, repo_path : str ) -> None
            
            We can download a file from our GitHub to the computer.'''
            content = self.repo.get_contents(repo_path)
            with open(local_path, "wb") as f:
                f.write(content.decoded_content)
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] File '{repo_path}' saved to '{local_path}'.")
            self.master.CONTENT.append(f"[{formatted}] File '{repo_path}' saved to '{local_path}'.")


        def read_file(self, repo_path: str) -> str:
            '''
            GitSys.GitFiles.read_file(repo_path: str) -> str
            
            Reads and returns the content of a file from the GitHub repository.
            '''
            content = self.repo.get_contents(repo_path)
            text = content.decoded_content.decode("utf-8")
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Content of '{repo_path}'.")
            self.master.CONTENT.append(f"[{formatted}] Content of '{repo_path}'.")
            return text


        def delete_file(self, repo_path: str, message: str = "Deleting path"):
            '''
            GitSys.GitFiles.delete_file ( repo_path: str, message: str ) -> None
            
            Deletes a file or directory (recursively) from the GitHub repository.
            '''
            contents = self.repo.get_contents(repo_path)
            if not isinstance(contents, list):
                contents = [contents]

            for item in contents:
                if item.type == "dir":
                    self.delete_path(item.path, message)
                else:
                    self.repo.delete_file(item.path, message, item.sha)
                    now = datetime.now()
                    formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                    print(f"[{formatted}] File '{item.path}' deleted.")
                    self.master.CONTENT.append(f"[{formatted}] File '{item.path}' deleted.")


        def update_file(self, repo_path: str, new_content: str, message: str = "Updating file"):
            '''
            GitSys.GitFiles.update_file(repo_path: str, new_content: str, message: str) -> None
            
            Updates the content of an existing file in the GitHub repository.
            '''
            content = self.repo.get_contents(repo_path)
            self.repo.update_file(repo_path, message, new_content, content.sha)
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] File '{repo_path}' updated successfully.")
            self.master.CONTENT.append(f"[{formatted}] File '{repo_path}' updated successfully.")


        def list_files(self):
            '''
            GitSys.GitFiles.list_files ( NaN ) -> tuple
            
            Recursively lists all files in the GitHub repository and returns them as a tuple.
            '''
            def recursive_list(path=""):
                files = []
                items = self.repo.get_contents(path)
                for item in items:
                    if item.type == "dir":
                        files += recursive_list(item.path)
                    else:
                        files.append(item.path)
                return files

            all_files = recursive_list()
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Files found in repository:")
            self.master.CONTENT.append(f"[{formatted}] Files found in repository:")

            for f in all_files:
                print(f"- {f}")

            return tuple(all_files)



    class server:
        def __init__(self, master, repo):
            self.master = master
            self.repo = repo

        def create_class(self, name):
            '''
            Creates a folder named `name` in the repository.

            Args:
                name (str): The name of the class/folder to create.

            Returns:
                str: The name of the created class.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            file.create_folder(path=f'{name}', message=f'Create class {name}.')

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Class '{name}' created successfully.")
            self.master.CONTENT.append(f"[{formatted}] Class '{name}' created successfully.")

            return name

        def create_table(self, _class, name):
            '''
            Creates a JSON file named `{name}.json` inside the folder `_class`.

            Args:
                _class (str): The folder/class where the table will be created.
                name (str): The name of the table (JSON file) to create.

            Returns:
                str: The path of the created JSON file.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            file.create_file(path=f'{_class}/{name}.json', content='', message=f'Create table {name}.')

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Table '{name}' created successfully.")
            self.master.CONTENT.append(f"[{formatted}] Table '{name}' created successfully.")

            return f'{_class}/{name}.json'

        def create_dict(self, table, name):
            '''
            Adds a new dictionary entry with `__name__` equal to `name` inside the JSON table.

            Args:
                table (str): The path to the JSON table file.
                name (str): The name of the dictionary to create.

            Returns:
                str: The name of the created dictionary.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)

            if txt_ant == '' or txt_ant is None:
                txt_ant = [
                    {
                        '__name__': str(name)
                    }
                ]
                txt_ant = json.dumps(txt_ant, indent=4, ensure_ascii=False)
                file.update_file(table, txt_ant)

                now = datetime.now()
                formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                print(f"[{formatted}] Dict '{name}' created successfully.")
                self.master.CONTENT.append(f"[{formatted}] Dict '{name}' created successfully.")
                return name

            ast: list = literal_eval(txt_ant)
            ast.append({'__name__': str(name)})
            ast = json.dumps(ast, indent=4, ensure_ascii=False)
            file.update_file(table, ast)

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Dict '{name}' created successfully.")
            self.master.CONTENT.append(f"[{formatted}] Dict '{name}' created successfully.")
            return name

        def delete_dict(self, table, name):
            '''
            Deletes the dictionary with `__name__` equal to `name` from the JSON table.

            Args:
                table (str): The path to the JSON table file.
                name (str): The name of the dictionary to delete.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)

            if not txt_ant:
                return

            ast = literal_eval(txt_ant)
            ast = [e for e in ast if e.get('__name__') != name]

            ast = json.dumps(ast, indent=4, ensure_ascii=False)
            file.update_file(table, ast)

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            log = f"[{formatted}] Dict '{name}' deleted."
            print(log)
            self.master.CONTENT.append(log)

        def delete(self, name, type):
            '''
            Deletes a class folder or table JSON file from the repository.

            Args:
                name (str): The name of the class or table.
                type (str): Either '_class' to delete a folder or '_table' to delete a JSON file.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")

            if type == '_class':
                file.delete_file(repo_path=name, message=f"Deleting {name}")
                log = f"[{formatted}] Class '{name}' deleted."
            elif type == '_table':
                file.delete_file(repo_path=f"{name}.json", message=f"Deleting {name}")
                log = f"[{formatted}] Table '{name}' deleted."
            else:
                print('[ERROR] type must be "_class" or "_table"')
                return

            print(log)
            self.master.CONTENT.append(log)

        def insert_value(self, table, dictionary, value=['key', 'value']):
            '''
            Inserts a key-value pair into the specified dictionary inside the JSON table.

            Args:
                table (str): The path to the JSON table file.
                dictionary (str): The dictionary `__name__` to insert the value into.
                value (list): A list with [key, value] to insert.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)

            if txt_ant == '' or txt_ant is None:
                return

            ast = literal_eval(txt_ant)
            for e in ast:
                if e['__name__'] == dictionary:
                    e[str(value[0])] = value[1]
            ast = json.dumps(ast, indent=4, ensure_ascii=False)
            file.update_file(table, ast)

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Key '{value}' inserted successfully.")
            self.master.CONTENT.append(f"[{formatted}] Key '{value}' inserted successfully.")

        def delete_value(self, table, dictionary, key_to_remove):
            '''
            Deletes a key from the specified dictionary inside the JSON table.

            Args:
                table (str): The path to the JSON table file.
                dictionary (str): The dictionary `__name__` to delete the key from.
                key_to_remove (str): The key to remove.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)

            if not txt_ant:
                return

            ast = literal_eval(txt_ant)

            for item in ast:
                if item['__name__'] == dictionary:
                    if str(key_to_remove) in item:
                        del item[str(key_to_remove)]

            ast = json.dumps(ast, indent=4, ensure_ascii=False)
            file.update_file(table, ast)

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Value '{key_to_remove}' deleted successfully.")
            self.master.CONTENT.append(f"[{formatted}] Value '{key_to_remove}' deleted successfully.")

        def update_value(self, table, dictionary, value=['key', 'value']):
            '''
            Updates a key's value in the specified dictionary inside the JSON table.

            Args:
                table (str): The path to the JSON table file.
                dictionary (str): The dictionary `__name__` to update.
                value (list): A list with [key, new_value].
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)

            if value[0] == '__name__':
                now = datetime.now()
                formatted = now.strftime("%Y/%m/%d %H:%M:%S")
                print(f"[{formatted}] [ERROR] Key '__name__' cannot be updated.")
                self.master.CONTENT.append(f"[{formatted}] [ERROR] Key '__name__' cannot be updated.")
                return

            ast = literal_eval(txt_ant)
            for e in ast:
                if e['__name__'] == dictionary:
                    value_ant = e.get(str(value[0]), None)
                    if value_ant is not None:
                        self.delete_value(table, dictionary, value[0])
                    self.insert_value(table, dictionary, value=[str(value[0]), str(value[1])])

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Value '{value_ant}' updated successfully to '{value[1]}'.")
            self.master.CONTENT.append(f"[{formatted}] Value '{value_ant}' updated successfully to '{value[1]}'.")

        def get_value(self, table, dictionary):
            '''
            Retrieves the dictionary with the specified `__name__` from the JSON table.

            Args:
                table (str): The path to the JSON table file.
                dictionary (str): The dictionary `__name__` to retrieve.

            Returns:
                dict: The dictionary content, or None if not found.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)
            _get = None

            if not txt_ant:
                return None

            ast = literal_eval(txt_ant)

            for item in ast:
                if item['__name__'] == dictionary:
                    _get = item
                    break

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Content of '{dictionary}'.")
            self.master.CONTENT.append(f"[{formatted}] Content of '{dictionary}'.")

            return _get

        def data_frame_value(self, table, values=['key']):
            '''
            Creates a pandas DataFrame from the specified keys in the JSON table.

            Args:
                table (str): The path to the JSON table file.
                values (list): List of keys to include in the DataFrame.

            Returns:
                pandas.DataFrame: DataFrame containing the specified keys.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)

            if not txt_ant:
                return None

            ast = literal_eval(txt_ant)

            result = {key: [] for key in values}

            for item in ast:
                for key in values:
                    result[key].append(item.get(key, 'NaN'))

            df = pd.DataFrame(result)

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] DataFrame created from table '{table}'.")
            self.master.CONTENT.append(f"[{formatted}] DataFrame created from table '{table}'.")

            return df

        def rename_dict(self, table, dictionary, new_name):
            '''
            Renames a dictionary `__name__` in the JSON table.

            Args:
                table (str): The path to the JSON table file.
                dictionary (str): The current name of the dictionary.
                new_name (str): The new name for the dictionary.

            Returns:
                str: The new name.
            '''
            file = self.master.GitFiles(repo=self.master.get(), master=self.master)
            txt_ant = file.read_file(table)

            if not txt_ant:
                return None

            ast = literal_eval(txt_ant)

            for item in ast:
                if item['__name__'] == dictionary:
                    item['__name__'] = new_name

            ast = json.dumps(ast, indent=4, ensure_ascii=False)
            file.update_file(table, ast)

            now = datetime.now()
            formatted = now.strftime("%Y/%m/%d %H:%M:%S")
            print(f"[{formatted}] Renamed '{dictionary}' to '{new_name}'.")
            self.master.CONTENT.append(f"[{formatted}] Renamed '{dictionary}' to '{new_name}'.")

            return new_name