from loguru import logger
import os
import sys
from typing import Callable, Any

from dbpoint.hub import Hub
from dbpoint.datacapsule import DataCapsule

from dapu.context import DapuContext
from .perks import halt, real_path_from_list, replace_dict, is_interactive, prepare_schema_name, version_string_from_timeint
from .fileops import read_content_of_file, read_content_of_package_file
from .textops import yaml_string_to_dict, yaml_string_to_list

class DapuProcess:
    """
    All Dapu processes behave somehow similar way 
    """
    
    context: DapuContext # class variable, mostly for our wise decorator 

    def __init__(self, args: list | DapuContext | None):
        """
        Two correct way to initialize: using list of arguments to create Context, and using existing Context to keep it.
        list of arguments:
        1) work_dir ()
        """

        if args is None: # no args, lets try static (cls) context and fail if none 
            if DapuProcess.context is None:
                halt(3, "Wrong initialization") # wasn't given and we don't have it here neither
                return  # only for pylance
            self.context = DapuProcess.context
            return
        
        if isinstance(args, DapuContext): # reusing context (worker -> job -> manager chain)
            self.context = args
            logger.debug(f"from existing context, work_dir is {self.context.work_dir}")
        elif isinstance(args, list):
            # argument is not DapuContext, so context must be generated, assumably for very first process in chain
            work_dir = real_path_from_list(args, 0) # first argument is working directory
            if work_dir is None:
                halt(3, "No project (work) directory specified")
                return # only for pylance
            #self.context.more_args = args[2:] # lets keep in instance var list having values starting from third from
            self.sql_profiles_text: str = read_content_of_file(work_dir + "/conf/profiles.yaml") or ""
            self.sql_drivers_text: str = read_content_of_package_file("dapu", "connections.yaml") or ""
            hub = Hub(self.sql_profiles_text, self.sql_drivers_text) # dbpoint gets all sql-type profiles 
            self.context = DapuContext(work_dir, hub)
            self.context.tags = args[1:] if len(args) > 1 and args[1] is not None else []
            self.prepare_notifier() # rare messages only (expesive logging)
            #self.prepare_logger() # permanent logging (cheep logging) -- no need, just use loguru standard
            # self.load_project_connections() # this function uses self.context (reads consts and fills self.context.profiles) 
            #if not self.context.profiles.profile_exists(self.context.PROFILE_TYPE_SQL, self.context.TARGET_ALIAS): # check if sql + target exists
            #    halt(10, f"Cannot work without connection named as '{self.context.TARGET_ALIAS}'")
            if not self.check_stopper():
                halt(4, "Cannot run any more (newer version of me is present)")
            logger.debug(f"from list, work_dir is {self.context.work_dir}")
        else:
            halt(4, "Very wrong initialization")
            return
        DapuProcess.context = self.context # lets remember this instance context as static context (needed for decorator)

    def prepare_logger(self): # deprecated
        if self.context and self.context.tags:
            tags: list[str] = self.context.tags
        else:
            tags = []
        logger.remove() # if not remove then apprise got messages twice
        if not 'debug' in tags:
            logger.add(sys.stdout, level="INFO")
        else:
            logger.add(sys.stdout, level="DEBUG", backtrace=True)
        if 'discord' in tags:
            try:
                import apprise
                #from loguru import FilterDict
                discord_hook_id = os.getenv("DISCORD_HOOK_ID", "")
                discord_hook_token = os.getenv("DISCORD_HOOK_TOKEN", "")
                if discord_hook_id and discord_hook_token:
                    notifier = apprise.Apprise()
                    notifier.add(f"discord://{discord_hook_id}/{discord_hook_token}")
                    discord_level: str = "ERROR"
                    #logger.add(notifier.notify, level=f"{discord_level}", filter= FilterDict({"apprise": False})) # type: ignore - notifier.notify tagastab bool, pylance arvab, et vaja None
                    logger.add(notifier.notify, level=f"{discord_level}") # type: ignore
                    logger.info(f"Discord logging for {discord_level} is turned ON")
            except Exception as e1:
                logger.error(f"Discord via Apprise problem")
                logger.error(str(e1))

    def prepare_notifier(self):
        self.notifier = None
        try:
            import apprise
            discord_hook_id = os.getenv("DISCORD_HOOK_ID", "")
            discord_hook_token = os.getenv("DISCORD_HOOK_TOKEN", "")
            if discord_hook_id and discord_hook_token:
                self.notifier = apprise.Apprise()
                self.notifier.add(f"discord://{discord_hook_id}/{discord_hook_token}")
        except Exception as e1:
            logger.error(f"Discord via Apprise problem")
            logger.error(str(e1))

    def notify(self, message: str):
        try:
            if self.notifier is None:
                return
            self.notifier.notify(message, title="Dapu")
        except:
            logger.error(f"Notifier problem")


    def check_stopper(self) -> bool:
        """
        Prevents execution it newer version is unleached. 
        Current version is stored in code (context.MYVERSION) and Last version is store in database (meta.stopper.allowed_version)
        If current is lower then prevent. If current is higher then update database (so old instances in wild can be prevented).
        Can be executed before tables are done, so error in select can be interpreted as missing table and lets continue.
        If table exists we can handle both cases: no rows and one row (if more then last taken, but updated will be all)
        """
        if self.context is None:
            return False
        stopper = self.context.find_registry_table_full_name('stopper')
        sql = f"""SELECT allowed_version FROM {stopper} ORDER BY id DESC LIMIT 1""" # there is one row actually
        try:
            result_set = self.context.target(sql)
        except Exception as e1:
            # error may happen on very first execution then tables are not present yet
            # in this case we just ignore everything and we are sure that in next run it will work
            return True
        allowed_version = 0
        no_rows = True
        if result_set and result_set[0]:
            allowed_version = result_set[0][0]
            no_rows = False
        if self.context.MYVERSION < allowed_version: # cannot execute any more
            logger.info(f"My version is {self.context.MYVERSION}, allowed version is {allowed_version}")
            return False
        if self.context.MYVERSION > allowed_version: # update database with my number
            if no_rows:
                sql_upd = f"""INSERT INTO {stopper} (allowed_version) VALUES ({self.context.MYVERSION})"""
            else:
                sql_upd = f"""UPDATE {stopper} SET allowed_version = {self.context.MYVERSION} WHERE true""" # one record
            self.context.target(sql_upd, False)
            logger.info(f"Stopper version updated to {self.context.MYVERSION}")
        return True


    def load_project_connections(self) -> None:
        """
        Loads all three types of profiles into self.context.profiles
        """
        if self.context is None:
            return None
        conf_files = [self.context.CONF_SQL_FILE_NAME, self.context.CONF_FILE_FILE_NAME, self.context.CONF_API_FILE_NAME]
        types = ['sql', 'file', 'api']
        for pos, type in enumerate(types):
            file_full_name = self.context.full_name_from_conf(conf_files[pos])
            if file_full_name is None:
                continue
            logger.debug(f"Reading file {file_full_name} for {type}") 
            text_content: str = read_content_of_file(file_full_name) or ""
            if type == 'sql':
                self.sql_profiles_text = text_content
            if text_content:
                list_of_profiles: list[dict] | None = yaml_string_to_list(text_content) ##### FIXME -> kas see peaks olema dict nüüd ???
                if list_of_profiles:
                    self.context.profiles.profiles_add(type, [replace_dict(profile) for profile in list_of_profiles])
                else:
                    logger.debug(f"File {file_full_name} interpretation as YAML gives empty list")
            else:
                logger.debug(f"File {file_full_name} is empty or not existing")
                       
    
    def check_for_schema(self, schema_name: str, create_if_missing: bool = True) -> bool:
        """
        Using Postgre meta-knowledge to ask if schema exists, and creating it if instructed
        Wrong input (dot in name, empty name) results to False. Apostrophes will be thrown away.
        Returns True - if schema exists (already or was created now)
        """
        schema_name = prepare_schema_name(schema_name)
        if schema_name == "":
            return False
        sql_sch = f"SELECT count(*) FROM information_schema.schemata WHERE schema_name = '{schema_name}'"
        capsule: DataCapsule = self.context.target(sql_sch)
        if capsule[0][0] > 0: # schema exists
            return True
        
        if create_if_missing: # FIXME creation add-ons are needed probably
            sql_cre = f"""CREATE SCHEMA IF NOT EXISTS {schema_name}""" # FIXME we miss here: alter default priviledges, grant usage etc
            self.context.target(sql_cre, False) # let it crash if problem (it is really fatal)
            msg = f"Schema '{schema_name}' created"
            logger.info(msg)
            return True
        
        return False
    
    
    def find_task_dir_path(self, task_id: str, must_exists: bool=False) -> str | None:
        """
        Full path from task_id (gives 3 directories) and self.context root path (work_dir)
        """
        #logger.debug(f"TASK {task_id}")
        if not self.context:
            return None
        if not task_id:
            logger.error(f"Empty task_id {task_id}")
            return None
        if not self.context or self.context.work_dir is None:
            logger.error(f"Context work_dir is missing for task {task_id}")
            return None
        path_way: list = task_id.split('.')
        if len(path_way) < 3:
            logger.error(f"Too short task_id {task_id}")
            return None
        path: str = self.context.full_name_from_pull(path_way) or ""
        if must_exists and not os.path.exists(path):
            logger.error(f"Path {path} for task '{task_id}' not exists in local file system")
            return None
        return path
    

    def find_task_file_path(self, task_id: str, file_in_task: str, must_exists:bool=False) -> str | None:
        """
        Very similar to prev, but the name carries difference
        """
        #logger.debug(f"TASK {task_id}, FILE {file_in_task}")
        if not self.context:
            return None
        if not task_id:
            logger.error(f"Empty task_id {task_id}")
            return None
        if not file_in_task:
            logger.error(f"Empty file_in_task {file_in_task} fot {task_id}")
            return None
        if self.context.work_dir is None:
            logger.error(f"Context work_dir is missing for {file_in_task}")
            return None
        path_way: list = task_id.split('.')
        path_way.append(file_in_task)
        if len(path_way) < 4:
            logger.error(f"Too short task_id {task_id} OR missing file")
            return None
        path: str = self.context.full_name_from_pull(path_way) or ""
        if must_exists and not os.path.exists(path):
            return None
        return path


    def find_route_dir_path(self, route_code: str, must_exists:bool=False) -> str |None:
        # joins together working directory and route code assuming that latter is subfolder
        # returns None on errors      
        if not self.context:
            return None
        if not route_code:
            logger.error(f"Empty route_code {route_code}")
            return None
        if self.context.work_dir is None:
            logger.error(f"Context work_dir is missing for route {route_code}")
            return None
        path: str = self.context.full_name_from_pull(route_code) or ""
        if must_exists and not os.path.exists(path):
            logger.error(f"Path {path} for route '{route_code}' not exists in local file system")
            return None
        return path


    def get_database_time(self, precise_time: bool=True):
        """
        Time in target database as ISO string. 
        Non-precise time is transaction start time (current_timestamp).
        """
        if not self.context:
            return None
        if precise_time:
            sql = "SELECT clock_timestamp()" # Very current time (inside transaction)
        else:
            sql = "SELECT current_timestamp" # Transaction beginning time
        result_set = self.context.target(sql)
        if result_set:
            return result_set[0][0] # ISO string
        return None
    

    def connect_main(self):
        """
        Due connection is always automatic, for validation you must run some safe SQL Select
        """
        if self.get_database_time(False) is None:
            raise Exception("Connection validation failed")


    def disconnect_main(self):
        if self.context:
            self.context.disconnect_target()
    
    
    def disconnect_all(self):
        if self.context:
            self.context.disconnect_all()
        

    def version(self, do_log=True, do_print=False) -> str:
        if is_interactive():
            ver_info = 'noname x.x.x'
        else:
            # FIXME järgmine rida ei tööta kui on nt jupyter vms interpreeter
            path = str(sys.modules[self.__module__].__file__) # tegeliku alamklassi failinimi
            name = os.path.basename(path).split(os.path.sep)[-1]
            ver = version_string_from_timeint(os.path.getmtime(path)) # local time (good enough)
            ver_info = f"{name} {ver}"
        if do_print:
            print(ver_info)
        if do_log:
            logger.info(ver_info)
        return ver_info

    @classmethod
    def task_id_eventlog(cls, flag: str, content: str|None = None) -> Callable: # decorator! very special!
        """
        Decorator will insert worker_log record with desired flag. And return INT (number of rows got).
        Use decorator for function which returns result set (list on tuples) where 1st in tuple is task_id.
        Uses cls.context - so it must remain as class variable (somehow duplicating instance variable)
        """
        # if cls.context is None:
        #     def nonsense(func: Callable[..., list[tuple]]) -> Callable:
        #         def wrapper(*args: Any, **kwargs: Any) -> int |None:
        #             return None
        #         return wrapper
        #     return nonsense
        
        flag = flag.upper().replace("'", "").strip()
        content_literal = "NULL"
        if content is not None:
            content = content.replace("'", "").strip()
            content_literal = f"'{content}'"

        def inner(func: Callable[..., list[tuple]]) -> Callable:
            def wrapper(*args: Any, **kwargs: Any) -> int:
                result_set = func(*args, **kwargs) # moving towards DataCapsule here instead of list
                if result_set is None: # error
                    logger.warning("Unexpected None as Datacapsule")
                    return 0
                if not result_set: # empty
                    logger.debug(f"No result for {flag}, by not")
                    return 0
                if len(result_set) == 0:
                    logger.debug(f"No result for {flag}, by len")
                    return 0
                if cls.context is None:
                    logger.warning("Unexpected missing context")
                    return 0
                worker_log = cls.context.find_registry_table_full_name('worker_log')
                try:
                    for changed_row in result_set:
                        changed_row_task_id = changed_row[0]
                        if cls.context.worker_id is None:
                            worker_literal = "NULL"
                        else:
                            worker_literal = cls.context.worker_id
                        sql_reg_log = f"""INSERT INTO {worker_log} (worker, task_id, flag, content) 
                            VALUES ({worker_literal}, '{changed_row_task_id}', '{flag}', {content_literal})"""
                        cls.context.target(sql_reg_log, False)
                    count_of_logged = len(result_set)
                    logger.info(f"{count_of_logged} for {flag}") 
                    return count_of_logged
                except Exception as e1:
                    logger.error(f"during task log {e1}")
                    return 0
            return wrapper
        return inner
