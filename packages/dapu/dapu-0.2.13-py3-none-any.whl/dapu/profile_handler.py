from loguru import logger

class ProfileHandler: # name <= py has package named "profile"
    """
    Handles different list of dicts.
    Every list if referenced by name (profile_type). Every list has objects (dict) which MUST HAVE key "name" (alias).
    For dapu we need profile_types 'sql', 'file', 'api'. And in 'sql' profile_type where must profile with alias 'target'
    
    Has functions in singular and plural! (profile vs profiles). 
    """
    
    def __init__(self):
        self.data: dict[str, list[dict]] = {}
        self.name_key = 'name' # key for keeping alias aka name of profile
        
    def profile_exists(self, profile_type: str, alias: str) -> bool:
        """
        Does we have any profiles of profile_type and amoungst them profile named by alias 
        """
        #logger.debug(f"Request for '{alias}' of type '{profile_type}'")
        list_of_profiles_of_type: list[dict] | None = self.data.get(profile_type, None)
        if not list_of_profiles_of_type:
            logger.warning(f"No profiles of type '{profile_type}'")
            return False # no such type profiles
        for one_profile in list_of_profiles_of_type:
            #logger.debug(f"Profile python type is '{type(one_profile)}'")
            #logger.debug(f"name is {one_profile.get(self.name_key)}")
            if isinstance(one_profile, dict) and one_profile.get(self.name_key) == alias:
                return True
        logger.error(f"No profiles with alias '{alias}'")
        return False # no profile with such name

    def profile_get(self, profile_type: str, alias: str) -> dict | None:
        """
        Return copy of profile of desired profile_type and name (first appearance if by mistake many exists)
        """
        list_of_profiles_of_type: list[dict] | None = self.data.get(profile_type, None)
        if not list_of_profiles_of_type:
            logger.warning(f"No profiles of type '{profile_type}'")
            return None # no such profile_type profiles
        for one_profile in list_of_profiles_of_type:
            if isinstance(one_profile, dict) and one_profile.get(self.name_key) == alias:
                return one_profile.copy()
        logger.error(f"No profiles with alias '{alias}'")
        return None # no profile with such name
      
    def profile_add(self, profile_type: str, profile: dict | None) -> bool:
        """
        Add one dict as profile for mentioned profile_type (no clean-up, so there may be similar dict)
        Profile must have key 'name'  
        """
        #logger.debug(f"Adding type {profile_type} profile")
        if profile is None: # no profile, no adding
            logger.error("Profile is none")
            return False
        if not profile.get(self.name_key, None): # badly formed profile
            logger.warning(f"Profile don't have name ('{self.name_key}' is missing)")
            return False
        if not profile_type in self.data: # if first of such profile_type
            self.data[profile_type] = [] # lets make empty list
            logger.debug(f"First of profile_type {profile_type}")
        self.data.get(profile_type, []).append(profile) # and append to list
        return True
    
    def profiles_set(self, profile_type: str, list_of_profiles: list[dict]):
        """
        Cleans one profile_type of profiles and overrides with new list of profiles 
        (no validation is made, just dummy assign)
        """
        self.data[profile_type] = list_of_profiles
               
    def profiles_add(self, profile_type: str, list_of_profiles: list[dict]) -> int:
        """
        Add all profiles in list to existing profiels of same type
        For adding profile must have key 'name'. Those without won't be added.
        """
        profiles_added: int = 0
        for one_profile in list_of_profiles:
            #logger.debug(one_profile)
            profiles_added += 1 if self.profile_add(profile_type, one_profile) else 0
        return profiles_added
    
    def profiles_get(self, profile_type: str) -> list[dict] | None:
        """
        Returns list of profiles of one profile_type (for example for dbpoint.Hub init)
        """
        return self.data.get(profile_type, None)
