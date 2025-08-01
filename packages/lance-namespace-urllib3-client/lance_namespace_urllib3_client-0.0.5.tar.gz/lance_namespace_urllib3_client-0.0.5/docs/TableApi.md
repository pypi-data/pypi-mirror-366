# lance_namespace_urllib3_client.TableApi

All URIs are relative to *http://localhost:2333*

Method | HTTP request | Description
------------- | ------------- | -------------
[**count_table_rows**](TableApi.md#count_table_rows) | **POST** /v1/table/{id}/count_rows | Count rows in a table
[**create_table**](TableApi.md#create_table) | **POST** /v1/table/{id}/create | Create a table with the given name
[**create_table_index**](TableApi.md#create_table_index) | **POST** /v1/table/{id}/create_index | Create an index on a table
[**delete_from_table**](TableApi.md#delete_from_table) | **POST** /v1/table/{id}/delete | Delete rows from a table
[**deregister_table**](TableApi.md#deregister_table) | **POST** /v1/table/{id}/deregister | Deregister a table
[**describe_table**](TableApi.md#describe_table) | **POST** /v1/table/{id}/describe | Describe information of a table
[**describe_table_index_stats**](TableApi.md#describe_table_index_stats) | **POST** /v1/table/{id}/index/{index_name}/stats | Get table index statistics
[**drop_table**](TableApi.md#drop_table) | **POST** /v1/table/{id}/drop | Drop a table
[**insert_into_table**](TableApi.md#insert_into_table) | **POST** /v1/table/{id}/insert | Insert records into a table
[**list_table_indices**](TableApi.md#list_table_indices) | **POST** /v1/table/{id}/index/list | List indexes on a table
[**list_tables**](TableApi.md#list_tables) | **GET** /v1/namespace/{id}/table/list | List tables in a namespace
[**merge_insert_into_table**](TableApi.md#merge_insert_into_table) | **POST** /v1/table/{id}/merge_insert | Merge insert (upsert) records into a table
[**query_table**](TableApi.md#query_table) | **POST** /v1/table/{id}/query | Query a table
[**register_table**](TableApi.md#register_table) | **POST** /v1/table/{id}/register | Register a table to a namespace
[**table_exists**](TableApi.md#table_exists) | **POST** /v1/table/{id}/exists | Check if a table exists
[**update_table**](TableApi.md#update_table) | **POST** /v1/table/{id}/update | Update rows in a table


# **count_table_rows**
> int count_table_rows(id, count_table_rows_request, delimiter=delimiter)

Count rows in a table

Count the number of rows in table `id`


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.count_table_rows_request import CountTableRowsRequest
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    count_table_rows_request = lance_namespace_urllib3_client.CountTableRowsRequest() # CountTableRowsRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Count rows in a table
        api_response = api_instance.count_table_rows(id, count_table_rows_request, delimiter=delimiter)
        print("The response of TableApi->count_table_rows:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->count_table_rows: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **count_table_rows_request** | [**CountTableRowsRequest**](CountTableRowsRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

**int**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Result of counting rows in a table |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_table**
> CreateTableResponse create_table(id, body, delimiter=delimiter, x_lance_table_location=x_lance_table_location, x_lance_table_properties=x_lance_table_properties)

Create a table with the given name

Create table `id` in the namespace with the given data in Arrow IPC stream.

The schema of the Arrow IPC stream is used as the table schema.    
If the stream is empty, the API creates a new empty table.

REST NAMESPACE ONLY
REST namespace uses Arrow IPC stream as the request body.
It passes in the `CreateTableRequest` information in the following way:
- `id`: pass through path parameter of the same name
- `location`: pass through header `x-lance-table-location`
- `properties`: pass through header `x-lance-table-properties`


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.create_table_response import CreateTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    body = None # bytearray | Arrow IPC data
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)
    x_lance_table_location = 'x_lance_table_location_example' # str | URI pointing to root location to create the table at (optional)
    x_lance_table_properties = 'x_lance_table_properties_example' # str | JSON-encoded string map (e.g. { \"owner\": \"jack\" })  (optional)

    try:
        # Create a table with the given name
        api_response = api_instance.create_table(id, body, delimiter=delimiter, x_lance_table_location=x_lance_table_location, x_lance_table_properties=x_lance_table_properties)
        print("The response of TableApi->create_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->create_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **body** | **bytearray**| Arrow IPC data | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 
 **x_lance_table_location** | **str**| URI pointing to root location to create the table at | [optional] 
 **x_lance_table_properties** | **str**| JSON-encoded string map (e.g. { \&quot;owner\&quot;: \&quot;jack\&quot; })  | [optional] 

### Return type

[**CreateTableResponse**](CreateTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/vnd.apache.arrow.stream
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Table properties result when creating a table |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_table_index**
> CreateTableIndexResponse create_table_index(id, create_table_index_request, delimiter=delimiter)

Create an index on a table

Create an index on a table column for faster search operations.
Supports vector indexes (IVF_FLAT, IVF_HNSW_SQ, IVF_PQ, etc.) and scalar indexes (BTREE, BITMAP, FTS, etc.).
Index creation is handled asynchronously. 
Use the `ListTableIndices` and `DescribeTableIndexStats` operations to monitor index creation progress.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.create_table_index_request import CreateTableIndexRequest
from lance_namespace_urllib3_client.models.create_table_index_response import CreateTableIndexResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    create_table_index_request = lance_namespace_urllib3_client.CreateTableIndexRequest() # CreateTableIndexRequest | Index creation request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Create an index on a table
        api_response = api_instance.create_table_index(id, create_table_index_request, delimiter=delimiter)
        print("The response of TableApi->create_table_index:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->create_table_index: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **create_table_index_request** | [**CreateTableIndexRequest**](CreateTableIndexRequest.md)| Index creation request | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**CreateTableIndexResponse**](CreateTableIndexResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Index created successfully |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_from_table**
> DeleteFromTableResponse delete_from_table(id, delete_from_table_request, delimiter=delimiter)

Delete rows from a table

Delete rows from table `id`.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.delete_from_table_request import DeleteFromTableRequest
from lance_namespace_urllib3_client.models.delete_from_table_response import DeleteFromTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    delete_from_table_request = lance_namespace_urllib3_client.DeleteFromTableRequest() # DeleteFromTableRequest | Delete request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Delete rows from a table
        api_response = api_instance.delete_from_table(id, delete_from_table_request, delimiter=delimiter)
        print("The response of TableApi->delete_from_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->delete_from_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **delete_from_table_request** | [**DeleteFromTableRequest**](DeleteFromTableRequest.md)| Delete request | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DeleteFromTableResponse**](DeleteFromTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Delete successful |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deregister_table**
> DeregisterTableResponse deregister_table(id, deregister_table_request, delimiter=delimiter)

Deregister a table

Deregister table `id` from its namespace.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.deregister_table_request import DeregisterTableRequest
from lance_namespace_urllib3_client.models.deregister_table_response import DeregisterTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    deregister_table_request = lance_namespace_urllib3_client.DeregisterTableRequest() # DeregisterTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Deregister a table
        api_response = api_instance.deregister_table(id, deregister_table_request, delimiter=delimiter)
        print("The response of TableApi->deregister_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->deregister_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **deregister_table_request** | [**DeregisterTableRequest**](DeregisterTableRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DeregisterTableResponse**](DeregisterTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response of DeregisterTable |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **describe_table**
> DescribeTableResponse describe_table(id, describe_table_request, delimiter=delimiter)

Describe information of a table

Describe the detailed information for table `id`.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.describe_table_request import DescribeTableRequest
from lance_namespace_urllib3_client.models.describe_table_response import DescribeTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    describe_table_request = lance_namespace_urllib3_client.DescribeTableRequest() # DescribeTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Describe information of a table
        api_response = api_instance.describe_table(id, describe_table_request, delimiter=delimiter)
        print("The response of TableApi->describe_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->describe_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **describe_table_request** | [**DescribeTableRequest**](DescribeTableRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DescribeTableResponse**](DescribeTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Table properties result when loading a table |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **describe_table_index_stats**
> DescribeTableIndexStatsResponse describe_table_index_stats(id, index_name, describe_table_index_stats_request, delimiter=delimiter)

Get table index statistics

Get statistics for a specific index on a table. Returns information about
the index type, distance type (for vector indices), and row counts.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.describe_table_index_stats_request import DescribeTableIndexStatsRequest
from lance_namespace_urllib3_client.models.describe_table_index_stats_response import DescribeTableIndexStatsResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    index_name = 'index_name_example' # str | Name of the index to get stats for
    describe_table_index_stats_request = lance_namespace_urllib3_client.DescribeTableIndexStatsRequest() # DescribeTableIndexStatsRequest | Index stats request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Get table index statistics
        api_response = api_instance.describe_table_index_stats(id, index_name, describe_table_index_stats_request, delimiter=delimiter)
        print("The response of TableApi->describe_table_index_stats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->describe_table_index_stats: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **index_name** | **str**| Name of the index to get stats for | 
 **describe_table_index_stats_request** | [**DescribeTableIndexStatsRequest**](DescribeTableIndexStatsRequest.md)| Index stats request | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DescribeTableIndexStatsResponse**](DescribeTableIndexStatsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Index statistics |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **drop_table**
> DropTableResponse drop_table(id, drop_table_request, delimiter=delimiter)

Drop a table

Drop table `id` and delete its data.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.drop_table_request import DropTableRequest
from lance_namespace_urllib3_client.models.drop_table_response import DropTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    drop_table_request = lance_namespace_urllib3_client.DropTableRequest() # DropTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Drop a table
        api_response = api_instance.drop_table(id, drop_table_request, delimiter=delimiter)
        print("The response of TableApi->drop_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->drop_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **drop_table_request** | [**DropTableRequest**](DropTableRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DropTableResponse**](DropTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response of DropTable |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **insert_into_table**
> InsertIntoTableResponse insert_into_table(id, body, delimiter=delimiter, mode=mode)

Insert records into a table

Insert new records into table `id`.

REST NAMESPACE ONLY
REST namespace uses Arrow IPC stream as the request body.
It passes in the `InsertIntoTableRequest` information in the following way:
- `id`: pass through path parameter of the same name
- `mode`: pass through query parameter of the same name


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.insert_into_table_response import InsertIntoTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    body = None # bytearray | Arrow IPC stream containing the records to insert
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)
    mode = append # str | How the insert should behave: - append (default): insert data to the existing table - overwrite: remove all data in the table and then insert data to it  (optional) (default to append)

    try:
        # Insert records into a table
        api_response = api_instance.insert_into_table(id, body, delimiter=delimiter, mode=mode)
        print("The response of TableApi->insert_into_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->insert_into_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **body** | **bytearray**| Arrow IPC stream containing the records to insert | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 
 **mode** | **str**| How the insert should behave: - append (default): insert data to the existing table - overwrite: remove all data in the table and then insert data to it  | [optional] [default to append]

### Return type

[**InsertIntoTableResponse**](InsertIntoTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/vnd.apache.arrow.stream
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Result of inserting records into a table |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_table_indices**
> ListTableIndicesResponse list_table_indices(id, list_table_indices_request, delimiter=delimiter)

List indexes on a table

List all indices created on a table. Returns information about each index
including name, columns, status, and UUID.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.list_table_indices_request import ListTableIndicesRequest
from lance_namespace_urllib3_client.models.list_table_indices_response import ListTableIndicesResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    list_table_indices_request = lance_namespace_urllib3_client.ListTableIndicesRequest() # ListTableIndicesRequest | Index list request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # List indexes on a table
        api_response = api_instance.list_table_indices(id, list_table_indices_request, delimiter=delimiter)
        print("The response of TableApi->list_table_indices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->list_table_indices: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **list_table_indices_request** | [**ListTableIndicesRequest**](ListTableIndicesRequest.md)| Index list request | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**ListTableIndicesResponse**](ListTableIndicesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of indices on the table |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_tables**
> ListTablesResponse list_tables(id, delimiter=delimiter, page_token=page_token, limit=limit)

List tables in a namespace

List all child table names of the parent namespace `id`.

REST NAMESPACE ONLY
REST namespace uses GET to perform this operation without a request body.
It passes in the `ListTablesRequest` information in the following way:
- `id`: pass through path parameter of the same name
- `page_token`: pass through query parameter of the same name
- `limit`: pass through query parameter of the same name


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.list_tables_response import ListTablesResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)
    page_token = 'page_token_example' # str |  (optional)
    limit = 56 # int |  (optional)

    try:
        # List tables in a namespace
        api_response = api_instance.list_tables(id, delimiter=delimiter, page_token=page_token, limit=limit)
        print("The response of TableApi->list_tables:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->list_tables: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 
 **page_token** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] 

### Return type

[**ListTablesResponse**](ListTablesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of tables |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**406** | Not Acceptable / Unsupported Operation. The server does not support this operation. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **merge_insert_into_table**
> MergeInsertIntoTableResponse merge_insert_into_table(id, on, body, delimiter=delimiter, when_matched_update_all=when_matched_update_all, when_matched_update_all_filt=when_matched_update_all_filt, when_not_matched_insert_all=when_not_matched_insert_all, when_not_matched_by_source_delete=when_not_matched_by_source_delete, when_not_matched_by_source_delete_filt=when_not_matched_by_source_delete_filt)

Merge insert (upsert) records into a table

Performs a merge insert (upsert) operation on table `id`.
This operation updates existing rows
based on a matching column and inserts new rows that don't match.
It returns the number of rows inserted and updated.

REST NAMESPACE ONLY
REST namespace uses Arrow IPC stream as the request body.
It passes in the `MergeInsertIntoTableRequest` information in the following way:
- `id`: pass through path parameter of the same name
- `on`: pass through query parameter of the same name
- `when_matched_update_all`: pass through query parameter of the same name
- `when_matched_update_all_filt`: pass through query parameter of the same name
- `when_not_matched_insert_all`: pass through query parameter of the same name
- `when_not_matched_by_source_delete`: pass through query parameter of the same name
- `when_not_matched_by_source_delete_filt`: pass through query parameter of the same name


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.merge_insert_into_table_response import MergeInsertIntoTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    on = 'on_example' # str | Column name to use for matching rows (required)
    body = None # bytearray | Arrow IPC stream containing the records to merge
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)
    when_matched_update_all = False # bool | Update all columns when rows match (optional) (default to False)
    when_matched_update_all_filt = 'when_matched_update_all_filt_example' # str | The row is updated (similar to UpdateAll) only for rows where the SQL expression evaluates to true (optional)
    when_not_matched_insert_all = False # bool | Insert all columns when rows don't match (optional) (default to False)
    when_not_matched_by_source_delete = False # bool | Delete all rows from target table that don't match a row in the source table (optional) (default to False)
    when_not_matched_by_source_delete_filt = 'when_not_matched_by_source_delete_filt_example' # str | Delete rows from the target table if there is no match AND the SQL expression evaluates to true (optional)

    try:
        # Merge insert (upsert) records into a table
        api_response = api_instance.merge_insert_into_table(id, on, body, delimiter=delimiter, when_matched_update_all=when_matched_update_all, when_matched_update_all_filt=when_matched_update_all_filt, when_not_matched_insert_all=when_not_matched_insert_all, when_not_matched_by_source_delete=when_not_matched_by_source_delete, when_not_matched_by_source_delete_filt=when_not_matched_by_source_delete_filt)
        print("The response of TableApi->merge_insert_into_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->merge_insert_into_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **on** | **str**| Column name to use for matching rows (required) | 
 **body** | **bytearray**| Arrow IPC stream containing the records to merge | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 
 **when_matched_update_all** | **bool**| Update all columns when rows match | [optional] [default to False]
 **when_matched_update_all_filt** | **str**| The row is updated (similar to UpdateAll) only for rows where the SQL expression evaluates to true | [optional] 
 **when_not_matched_insert_all** | **bool**| Insert all columns when rows don&#39;t match | [optional] [default to False]
 **when_not_matched_by_source_delete** | **bool**| Delete all rows from target table that don&#39;t match a row in the source table | [optional] [default to False]
 **when_not_matched_by_source_delete_filt** | **str**| Delete rows from the target table if there is no match AND the SQL expression evaluates to true | [optional] 

### Return type

[**MergeInsertIntoTableResponse**](MergeInsertIntoTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/vnd.apache.arrow.stream
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Result of merge insert operation |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_table**
> bytearray query_table(id, query_table_request, delimiter=delimiter)

Query a table

Query table `id` with vector search, full text search and optional SQL filtering.
Returns results in Arrow IPC file or stream format.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.query_table_request import QueryTableRequest
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    query_table_request = lance_namespace_urllib3_client.QueryTableRequest() # QueryTableRequest | Query request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Query a table
        api_response = api_instance.query_table(id, query_table_request, delimiter=delimiter)
        print("The response of TableApi->query_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->query_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **query_table_request** | [**QueryTableRequest**](QueryTableRequest.md)| Query request | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

**bytearray**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/vnd.apache.arrow.file, application/vnd.apache.arrow.stream, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query results in Arrow IPC file or stream format |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **register_table**
> RegisterTableResponse register_table(id, register_table_request, delimiter=delimiter)

Register a table to a namespace

Register an existing table at a given storage location as `id`.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.register_table_request import RegisterTableRequest
from lance_namespace_urllib3_client.models.register_table_response import RegisterTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    register_table_request = lance_namespace_urllib3_client.RegisterTableRequest() # RegisterTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Register a table to a namespace
        api_response = api_instance.register_table(id, register_table_request, delimiter=delimiter)
        print("The response of TableApi->register_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->register_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **register_table_request** | [**RegisterTableRequest**](RegisterTableRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**RegisterTableResponse**](RegisterTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Table properties result when registering a table |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**406** | Not Acceptable / Unsupported Operation. The server does not support this operation. |  -  |
**409** | The request conflicts with the current state of the target resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **table_exists**
> table_exists(id, table_exists_request, delimiter=delimiter)

Check if a table exists

Check if table `id` exists.

This operation should behave exactly like DescribeTable, 
except it does not contain a response body.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.table_exists_request import TableExistsRequest
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    table_exists_request = lance_namespace_urllib3_client.TableExistsRequest() # TableExistsRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Check if a table exists
        api_instance.table_exists(id, table_exists_request, delimiter=delimiter)
    except Exception as e:
        print("Exception when calling TableApi->table_exists: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **table_exists_request** | [**TableExistsRequest**](TableExistsRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success, no content |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_table**
> UpdateTableResponse update_table(id, update_table_request, delimiter=delimiter)

Update rows in a table

Update existing rows in table `id`.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.update_table_request import UpdateTableRequest
from lance_namespace_urllib3_client.models.update_table_response import UpdateTableResponse
from lance_namespace_urllib3_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:2333
# See configuration.py for a list of all supported configuration parameters.
configuration = lance_namespace_urllib3_client.Configuration(
    host = "http://localhost:2333"
)


# Enter a context with an instance of the API client
with lance_namespace_urllib3_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = lance_namespace_urllib3_client.TableApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    update_table_request = lance_namespace_urllib3_client.UpdateTableRequest() # UpdateTableRequest | Update request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Update rows in a table
        api_response = api_instance.update_table(id, update_table_request, delimiter=delimiter)
        print("The response of TableApi->update_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TableApi->update_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **update_table_request** | [**UpdateTableRequest**](UpdateTableRequest.md)| Update request | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**UpdateTableResponse**](UpdateTableResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Update successful |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

