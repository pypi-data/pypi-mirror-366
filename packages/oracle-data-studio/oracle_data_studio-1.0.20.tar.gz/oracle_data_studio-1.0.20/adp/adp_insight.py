'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

import json
from .rest import Rest
from .adp_misc import AdpMisc
from .adp_analytics import AdpAnalytics

class AdpInsight():
    '''
    classdocs
    '''
    def __init__(self):
        self.rest=None
        self.analytics=None
        self.misc=None


    def set_rest(self, rest : Rest) -> None:
        '''
            Set Rest instance
            
            @param rest (Rest): rest instance
        '''
        self.rest = rest
        self.analytics = AdpAnalytics()
        self.analytics.set_rest(rest)
        self.misc = AdpMisc()
        self.misc.set_rest(rest)

    def generate(self, av_name : str, measure : str, job_owner : str = None, object_owner : str = None) -> str:
        '''
            Generate insight of the measure for the Analytic view 
            @param avName (String): name of the Analytic view
            @param measure (String): name of the measure of the Analytic view 
            @param job_owner (String): schema name of the job (None means that the current schema is used)
            @param object_owner (String): schema name of the object (None means that the current schema is used)
        '''
        text = self.analytics.get_list()
        json_obj = json.loads(text)

        analytic_list = []

        for row in json_obj['nodes']:
            analytic_list.append(row['data']['name'])


        text = self.misc.list_tables()
        json_obj = json.loads(text)

        tables = []

        for row in json_obj['nodes']:
            tables.append(row['data']['name'])

        #print(tables)

        object_type = None

        if av_name in analytic_list:
            object_type = 'ANALYTIC_VIEW'

        if av_name in tables:
            object_type = 'TABLE'

        if object_type is None:
            return "{\"message\":\"Object name does not exist\"}"

        if job_owner is None:
            job_owner = self.rest.username
        if object_owner is None:
            object_owner = self.rest.username


        payload = {"job_owner" : job_owner, "max_insight_count": 20, "name": av_name,
                   "object_owner": self.rest.username, "object_type": object_type,
                   "request_job_settings": "{\"insightTypes\":[\"FITTED_SHARE_COMPARISON\"]}",
                   "request_metadata": "{\"targets\":[\""+ measure + "\"], \"appName\":\"INSIGHTS\"}", 
                   "request_owner": job_owner,
                   "appName":"INSIGHTS"
                   }
        url="{}/_adpins/_services/insights/generateinsight/".format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def drop(self, request_name : str) -> str:
        '''
            Drop insight 
            @param requestName (String): name of request
        '''
        payload = {"request_name": request_name }
        url="{0}/_adpins/_services/insights/dropinsightrequest/".format(self.rest.get_prefix())
        self.rest.post(url, payload)
        return "success"

    def get_request_list(self, owner : str = None) -> list:
        '''
            Get list of insight request names
            @param owner (String): schema name of the source object (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username

        url="{0}/_adpins/_services/objects/insightrequestlist/?SOURCE_OWNER={1}".format(self.rest.get_prefix(), self.rest.username)
        text = self.rest.get(url)
        json_objects = json.loads(text)

        return json_objects.get("items")

    def get_insights_list(self, request_name : str) -> list:
        '''
            Get list of insights for the specified request name 
            @param requestName (String): name of request
        '''
        url = "{0}/_adpins/_services/objects/insightslist/?offset=0&request_name={1}".format(self.rest.get_prefix(), request_name)
        text = self.rest.get(url)
        json_objects = json.loads(text)
        insight_names = []

        items = json_objects.get("items")
        for item in items:
            insight = {}
            insight["insight_name"] = item["insight_name"]
            insight["visualization_id"] = item["visualization_id"]
            insight["insight_column"] = item["insight_column"]
            insight["insight_value"] = item["insight_value"]
            insight["insight_dimension"] = item["insight_dimension"]
            insight["dimension"] = item["dimension"]
            insight_names.append(insight)

        return insight_names

    def get_graph_details(self, name : str, viz_id : int, count : int = 0, query_manipulation : bool = None, owner : str = None) -> dict:
        '''
            Get graph details for the insight 
            @param name (String): name of insight
            @param id (String): Id of the visualization
            @param count (Integer): Number of values
            @param queryManipulation (boolean): Add cursor types
            @param owner (String): schema name of the object (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username

        url="{0}/_adpins/_services/insights/graph-details/?owner={1}&viz_id={2}&insight_name={3}".format(self.rest.get_prefix(), owner, viz_id, name)
        if query_manipulation is not None:
            url = url + "&cursorTypes=CHART&grandTotals=true"
        if count > 0:
            url = "{0}&rowSize={1}".format(url, count)

        text = self.rest.get(url)
        json_objects = json.loads(text)
        items = json_objects.get("items")[0]
        query = json_objects.get("query-result")
        measure = items["measure"]
        labels = []
        actuals = []
        estimates = []
        targets = []
        probabilities = []
        scores = []
        z_scores = []
        totals = []
        rows = []
        differences = []
        remainder_values = []
        remainder_counts = []
        for item in query:
            labels.append(item["X_AXIS_LABEL"])
            actuals.append(item[measure])
            estimates.append(item["ESTIMATE_1"])
            targets.append(item["TARGET"])
            probabilities.append(item["INSIGHT_PROBABILITY"])
            scores.append(item["INSIGHT_SCORE"])
            z_scores.append(item["INSIGHT_Z_SCORE"])
            totals.append(item["GRAND_TOTAL"])
            rows.append(item["NUM_ROWS"])
            differences.append(item["DIFFERENCE_1"])
            remainder_values.append(item["REMAINDER_VALUE"])
            remainder_counts.append(item["REMAINDER_COUNT"])


        results = {"items": {"description": items["short_description"], "XAXIS": items["XAXIS"],
                             "insight_description": items["insight_description"],
                             "measure": measure, "insight_type_label": items.get("insight_type_label"),
                             "visualization_condition": items.get("visualization_condition"),
                             "source_object": items.get("source_object")},
        "query":{"X_AXIS_LABEL": labels, "ACTUALS": actuals, "ESTIMATES": estimates, "TARGETS": targets, "INSIGHT_PROBABILITIES": probabilities,
            "INSIGHT_SCORES": scores, "INSIGHT_Z_SCORES": z_scores, "GRAND_TOTALS" :totals, "NUM_ROWS": rows,"DIFFERENCES": differences,
            "REMAINDER_VALUES": remainder_values, "REMAINDER_COUNTS": remainder_counts}}
        return results

    def get_job_status(self, request_name : str, owner : str = None) -> str:
        '''
            Get request job status
            
            @param requestName (String): name of the request
            @param owner (String): schema name of the job (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username

        url = "{0}/_adpins/_services/objects/insight-job-status/?schema_owner={1}&request_name={2}".format(self.rest.get_prefix(), owner, request_name)
        return self.rest.get(url)
