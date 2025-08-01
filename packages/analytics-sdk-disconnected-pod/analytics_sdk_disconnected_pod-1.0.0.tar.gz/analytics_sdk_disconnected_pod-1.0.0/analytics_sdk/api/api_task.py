import os
import json
import math
import copy
import logging

from .thread_process import *
from analytics_sdk.utilities import (
    BASE_API_URL,
    NO_OF_API_THREADS,
    DISABLE_API_THREADS,
    API_PAGE_SIZE,
    get_paginated_api_results,
    get_post_opsql_count_results,
    get_post_request_results,
    get_response
)

logger = logging.getLogger(__name__)

class ApiTask:
    def __init__(self, api_client, form, jwt=True):
        self.results = []
        self.api_client = api_client
        self.form = form
        self.jwt = jwt


    def get_paginated_api_results(self, method, url, data, api_type, session=None):
        if self.jwt:
            return self.api_client.get_paginated_api_results(method, url, data, api_type)
        return get_paginated_api_results(method, url, data, api_type, session=session)


    def get_post_opsql_count_results(self, url, data, api_type):
        if self.jwt:
            return self.api_client.get_post_opsql_count_results(url, data, api_type)
        return get_post_opsql_count_results(url, data, api_type)


    def get_post_request_results(self, url, data, api_type, session=None):
        if self.jwt:
            return self.api_client.get_post_request_results(url, data, api_type)
        return get_post_request_results(url, data, api_type, session=session)


    def get_response(self, url, api_type, session=None):
        if self.jwt:
            return self.api_client.get_response(url, api_type)
        return get_response(url, api_type, session=session)


    # Not using in any reporting app
    def get_opsql_results_with_threads_by_tenant(self, api_client, method='POST'):
        if self.form is not None and self.form.query_builder is not None:
            # Multi thread / Parallel processing
            if DISABLE_API_THREADS == 'false':
                pool = ThreadPool(int(NO_OF_API_THREADS))
                for query in self.form.query_builder:
                    pool.add_task(self.fetch_opsql_results_with_all_pages, api_client, query, method)
                pool.wait_completion()
                self.results = [item for sublist in self.results for item in sublist]
            else: # Sequential processing
                for query in self.form.query_builder:
                    url = BASE_API_URL + f'/opsql/api/v7/tenants/{query.tenant_id}/queries'
                    data = query.get_query()
                    result = self.get_paginated_api_results(method, url, json.dumps(data), f'V7 {data["objectType"]} OpsQL, tenant id is : {query.tenant_id} , run id is : {self.form.get_run_id()}')
                    if not result:
                        continue
                    self.results.append(result)
                self.results = [item for sublist in self.results for item in sublist]
        return self.results


    def get_opsql_results_with_threads_by_tenant_page(self, api_client, method='POST', session=None):
        if self.form is not None and self.form.query_builder is not None:
            # Multi thread / Parallel processing
            if DISABLE_API_THREADS == 'false':
                pool = ThreadPool(int(NO_OF_API_THREADS))
                for query in self.form.query_builder:
                    page_size = query.get_opsql_page_size()
                    total_results_count = self.get_opsql_total_results(api_client, query)
                    if total_results_count > 0:
                        total_pages = self.get_no_of_pages(total_results_count, page_size)
                        if total_pages > 0:
                            t_resp = []
                            page_no = 1
                            while(page_no <= total_pages):
                                q_builder = copy.copy(query)
                                q_builder.page_no = page_no
                                q_builder.page_size = page_size
                                pool.add_task(self.fetch_opsql_results, api_client, q_builder, method, session=session)
                                page_no += 1
                pool.wait_completion()
                self.results = [item for sublist in self.results for item in sublist]
            else: # Sequential processing
                for query in self.form.query_builder:
                    url = BASE_API_URL + f'/opsql/api/v7/tenants/{query.tenant_id}/queries'
                    data = query.get_query()
                    result = self.get_paginated_api_results(method, url, json.dumps(data), f'V7 {data["objectType"]} OpsQL, tenant id is : {query.tenant_id} , run id is : {self.form.get_run_id()}',session=session)
                    if not result:
                        continue
                    self.results.append(result)
                self.results = [item for sublist in self.results for item in sublist]
        return self.results

    # Not using in any reporting app
    def get_opsql_total_results(self, api_client, query):
        count = 0
        if query is not None:
            url = BASE_API_URL + f'/opsql/api/v7/tenants/{query.tenant_id}/queries/count'
            data = query.get_count_query()
            count_result = self.get_post_opsql_count_results(url, json.dumps(data), f'V7 {data["objectType"]} OpsQL, tenant id is : {query.tenant_id}')
            if count_result and count_result is not None and 'count' in count_result:
                count = count_result['count']
        return count


    # Not using in any reporting app
    def fetch_opsql_results_with_all_pages(self, api_client, query, method):
        url = BASE_API_URL + f'/opsql/api/v7/tenants/{query.tenant_id}/queries'
        data = query.get_query()
        result = self.get_paginated_api_results(method, url, json.dumps(data), f'V7 {query.object_type} OpsQL, tenant id is : {query.tenant_id}')
        if result:
            self.results.append(result)


    def fetch_opsql_results(self, api_client, query, method, session=None):
        url = BASE_API_URL + f'/opsql/api/v7/tenants/{query.tenant_id}/queries'
        data = query.get_query()
        if method == 'POST':
            res = self.get_post_request_results(url, json.dumps(data), f'V7 {query.object_type} OpsQL, tenant id is : {query.tenant_id}', session=session)
        else:
            res = self.get_response(url, f'V7 {query.object_type} OpsQL, tenant id is : {query.tenant_id}', session=session)

        result = None
        if res == None or not res.ok:
            logger.error('Get %s API is failed, url %s', f'V7 {query.object_type} OpsQL, tenant id is : {query.tenant_id}', url)
            return result
        elif "results" not in res.json() or len(res.json()['results'])==0 :
            logger.error('Get %s API results are empty, url is %s', f'V7 {query.object_type} OpsQL, tenant id is : {query.tenant_id}', url)
            return result
        else:
            if 'results' in res.json():
                result = res.json()['results']

        if result:
            self.results.append(result)


    def get_no_of_pages(self, count, page_size):
        total_pages = 0
        if count > 0:
            total_pages = math.ceil(count / page_size)
        return total_pages


    # Not using in any reporting app
    def get_results_with_all_pages(self, api_client, url, type):
        url = BASE_API_URL + url
        result = self.get_response(url, type)
        if result:
            self.results.append(result)


    # Not using in any reporting app
    def get_results_by_threads(self, api_client, url_list, type):
        self.results = []
        if url_list is not None and len(url_list) > 0:
            if DISABLE_API_THREADS == 'false':
                pool = ThreadPool(int(NO_OF_API_THREADS))
                for url in url_list:
                    pool.add_task(self.get_results_with_all_pages, api_client, url, type)
                pool.wait_completion()
            else:
                for url in url_list:
                    result = self.get_response(url, type)
                    if result:
                        self.results.append(result)
                    else:
                        continue
        return self.results


    def get_results_json_map_with_all_pages(self, api_client, url, key, type, session=None):
        url = BASE_API_URL + url
        type = type + f' key : {key}'
        # result = api_client.get_response(url, type)
        data = {}
        result = self.get_paginated_api_results('GET', url, json.dumps(data), f'{type} V2 tenant id is : {self.form.get_tenant_id()} , run id is : {self.form.get_run_id()}', session=session)
        if result:
            res = {}
            res[key] = result
            self.results.append(res)


    def get_results_json_map_by_threads(self, api_client, url_map, type, session=None):
        self.results = []
        if url_map is not None and len(url_map) > 0:
            if DISABLE_API_THREADS == 'false':
                pool = ThreadPool(int(NO_OF_API_THREADS))
                for key in url_map:
                    pool.add_task(self.get_results_json_map_with_all_pages, api_client, url_map[key], key, type, session=session)
                pool.wait_completion()
            else:
                for key in url_map:
                    result = self.get_response(url_map[key], type, session=session)
                    if result:
                        res = {}
                        res[key] = result
                        self.results.append(res)
                    else:
                        continue
        return self.results


    def get_results_map_with_all_pages(self, api_client, url, key, type, session=None):
        url = BASE_API_URL + url
        type = type + f' key : {key}'
        result = self.get_response(url, type, session=session)
        if result:
            res = {}
            res[key] = result
            self.results.append(res)


    def get_results_map_by_threads(self, api_client, url_map, type, session=None):
        self.results = []
        if url_map is not None and len(url_map) > 0:
            if DISABLE_API_THREADS == 'false':
                pool = ThreadPool(int(NO_OF_API_THREADS))
                for key in url_map:
                    pool.add_task(self.get_results_map_with_all_pages, api_client, url_map[key], key, type, session=session)
                pool.wait_completion()
            else:
                for key in url_map:
                    url = BASE_API_URL + url_map[key]
                    result = self.get_response(url, type, session=session)
                    if result:
                        res = {}
                        res[key] = result
                        self.results.append(res)
                    else:
                        continue
        return self.results