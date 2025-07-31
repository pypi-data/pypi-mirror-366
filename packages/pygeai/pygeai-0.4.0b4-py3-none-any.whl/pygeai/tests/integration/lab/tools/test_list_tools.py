from unittest import TestCase
from pygeai.lab.managers import AILabManager
from pygeai.lab.models import ToolList, FilterSettings
import copy

ai_lab_manager: AILabManager

class TestAILabListToolsIntegration(TestCase):    

    def setUp(self):
        self.ai_lab_manager = AILabManager(alias="beta")
        self.filter_settings = FilterSettings(
            allow_external=False,
            allow_drafts=True,
            access_scope="private"
        )
    """ list-tools or lt            List tools
        --project-id or --pid           ID of the project
        --id                    ID of the tool to filter by. Defaults to an empty string (no filtering).
        --count                 Number of tools to retrieve. Defaults to '100'.
        --access-scope          Access scope of the tools, either "public" or "private". Defaults to "public".
        --allow-drafts          Whether to include draft tools. Defaults to 1 (True).
        --scope                 Scope of the tools, must be 'builtin', 'external', or 'api'. Defaults to 'api'.
        --allow-external                Whether to include external tools. Defaults to 1 (True). """

    def __list_tools(self, filter_settings: FilterSettings = None):
        filter_settings = filter_settings if filter_settings != None else self.filter_settings
        return self.ai_lab_manager.list_tools(filter_settings=filter_settings)
    
    def test_private_list_tools(self):
        result = self.__list_tools()
        self.assertIsInstance(result, ToolList , "Expected a list of tools") 
        print(result)
        for tool in result.tools:
            self.assertTrue(tool.access_scope == "private", "Expected all tools to be private")
        


