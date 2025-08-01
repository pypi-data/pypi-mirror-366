# lance_namespace_urllib3_client.MetadataApi

All URIs are relative to *http://localhost:2333*

Method | HTTP request | Description
------------- | ------------- | -------------
[**alter_transaction**](MetadataApi.md#alter_transaction) | **POST** /v1/transaction/{id}/alter | Alter information of a transaction.
[**create_namespace**](MetadataApi.md#create_namespace) | **POST** /v1/namespace/{id}/create | Create a new namespace
[**create_table_index**](MetadataApi.md#create_table_index) | **POST** /v1/table/{id}/create_index | Create an index on a table
[**deregister_table**](MetadataApi.md#deregister_table) | **POST** /v1/table/{id}/deregister | Deregister a table
[**describe_namespace**](MetadataApi.md#describe_namespace) | **POST** /v1/namespace/{id}/describe | Describe a namespace
[**describe_table**](MetadataApi.md#describe_table) | **POST** /v1/table/{id}/describe | Describe information of a table
[**describe_table_index_stats**](MetadataApi.md#describe_table_index_stats) | **POST** /v1/table/{id}/index/{index_name}/stats | Get table index statistics
[**describe_transaction**](MetadataApi.md#describe_transaction) | **POST** /v1/transaction/{id}/describe | Describe information about a transaction
[**drop_namespace**](MetadataApi.md#drop_namespace) | **POST** /v1/namespace/{id}/drop | Drop a namespace
[**drop_table**](MetadataApi.md#drop_table) | **POST** /v1/table/{id}/drop | Drop a table
[**list_namespaces**](MetadataApi.md#list_namespaces) | **GET** /v1/namespace/{id}/list | List namespaces
[**list_table_indices**](MetadataApi.md#list_table_indices) | **POST** /v1/table/{id}/index/list | List indexes on a table
[**list_tables**](MetadataApi.md#list_tables) | **GET** /v1/namespace/{id}/table/list | List tables in a namespace
[**namespace_exists**](MetadataApi.md#namespace_exists) | **POST** /v1/namespace/{id}/exists | Check if a namespace exists
[**register_table**](MetadataApi.md#register_table) | **POST** /v1/table/{id}/register | Register a table to a namespace
[**table_exists**](MetadataApi.md#table_exists) | **POST** /v1/table/{id}/exists | Check if a table exists


# **alter_transaction**
> AlterTransactionResponse alter_transaction(id, alter_transaction_request, delimiter=delimiter)

Alter information of a transaction.

Alter a transaction with a list of actions such as setting status or properties.
The server should either succeed and apply all actions, or fail and apply no action.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.alter_transaction_request import AlterTransactionRequest
from lance_namespace_urllib3_client.models.alter_transaction_response import AlterTransactionResponse
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    alter_transaction_request = lance_namespace_urllib3_client.AlterTransactionRequest() # AlterTransactionRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Alter information of a transaction.
        api_response = api_instance.alter_transaction(id, alter_transaction_request, delimiter=delimiter)
        print("The response of MetadataApi->alter_transaction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->alter_transaction: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **alter_transaction_request** | [**AlterTransactionRequest**](AlterTransactionRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**AlterTransactionResponse**](AlterTransactionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response of AlterTransaction |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**409** | The request conflicts with the current state of the target resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_namespace**
> CreateNamespaceResponse create_namespace(id, create_namespace_request, delimiter=delimiter)

Create a new namespace

Create new namespace `id`.

During the creation process, the implementation may modify user-provided `properties`, 
such as adding additional properties like `created_at` to user-provided properties, 
omitting any specific property, or performing actions based on any property value.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.create_namespace_request import CreateNamespaceRequest
from lance_namespace_urllib3_client.models.create_namespace_response import CreateNamespaceResponse
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    create_namespace_request = lance_namespace_urllib3_client.CreateNamespaceRequest() # CreateNamespaceRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Create a new namespace
        api_response = api_instance.create_namespace(id, create_namespace_request, delimiter=delimiter)
        print("The response of MetadataApi->create_namespace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->create_namespace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **create_namespace_request** | [**CreateNamespaceRequest**](CreateNamespaceRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**CreateNamespaceResponse**](CreateNamespaceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Result of creating a namespace |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**406** | Not Acceptable / Unsupported Operation. The server does not support this operation. |  -  |
**409** | The request conflicts with the current state of the target resource. |  -  |
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    create_table_index_request = lance_namespace_urllib3_client.CreateTableIndexRequest() # CreateTableIndexRequest | Index creation request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Create an index on a table
        api_response = api_instance.create_table_index(id, create_table_index_request, delimiter=delimiter)
        print("The response of MetadataApi->create_table_index:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->create_table_index: %s\n" % e)
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    deregister_table_request = lance_namespace_urllib3_client.DeregisterTableRequest() # DeregisterTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Deregister a table
        api_response = api_instance.deregister_table(id, deregister_table_request, delimiter=delimiter)
        print("The response of MetadataApi->deregister_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->deregister_table: %s\n" % e)
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

# **describe_namespace**
> DescribeNamespaceResponse describe_namespace(id, describe_namespace_request, delimiter=delimiter)

Describe a namespace

Describe the detailed information for namespace `id`.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.describe_namespace_request import DescribeNamespaceRequest
from lance_namespace_urllib3_client.models.describe_namespace_response import DescribeNamespaceResponse
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    describe_namespace_request = lance_namespace_urllib3_client.DescribeNamespaceRequest() # DescribeNamespaceRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Describe a namespace
        api_response = api_instance.describe_namespace(id, describe_namespace_request, delimiter=delimiter)
        print("The response of MetadataApi->describe_namespace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->describe_namespace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **describe_namespace_request** | [**DescribeNamespaceRequest**](DescribeNamespaceRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DescribeNamespaceResponse**](DescribeNamespaceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns a namespace, as well as any properties stored on the namespace if namespace properties are supported by the server. |  -  |
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    describe_table_request = lance_namespace_urllib3_client.DescribeTableRequest() # DescribeTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Describe information of a table
        api_response = api_instance.describe_table(id, describe_table_request, delimiter=delimiter)
        print("The response of MetadataApi->describe_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->describe_table: %s\n" % e)
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    index_name = 'index_name_example' # str | Name of the index to get stats for
    describe_table_index_stats_request = lance_namespace_urllib3_client.DescribeTableIndexStatsRequest() # DescribeTableIndexStatsRequest | Index stats request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Get table index statistics
        api_response = api_instance.describe_table_index_stats(id, index_name, describe_table_index_stats_request, delimiter=delimiter)
        print("The response of MetadataApi->describe_table_index_stats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->describe_table_index_stats: %s\n" % e)
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

# **describe_transaction**
> DescribeTransactionResponse describe_transaction(id, describe_transaction_request, delimiter=delimiter)

Describe information about a transaction

Return a detailed information for a given transaction


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.describe_transaction_request import DescribeTransactionRequest
from lance_namespace_urllib3_client.models.describe_transaction_response import DescribeTransactionResponse
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    describe_transaction_request = lance_namespace_urllib3_client.DescribeTransactionRequest() # DescribeTransactionRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Describe information about a transaction
        api_response = api_instance.describe_transaction(id, describe_transaction_request, delimiter=delimiter)
        print("The response of MetadataApi->describe_transaction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->describe_transaction: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **describe_transaction_request** | [**DescribeTransactionRequest**](DescribeTransactionRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DescribeTransactionResponse**](DescribeTransactionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response of GetTransaction |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**503** | The service is not ready to handle the request. The client should wait and retry. The service may additionally send a Retry-After header to indicate when to retry. |  -  |
**5XX** | A server-side problem that might not be addressable from the client side. Used for server 5xx errors without more specific documentation in individual routes. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **drop_namespace**
> DropNamespaceResponse drop_namespace(id, drop_namespace_request, delimiter=delimiter)

Drop a namespace

Drop namespace `id` from its parent namespace.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.drop_namespace_request import DropNamespaceRequest
from lance_namespace_urllib3_client.models.drop_namespace_response import DropNamespaceResponse
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    drop_namespace_request = lance_namespace_urllib3_client.DropNamespaceRequest() # DropNamespaceRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Drop a namespace
        api_response = api_instance.drop_namespace(id, drop_namespace_request, delimiter=delimiter)
        print("The response of MetadataApi->drop_namespace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->drop_namespace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **drop_namespace_request** | [**DropNamespaceRequest**](DropNamespaceRequest.md)|  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 

### Return type

[**DropNamespaceResponse**](DropNamespaceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Result of dropping a namespace |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**409** | The request conflicts with the current state of the target resource. |  -  |
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    drop_table_request = lance_namespace_urllib3_client.DropTableRequest() # DropTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Drop a table
        api_response = api_instance.drop_table(id, drop_table_request, delimiter=delimiter)
        print("The response of MetadataApi->drop_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->drop_table: %s\n" % e)
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

# **list_namespaces**
> ListNamespacesResponse list_namespaces(id, delimiter=delimiter, page_token=page_token, limit=limit)

List namespaces

List all child namespace names of the parent namespace `id`.

REST NAMESPACE ONLY
REST namespace uses GET to perform this operation without a request body.
It passes in the `ListNamespacesRequest` information in the following way:
- `id`: pass through path parameter of the same name
- `page_token`: pass through query parameter of the same name
- `limit`: pass through query parameter of the same name


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.list_namespaces_response import ListNamespacesResponse
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)
    page_token = 'page_token_example' # str |  (optional)
    limit = 56 # int |  (optional)

    try:
        # List namespaces
        api_response = api_instance.list_namespaces(id, delimiter=delimiter, page_token=page_token, limit=limit)
        print("The response of MetadataApi->list_namespaces:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->list_namespaces: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **delimiter** | **str**| An optional delimiter of the &#x60;string identifier&#x60;, following the Lance Namespace spec. When not specified, the &#x60;.&#x60; delimiter must be used.  | [optional] 
 **page_token** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] 

### Return type

[**ListNamespacesResponse**](ListNamespacesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of namespaces |  -  |
**400** | Indicates a bad request error. It could be caused by an unexpected request body format or other forms of request validation failure, such as invalid json. Usually serves application/json content, although in some cases simple text/plain content might be returned by the server&#39;s middleware. |  -  |
**401** | Unauthorized. The request lacks valid authentication credentials for the operation. |  -  |
**403** | Forbidden. Authenticated user does not have the necessary permissions. |  -  |
**404** | A server-side problem that means can not find the specified resource. |  -  |
**406** | Not Acceptable / Unsupported Operation. The server does not support this operation. |  -  |
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    list_table_indices_request = lance_namespace_urllib3_client.ListTableIndicesRequest() # ListTableIndicesRequest | Index list request
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # List indexes on a table
        api_response = api_instance.list_table_indices(id, list_table_indices_request, delimiter=delimiter)
        print("The response of MetadataApi->list_table_indices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->list_table_indices: %s\n" % e)
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)
    page_token = 'page_token_example' # str |  (optional)
    limit = 56 # int |  (optional)

    try:
        # List tables in a namespace
        api_response = api_instance.list_tables(id, delimiter=delimiter, page_token=page_token, limit=limit)
        print("The response of MetadataApi->list_tables:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->list_tables: %s\n" % e)
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

# **namespace_exists**
> namespace_exists(id, namespace_exists_request, delimiter=delimiter)

Check if a namespace exists

Check if namespace `id` exists.

This operation must behave exactly like the DescribeNamespace API, 
except it does not contain a response body.


### Example


```python
import lance_namespace_urllib3_client
from lance_namespace_urllib3_client.models.namespace_exists_request import NamespaceExistsRequest
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    namespace_exists_request = lance_namespace_urllib3_client.NamespaceExistsRequest() # NamespaceExistsRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Check if a namespace exists
        api_instance.namespace_exists(id, namespace_exists_request, delimiter=delimiter)
    except Exception as e:
        print("Exception when calling MetadataApi->namespace_exists: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| &#x60;string identifier&#x60; of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, &#x60;v1/namespace/./list&#x60; performs a &#x60;ListNamespace&#x60; on the root namespace.  | 
 **namespace_exists_request** | [**NamespaceExistsRequest**](NamespaceExistsRequest.md)|  | 
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    register_table_request = lance_namespace_urllib3_client.RegisterTableRequest() # RegisterTableRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Register a table to a namespace
        api_response = api_instance.register_table(id, register_table_request, delimiter=delimiter)
        print("The response of MetadataApi->register_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->register_table: %s\n" % e)
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
    api_instance = lance_namespace_urllib3_client.MetadataApi(api_client)
    id = 'id_example' # str | `string identifier` of an object in a namespace, following the Lance Namespace spec. When the value is equal to the delimiter, it represents the root namespace. For example, `v1/namespace/./list` performs a `ListNamespace` on the root namespace. 
    table_exists_request = lance_namespace_urllib3_client.TableExistsRequest() # TableExistsRequest | 
    delimiter = 'delimiter_example' # str | An optional delimiter of the `string identifier`, following the Lance Namespace spec. When not specified, the `.` delimiter must be used.  (optional)

    try:
        # Check if a table exists
        api_instance.table_exists(id, table_exists_request, delimiter=delimiter)
    except Exception as e:
        print("Exception when calling MetadataApi->table_exists: %s\n" % e)
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

