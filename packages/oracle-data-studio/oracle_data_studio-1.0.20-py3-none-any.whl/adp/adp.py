'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

from .adp_misc import AdpMisc
from .adp_analytics import AdpAnalytics
from .adp_ingest import AdpIngest
from .adp_insight import AdpInsight
from .adp_share import AdpShare
from .rest import Rest
from .adp_dataframe import AdpDataframe
from .adp_ai import AdpAI
from .adp_catalog import AdpCatalog


class Adp:
    '''
    A class used to represent ORDS API
    '''
    def __init__(self, rest : Rest) -> None:
        self.set_rest(rest)
        # pylint: disable-msg=C0103
        self.Analytics = self.InAnalytics(rest)
        self.Ingest = self.InIngest(rest)
        self.Insight = self.InInsight(rest)
        self.Misc = self.InMisc(rest)
        self.Share = self.InShare(rest)
        self.Catalog = self.InCatalog(rest)
        self.AI = self.InAI(rest)
        self.dt = None

    class InAI(AdpAI):
        '''
            Class for select AI
        '''
        def __init__(self, rest : Rest) -> None:
            super().__init__()
            super().set_rest(rest)

    def setDataTransforms(self,datatransforms):
        self.dt = datatransforms

    def datatransforms(self):
        '''
        Method returns DataTransforms Workbench
        '''
        return self.dt

    def dataframe(self, table_name: str):
        '''
        Method to dynamically create an instance of InDataframe with table_name.
        '''
        return self.InDataframe(self.rest, table_name)  # Instantiate with table_name


    class InDataframe(AdpDataframe):
        '''
            Class for dataframe
        '''
        def __init__(self, rest : Rest, table_name: str) -> None:
            super().__init__(table_name)
            super().set_rest(rest)

    class InAnalytics(AdpAnalytics):
        '''
            Class for analytic view
        '''
        def __init__(self, rest : Rest) -> None:
            super().__init__()
            super().set_rest(rest)

    class InIngest(AdpIngest):
        '''
            Class for copy tables from db link or cloud storage
        '''
        def __init__(self, rest : Rest) -> None:
            super().__init__()
            super().set_rest(rest)

    class InInsight(AdpInsight):
        '''
            Class for insights
        '''
        def __init__(self, rest : Rest) -> None:
            super().__init__()
            super().set_rest(rest)

    class InMisc(AdpMisc):
        '''
            Class for additional functions
        '''
        def __init__(self, rest : Rest) -> None:
            super().__init__()
            super().set_rest(rest)

    class InShare(AdpShare):
        '''
            Class for additional functions
        '''
        def __init__(self, rest : Rest) -> None:
            super().__init__()
            super().set_rest(rest)

    class InCatalog(AdpCatalog):
        '''
            Class for Catalog
        '''
        def __init__(self, rest : Rest) -> None:
            super().__init__()
            super().set_rest(rest)


    def set_rest(self, rest : Rest) -> None:
        '''
            Set REST class
        '''

        self.rest = rest

    def get_rest(self) -> Rest:
        '''
            Access to Rest class
        '''
        return self.rest
