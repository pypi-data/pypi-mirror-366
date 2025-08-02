from loguru import logger
import os
from typing import Any
from dbpoint.hub import Hub
from dbpoint.datacapsule import DataCapsule

from dapu.profile_handler import ProfileHandler
from .textops import yaml_string_to_dict
from .fileops import read_content_of_file, read_content_of_package_file

class DapuContext():
    """
    One central class which have one instance what can be given as starting point to all next Dapu-sh components
    (Workers inits Job and Job inits Manager, using context, context values are calculated in very first process in sequence)
    """
    def __init__(self, work_dir: str, hub: Hub) -> None:

        self.work_dir: str | None = work_dir # target directory (=src in source code, see "layout"), must be initialized
        self.tags: list[str] = [] # clear known arguments (eg. debug)
        self.more_args: list = [] # and other unclear arguments
        self.LOG_LEVEL : int = 20 # don't use here enums directly from logging (cycle will occur!)

        # Critical version: myversion vs meta.stopper.allowed_version
        self.MYVERSION = 2 # int, increment it every time if needed to prevent previous code to start any more

        self.CONF_SUB_DIR: str = 'conf' # fixed! this folder may have conf.yaml for overriding default hard-coded here
        self.CONF_FILE_NAME: str = 'conf.yaml' # if not existing defaults are used (application level fine tuning)

        self.PACKAGE_NAME : str = 'dapu' # for dynamic loading
        self.PACKAGE_VER_SUB_DIR: str = 'ver' # has meaning of "submodule" under module above, keeps core versioning files

        self.PROJECT_VER_SUB_DIR: str = 'ver' # sub dir for custom versioning 
        self.CHANGES_INDEX_FILE_NAME = 'changes.yaml' # same name for both core and custom versioning
        self.TABLE_VER_SUB_DIR: str = 'ver' # for target tables versioning (last part in path /mytarget/ver), here no index file (just numbers)

        self.ROUTES_SUB_DIR: str = 'routes' # for target tables definitions (last part in path mytarget/routes)
        self.ROUTE_FILE_NAME = 'route.yaml' # inside dir directly under pull (mytarget/pull/from_asjur5/route.yaml)

        self.APP_NAME : str = 'dapu' # for logging and temp dir under system-wide temp dir (don't use spaces, don't live complicated life)
        
        self.PROFILE_TYPE_SQL: str = 'sql'        
        self.PROFILE_TYPE_API: str = 'api'
        self.PROFILE_TYPE_FILE: str = 'file'
        self.CONF_API_FILE_NAME: str = f'{self.PROFILE_TYPE_API}.yaml' # inside conf directory
        self.CONF_FILE_FILE_NAME: str = f'{self.PROFILE_TYPE_FILE}.yaml' # inside conf directory

        self.TARGET_ALIAS: str = 'target' # main connection name/reference (to database where meta tables reside)
        self.CONF_SQL_FILE_NAME: str = f'{self.PROFILE_TYPE_SQL}.yaml' # inside conf directory
        self.DAPU_SCHEMA = 'meta' # the latest idea: lets call schema this way, just "meta"
        self.DAPU_PREFIX = '' # and lets prefix all tables in above mentioned schema this way (no prefix)

        
        self.list_of_profiles : list[dict] # profiles for rdbms (must think, where to keep api and file access profiles)
        self.profiles: ProfileHandler = ProfileHandler() # empty object
        self.hub: Hub = hub
        self.agents: dict[str, dict] = {} # agents meta will be loaded on first call of get_agents
        self.agents_loaded = False

        # Cleaner:
        self.DELETE_LOGS_OLDER_THEN: str = "2 months"
        self.DELETE_TRACE_LOGS_OLDER_THEN: str = "15 days"
        self.DELETE_AGENDA_OLDER_THEN: str = "14 months" # PROD keskkonnas soovituslik vähemalt aasta, nt 14 months

        # Registrar:
        self.FILENAME_DEFINITION_FILE: str = 'haulwork.yaml' # NB! lowercase!!
        self.FILENAME_FOR_DELETION = 'tasks_to_delete.txt' # file inside conf (mytarget/conf/tasks_to_delete.txt)
        
        # Manager
        self.FAILURE_LIMIT : int = 3
        self.DEFAULT_MANAGER_INTERVAL: str = '4 hours'
        self.DEFAULT_KEEP_GOING_INTERVAL: str = '5 hours' # '2 minutes' # '2 days' # valid PG interval, 

        # Worker
        self.worker_id : int | None = None
        self.WORKER_NO_NEW_HAUL_AFTER_MINUTES: int = 27
        self.AGENTS_INDEX_FILE_NAME = 'agents.yaml' # in root of dapu, in the target dir (work_dir) if custom are needed

        self.override_configuration() # overriding, customization
        
    def override_configuration(self) -> None:
        """
        If conf subfolder has conf.yaml file, let read values from where and override instance variables here
        """
        conf_file_full_name: str = self.full_name_from_conf(self.CONF_FILE_NAME) or ""
        if not conf_file_full_name:
            return 
        logger.info(f"looking for conf in file {conf_file_full_name}")
        content = read_content_of_file(conf_file_full_name)
        if not content:
            return # no content, no problem (both empty content and missing of file are reasons to keep hard-coded conf) 
        reconf: dict = yaml_string_to_dict(content) or {}
        if not reconf:
            return
        # TODO / FIXME make it more dynamic (but static is more secure)
        # from dict key to assign self var with same name, if key missing use original value
        # TODO / FIXME validate somehow
        self.APP_NAME = reconf.get('APP_NAME', self.APP_NAME)
        self.DAPU_SCHEMA = reconf.get('DAPU_SCHEMA', self.DAPU_SCHEMA)
        self.DAPU_PREFIX = reconf.get('DAPU_PREFIX', self.DAPU_PREFIX)
        self.FILENAME_FOR_DELETION = reconf.get('FILENAME_FOR_DELETION', self.FILENAME_FOR_DELETION)
        self.FILENAME_DEFINITION_FILE = reconf.get('FILENAME_DEFINITION_FILE', self.FILENAME_DEFINITION_FILE)
        self.FAILURE_LIMIT = reconf.get('FAILURE_LIMIT', self.FAILURE_LIMIT)
        self.DEFAULT_MANAGER_INTERVAL = reconf.get('DEFAULT_MANAGER_INTERVAL', self.DEFAULT_MANAGER_INTERVAL)
        self.DEFAULT_KEEP_GOING_INTERVAL = reconf.get('DEFAULT_KEEP_GOING_INTERVAL', self.DEFAULT_KEEP_GOING_INTERVAL)
        
    def get_agent_definition(self, agent_alias: str) -> dict | None:
        """
        For dynamical load of module which will do action we need all allowed packages/modules defined.  
        We trust our own modules (built-in dapu.agents.agent_...) and may-be some external.
        """
        if not agent_alias:
            return None
        if not self.agents_loaded:
            self.load_agents_index()
        agent: dict | None = self.agents.get(agent_alias) # või None
        return agent

    def load_agents_index(self):
        """
        If agents definitions (alias -> package & module) are not loaded yet, lets do it.
        Definitions can be locally built in or current loading project ones.
        """
        core_agents: dict = yaml_string_to_dict(read_content_of_package_file(self.PACKAGE_NAME, self.AGENTS_INDEX_FILE_NAME)) or {}
        custom_agents = {}
        try:
            with open(self.full_name_from_conf(self.AGENTS_INDEX_FILE_NAME), 'r', encoding='utf-8') as file:
                content = file.read()
            custom_agents = yaml_string_to_dict(content) or {}
        except Exception as e1:
            pass # custom agents listing file don't need to exists
        self.agents = core_agents | custom_agents # | needs 3.9+
        self.agents_loaded = True
        
    def run(self, alias: str, sql: str | DataCapsule, do_return: bool = True, **kwargs: dict) -> DataCapsule:
        """ Wrapper """
        if isinstance(sql, str):
            capsule = DataCapsule(sql)
        else:
            capsule = sql
        if not do_return:
            capsule.set_flag("do_return", False)
        if "verbose" in self.tags:
            capsule.set_flag("verbose", True)
            logger.debug("VERBOSE SQL")
        return self.hub.run(alias, capsule)

    def target(self, sql: str | DataCapsule, do_return: bool = True, **kwargs: dict) -> DataCapsule:
        """ Wrapper """
        return self.run(self.TARGET_ALIAS, sql, do_return)
    
    def disconnect_target(self):
        """ Wrapper """
        self.hub.disconnect(self.TARGET_ALIAS)

    def disconnect_all(self):
        """ Wrapper """
        self.hub.disconnect_all()

    def disconnect_alias(self, profile_name: str):
        """ Wrapper """
        self.hub.disconnect(profile_name)

    def full_name_from_root(self, inner_part: str | list[str]):
        return self._full_name(inner_part)
    
    def full_name_from_pull(self, inner_part: str | list[str]):
        """ Project level routes root, usually mytarget/routes (old way: mytarget/pull) """
        if isinstance(inner_part, str):
            inner_part = [inner_part]
        return self._full_name([self.ROUTES_SUB_DIR, *inner_part])
    
    def full_name_from_ver(self, inner_part: str | list[str]): 
        """ Custom overall versioning, usually mytarget/ver """
        if isinstance(inner_part, str):
            inner_part = [inner_part]
        return self._full_name([self.PROJECT_VER_SUB_DIR, *inner_part])
    
    def full_name_from_conf(self, inner_part: str | list[str]): 
        """ Custom overall conf, usually /conf """
        if isinstance(inner_part, str):
            inner_part = [inner_part]
        return self._full_name([self.CONF_SUB_DIR, *inner_part])

    def _full_name(self, inner_part: str | list[str]) -> str:
        """
        Returns full name of inside file object (dir or file) short name (or list of part components).
        Don't use it directly! Private function ;)
        """
        import os
        if not self.work_dir:
            raise Exception("work_dir don't have value")
        if not inner_part:
            raise Exception("inner part is missing")
        if isinstance(inner_part, str):
            return os.path.join(self.work_dir, inner_part)
        if isinstance(inner_part, list):
            return os.path.join(self.work_dir, *inner_part)
        raise Exception(f"inner part type is wrong {type(inner_part)}")

    #@lru_cache(maxsize=120, typed=False) -> CacheInfo(hits=24, misses=19, maxsize=120, currsize=19) 
    # not very helpful: there are max 7 different arguments (table_short_name), why 19 misses?
    #@cache # now it may have point to use cache (now = after remaking this as context own function)
    def find_registry_table_full_name(self, table_short_name: str) -> str:
        #logger.debug(f"Usage of {table_short_name}")
        """
        from short name makes full table name according to system global setup (compatibility with historical ideas)
        "agenda" -> "meta.bis_agenda" or "bis.agenda" or "bis.bis_agenda"
        """
        schema_part = ''
        if self.DAPU_SCHEMA is not None and self.DAPU_SCHEMA.strip() > '': # if schema name is present
            schema_part = self.DAPU_SCHEMA.strip() + '.' # dot at end as seperator between schema name and table name      
        table_prefix = ''
        if self.DAPU_PREFIX is not None and self.DAPU_PREFIX.strip() > '':
            table_prefix = self.DAPU_PREFIX.strip()
        
        return ('').join([schema_part, table_prefix, table_short_name])

    def find_loaded_profile(self, profile_name: str) -> dict: # FIXME -- used??? redo to context.profiles.
        name_key: str='name'
        profile: dict = {}
        for one_profile in self.list_of_profiles:
            if isinstance(one_profile, dict) and one_profile.get(name_key) == profile_name:
                profile = one_profile.copy()
                break
        return profile
   
    def get_task_hash_from_registry(self, task_id: str) -> str:
        """
        Get the latest saved hash of source data (in case of file it is hash of file) 
        """
        registry = self.find_registry_table_full_name("registry")
        
        sql_hash = f"""SELECT r.source_hash FROM {registry} r WHERE task_id = '{task_id}'"""
        result_set = self.target(sql_hash)
        return result_set[0][0] # hash as string
       
    def save_task_hash_to_registry(self, task_id: str, new_hash: str) -> None:
        """
        Updates source_hash for task_id
        """
        registry = self.find_registry_table_full_name("registry")
        sql_hash = f"""UPDATE {registry} SET source_hash = '{new_hash}' WHERE task_id = '{task_id}'"""
        self.target(sql_hash, False)
    
    def get_task_sync_until_ts(self, task_id: str, precision: int = 6) -> str:
        """
        Returns tasks sync time (as ISO date string with seconds).
        Use of precision over 0 demands PostgreSQL version 13 // in PG12 were possible '000' as 'MS' and '000000' as 'US'
        """
        registry = self.find_registry_table_full_name("registry")
        
        expression_missing_pg: str = '1990-01-01 00:00:00' # .000000
        format_to_char = 'YYYY-MM-DD HH24:MI:SS' # .FF6
        if precision >= 1 and precision <= 6:
            expression_missing_pg += '.' + ('0' * precision)
            format_to_char += '.FF' + str(precision) 
        
        sql_last_ts = f"""SELECT to_char(coalesce(synced_until_ts, '{expression_missing_pg}'), '{format_to_char}')
            FROM {registry} WHERE task_id = '{task_id}' """
        result_set = self.target(sql_last_ts)
        return result_set[0][0] # return ISO DATE/TIME as string

    def save_task_sync_until_ts(self, task_id: str, new_ts: str | None, precision: int = 6):
        """
        new_ts must be ISO date, its precision may be higher or lower then parameter precision
        if new_ts is None, then NULL will be set to database
        """
        registry = self.find_registry_table_full_name("registry")
        if new_ts is None:
            time_expression = 'NULL'
        else:
            time_expression = f"'{new_ts}'"
        
        sql_upd = f"UPDATE {registry} SET synced_until_ts = {time_expression} WHERE task_id = '{task_id}'"
        self.target(sql_upd, False)

    def replace_compatibility(self, sql: str, local_replacements : list[tuple] = []) -> str:
        """
        Owner is nice trick here (so each new schema can be created with minimal effort (copy-paste))
        """
        replacements = []
        replacements.append(('{schema}', self.DAPU_SCHEMA))
        replacements.append(('{prefix}', self.DAPU_PREFIX))
        replacements.append(('{owner}', self.hub.get_profile(self.TARGET_ALIAS)['username'])) # after schema create
        for local_replacement in local_replacements: # orvuke tegelt (orphan, never assigned yet)
            replacements.append(local_replacement) # tuple[str, str]
        
        for replacement in replacements:
            sql = sql.replace(replacement[0], replacement[1])
        return sql
   