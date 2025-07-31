"""Classes for communicating with the MapLarge Rest API. See RestClient."""
from   collections     import deque
from   datetime        import datetime, timedelta
from   enum            import auto, Enum
from   hashlib         import md5
from   inspect         import isclass
from   io              import BytesIO, StringIO
import json
import re
import socket
from   time            import sleep
from   typing          import Any, Callable, cast, Deque, Dict, IO, Iterable, List, Literal, Mapping, Optional, overload, Tuple, Type, TypedDict, TypeVar, Union
from   urllib.error    import HTTPError
from   urllib.parse    import parse_qs, quote, urlparse
from   urllib.request  import build_opener, HTTPDefaultErrorHandler, HTTPRedirectHandler, Request, urlopen
from   urllib.response import addinfourl
import uuid

from   dateutil.parser import isoparse

import maplargerest.models
#from   maplargerest.models import Page, RestList
from   maplargerest.models import * # pylint: disable=unused-wildcard-import,wildcard-import
class AccountsEndpoints:
	"""
	Accounts are the top-level organizational structure in the MapLarge API.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Account]:
		"""
		Get the list of existing accounts.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Account]
		"""

		return cast(RestList[Account], self.client._send_request(
			path='/accounts',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Account",
			timeout=timeout
		))
	def post(self, *,
		body: CreateAccountRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Account:
		"""
		Create a new account.

		:param body:
		:type body: CreateAccountRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Account
		"""

		return cast(Account, self.client._send_request(
			path='/accounts',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Account",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_or_code: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Account:
		"""
		Get a specific account.

		:param id_or_code: Account id or code
		:type id_or_code: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Account
		"""

		return cast(Account, self.client._send_request(
			path='/accounts/{idOrCode}',
			method=HttpMethod.GET,
			parameters={
				'idOrCode': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'idOrCode': id_or_code,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Account",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_or_code: str,
		body: UpdateAccountRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Account:
		"""
		Update an existing account.

		:param id_or_code: Account id or code
		:type id_or_code: str
		:param body:
		:type body: UpdateAccountRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Account
		"""

		return cast(Account, self.client._send_request(
			path='/accounts/{idOrCode}',
			method=HttpMethod.PUT,
			parameters={
				'idOrCode': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'idOrCode': id_or_code,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Account",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_or_code: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing account.

		:param id_or_code: Account id or code
		:type id_or_code: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{idOrCode}',
			method=HttpMethod.DELETE,
			parameters={
				'idOrCode': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'idOrCode': id_or_code,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def post_many(self, *,
		body: List[CreateAccountRequest],
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> List[Account]:
		"""
		Create several new accounts.

		:param body:
		:type body: List[CreateAccountRequest]
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: List[Account]
		"""

		return cast(List[Account], self.client._send_request(
			path='/accounts/many',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="list",
			item_type="Account",
			timeout=timeout
		))
class FoldersEndpoints:
	"""
	Resources are used to manage fine-grained access control to various items (currently just tables, but perhaps other things in the future).
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		account: str,
		id_or_path: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		recurse_depth: Optional[int] = None,
		timeout: Optional[float] = None
	) -> ResourceFolder:
		"""
		Get a specific resource folder.

		:param account: Account id or code
		:type account: str
		:param id_or_path: Id or Path of the folder. If path, make sure to URI escape the value (replace forward slash with %2F).
		:type id_or_path: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param recurse_depth: How many levels of folder contents to fetch. Defaults to 1 (i.e. only this folder's contents will be populated). -1 means infinite.
		:type recurse_depth: int or None
		:rtype: ResourceFolder
		"""

		return cast(ResourceFolder, self.client._send_request(
			path='/accounts/{account}/folders',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrPath': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'recurseDepth': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'idOrPath': id_or_path,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'recurseDepth': recurse_depth,
			},
			result_type="ResourceFolder",
			item_type=None,
			timeout=timeout
		))
	def post(self, *,
		account: str,
		body: UpdateResourceFolderRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> ResourceFolder:
		"""
		Create a new folder.

		:param account: Account id or code
		:type account: str
		:param body:
		:type body: UpdateResourceFolderRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: ResourceFolder
		"""

		return cast(ResourceFolder, self.client._send_request(
			path='/accounts/{account}/folders',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="ResourceFolder",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		account: str,
		id_or_path: str,
		body: UpdateResourceFolderRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> ResourceFolder:
		"""
		Update an existing folder.

		:param account: Account id or code
		:type account: str
		:param id_or_path: Id or Path of the folder. If path, make sure to URI escape the value (replace forward slash with %2F).
		:type id_or_path: str
		:param body:
		:type body: UpdateResourceFolderRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: ResourceFolder
		"""

		return cast(ResourceFolder, self.client._send_request(
			path='/accounts/{account}/folders',
			method=HttpMethod.PUT,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrPath': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'idOrPath': id_or_path,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="ResourceFolder",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		id_or_path: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		cascade: Optional[ResourceDeleteCascade] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing folder.

		:param account: Account id or code
		:type account: str
		:param id_or_path: Id or Path of the folder. If path, make sure to URI escape the value (replace forward slash with %2F).
		:type id_or_path: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param cascade: Specify what should be done with folder contents when the folder is deleted. Defaults to `Delete`.
* `Delete` - Delete folder contents
* `Move` - Move folder contents up to the root folder
		:type cascade: ResourceDeleteCascade or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/folders',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrPath': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'cascade': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'idOrPath': id_or_path,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'cascade': cascade,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def contents(self, *,
		account: str,
		id_or_path: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		recurse_depth: Optional[int] = None,
		timeout: Optional[float] = None
	) -> RestList[ResourceBase]:
		"""
		Get contents of a specific resource folder.

		:param account: Account id or code
		:type account: str
		:param id_or_path: Id or Path of the folder. If path, make sure to URI escape the value (replace forward slash with %2F).
		:type id_or_path: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param recurse_depth: How many levels of folder contents to fetch. Defaults to 1 (i.e. only this folder's contents will be populated). -1 means infinite.
		:type recurse_depth: int or None
		:rtype: RestList[ResourceBase]
		"""

		return cast(RestList[ResourceBase], self.client._send_request(
			path='/accounts/{account}/folders/contents',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrPath': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'recurseDepth': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'idOrPath': id_or_path,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'recurseDepth': recurse_depth,
			},
			result_type="RestList",
			item_type="ResourceBase",
			timeout=timeout
		))
class GroupsEndpoints:
	"""
	Create and delete groups. Groups are used to manage user access to accounts.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		account: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Group]:
		"""
		Get a list of groups belonging to an account.

		:param account: Account id or code
		:type account: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Group]
		"""

		return cast(RestList[Group], self.client._send_request(
			path='/accounts/{account}/groups',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Group",
			timeout=timeout
		))
	def post(self, *,
		account: str,
		body: CreateGroupRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Group:
		"""
		Create a new group.

		:param account: Account id or code
		:type account: str
		:param body:
		:type body: CreateGroupRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Group
		"""

		return cast(Group, self.client._send_request(
			path='/accounts/{account}/groups',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Group",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		account: str,
		id_or_name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Group:
		"""
		Get a specific group.

		:param account: Account id or code
		:type account: str
		:param id_or_name: Group id or name
		:type id_or_name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Group
		"""

		return cast(Group, self.client._send_request(
			path='/accounts/{account}/groups/{idOrName}',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'idOrName': id_or_name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Group",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		account: str,
		id_or_name: str,
		body: UpdateGroupRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Group:
		"""
		Update an existing group.

		:param account: Account id or code
		:type account: str
		:param id_or_name: Group id or name
		:type id_or_name: str
		:param body:
		:type body: UpdateGroupRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Group
		"""

		return cast(Group, self.client._send_request(
			path='/accounts/{account}/groups/{idOrName}',
			method=HttpMethod.PUT,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'idOrName': id_or_name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Group",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		id_or_name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing group.

		:param account: Account id or code
		:type account: str
		:param id_or_name: Group id or name
		:type id_or_name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/groups/{idOrName}',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'idOrName': id_or_name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def post_default(self, *,
		account: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Group]:
		"""
		Create default groups.

		:param account: Account id or code
		:type account: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Group]
		"""

		return cast(RestList[Group], self.client._send_request(
			path='/accounts/{account}/groups/default',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Group",
			timeout=timeout
		))
	def post_many(self, *,
		body: List[CreateGroupWithAccountRequest],
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> List[Group]:
		"""
		Create several new groups.

		:param body:
		:type body: List[CreateGroupWithAccountRequest]
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: List[Group]
		"""

		return cast(List[Group], self.client._send_request(
			path='/groups/many',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="list",
			item_type="Group",
			timeout=timeout
		))
class IndexesEndpoints: # pylint: disable=missing-class-docstring
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list_indexed_tables(self, *,
		account: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestListBase[TableVersion]:
		"""
		Get the list of tables which have an index associated with them

		:param account: Account id or code
		:type account: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestListBase[TableVersion]
		"""

		return cast(RestListBase[TableVersion], self.client._send_request(
			path='/accounts/{account}/indexes',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestListBase",
			item_type="TableVersion",
			timeout=timeout
		))
	def list(self, *,
		account: str,
		table_name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestListBase[IndexDefinition]:
		"""
		Get the list of indexes for the specified table

		:param account: Account id or code
		:type account: str
		:param table_name: The table name. Just the name - no account code or table version.
		:type table_name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestListBase[IndexDefinition]
		"""

		return cast(RestListBase[IndexDefinition], self.client._send_request(
			path='/accounts/{account}/indexes/{tableName}',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'tableName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'tableName': table_name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestListBase",
			item_type="IndexDefinition",
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		table_name: str,
		index_name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete the specified index from the specified table

		:param account: Account id or code
		:type account: str
		:param table_name: The table name. Just the name - no account code or table version.
		:type table_name: str
		:param index_name: The name of the index to be deleted
		:type index_name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/indexes/{tableName}/{indexName}',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'tableName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'indexName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'tableName': table_name,
				'indexName': index_name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def create(self, *,
		account: str,
		table_name: str,
		index_type: str,
		index_name: str,
		body: CreateIndexRequestOptions,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[IndexDefinition]:
		"""
		Create a new index on the specified table

		:param account: Account id or code
		:type account: str
		:param table_name: The table name. Just the name - no account code or table version.
		:type table_name: str
		:param index_type: The index type to be created
		:type index_type: str
		:param index_name: The name of the index to be created
		:type index_name: str
		:param body:
		:type body: CreateIndexRequestOptions
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[IndexDefinition]
		"""

		return cast(RestList[IndexDefinition], self.client._send_request(
			path='/accounts/{account}/indexes/{tableName}/create/{indexType}/{indexName}',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'tableName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'indexType': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'indexName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'tableName': table_name,
				'indexType': index_type,
				'indexName': index_name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="IndexDefinition",
			timeout=timeout
		))
	def types(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestListBase[IndexType]:
		"""
		Get the list of available index types

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestListBase[IndexType]
		"""

		return cast(RestListBase[IndexType], self.client._send_request(
			path='/accounts/{account}/indexes/types',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestListBase",
			item_type="IndexType",
			timeout=timeout
		))
class ResourcesEndpoints:
	"""
	Resources are used to manage fine-grained access control to various items (currently just tables, but perhaps other things in the future).
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		account: str,
		id_or_urn: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Resource:
		"""
		Get a specific resource.

		:param account: Account id or code
		:type account: str
		:param id_or_urn: Id or URN of the resource. Make sure to URI escape the URN value (replace forward slash with %2F).
		:type id_or_urn: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Resource
		"""

		return cast(Resource, self.client._send_request(
			path='/accounts/{account}/resources',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrUrn': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'idOrUrn': id_or_urn,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Resource",
			item_type=None,
			timeout=timeout
		))
	def post(self, *,
		account: str,
		body: UpdateResourceRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Resource:
		"""
		Create a new resource.

		:param account: Account id or code
		:type account: str
		:param body:
		:type body: UpdateResourceRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Resource
		"""

		return cast(Resource, self.client._send_request(
			path='/accounts/{account}/resources',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Resource",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		account: str,
		id_or_urn: str,
		body: UpdateResourceRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Resource:
		"""
		Update an existing resource.

		:param account: Account id or code
		:type account: str
		:param id_or_urn: Id or URN of the resource. Make sure to URI escape the URN value (replace forward slash with %2F).
		:type id_or_urn: str
		:param body:
		:type body: UpdateResourceRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Resource
		"""

		return cast(Resource, self.client._send_request(
			path='/accounts/{account}/resources',
			method=HttpMethod.PUT,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrUrn': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'idOrUrn': id_or_urn,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Resource",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		id_or_urn: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing resource.

		:param account: Account id or code
		:type account: str
		:param id_or_urn: Id or URN of the resource. Make sure to URI escape the URN value (replace forward slash with %2F).
		:type id_or_urn: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/resources',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'idOrUrn': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'idOrUrn': id_or_urn,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class TablesEndpoints: # pylint: disable=missing-class-docstring
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.rows = TablesRowsEndpoints(self.client)
		self.versions = TablesVersionsEndpoints(self.client)
		self.tags = TablesTagsEndpoints(self.client)
	def list(self, *,
		account: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		page: Optional[PageOptions] = None,
		timeout: Optional[float] = None
	) -> RestListBase[TableVersion]:
		"""
		Get the list of tables. Returns the currently active version of each table.

		:param account: Account id or code
		:type account: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param page:
		:type page: PageOptions or None
		:rtype: RestListBase[TableVersion]
		"""

		return cast(RestListBase[TableVersion], self.client._send_request(
			path='/accounts/{account}/tables',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'page': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'page': page,
			},
			result_type="RestListBase",
			item_type="TableVersion",
			timeout=timeout
		))
	def get(self, *,
		account: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TableVersion:
		"""
		Get the currently active version of a specific table.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TableVersion
		"""

		return cast(TableVersion, self.client._send_request(
			path='/accounts/{account}/tables/{name}',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TableVersion",
			item_type=None,
			timeout=timeout
		))
	def post(self, *,
		account: str,
		name: str,
		body: CreateTableRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Import:
		"""
		Create a new table asynchronously. Poll `imports/{importGuid}` for status updates.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param body:
		:type body: CreateTableRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Import
		"""

		return cast(Import, self.client._send_request(
			path='/accounts/{account}/tables/{name}',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Import",
			item_type=None,
			timeout=timeout
		))
	def post_empty(self, *,
		account: str,
		name: str,
		body: CreateEmptyTableRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[TableVersion]:
		"""
		Create a new empty table synchronously.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param body:
		:type body: CreateEmptyTableRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[TableVersion]
		"""

		return cast(RestList[TableVersion], self.client._send_request(
			path='/accounts/{account}/tables/{name}/empty',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="TableVersion",
			timeout=timeout
		))
	def post_synchronous(self, *,
		account: str,
		name: str,
		body: CreateTableRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[TableVersion]:
		"""
		Create a new table synchronously. Use the asynchronous version instead when possible.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param body:
		:type body: CreateTableRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[TableVersion]
		"""

		return cast(RestList[TableVersion], self.client._send_request(
			path='/accounts/{account}/tables/{name}/synchronous',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="TableVersion",
			timeout=timeout
		))
	def upload(self, *,
		account: str,
		name: str,
		body: CreateTableFromFileUploadRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Import:
		"""
		Create a new table by file upload asynchronously. Poll `imports/{importGuid}` for status updates.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param body:
		:type body: CreateTableFromFileUploadRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Import
		"""

		return cast(Import, self.client._send_request(
			path='/accounts/{account}/tables/{name}/upload',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.MULTI_PART_FORM_DATA,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Import",
			item_type=None,
			timeout=timeout
		))
	def upload_stream(self, *,
		account: str,
		name: str,
		filename: str,
		visibility: TableVisibility,
		body: File,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[FileImportOptions] = None,
		timeout: Optional[float] = None
	) -> Import:
		"""
		Create a new table by file upload asynchronously. The body of the request is a single stream. Poll `imports/{importGuid}` for status updates.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param filename: The name of the originating file. Mostly used for inferring file format from the extension.
		:type filename: str
		:param visibility: The accessibility and discoverability of the table. Must be of the following three values: Public, PublicUnlisted or Private. If omitted, Private will be used.
		:type visibility: TableVisibility
		:param body:
		:type body: File
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param options: JSON (escaped) that defines file import options values. It is only necessary to specify non-default values.
		:type options: FileImportOptions or None
		:rtype: Import
		"""

		return cast(Import, self.client._send_request(
			path='/accounts/{account}/tables/{name}/uploadstream',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'filename': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'visibility': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'isJson': True },
			},
			request_body=RequestBodyType.BINARY,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'filename': filename,
				'visibility': visibility,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			},
			result_type="Import",
			item_type=None,
			timeout=timeout
		))
	def upload_synchronous(self, *,
		account: str,
		name: str,
		body: CreateTableFromFileUploadRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[TableVersion]:
		"""
		Create a new table by file upload synchronously.Use the asynchronous version instead when possible.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param body:
		:type body: CreateTableFromFileUploadRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[TableVersion]
		"""

		return cast(RestList[TableVersion], self.client._send_request(
			path='/accounts/{account}/tables/{name}/uploadsynchronous',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.MULTI_PART_FORM_DATA,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="TableVersion",
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete all versions of the specified table.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/tables/{name}/versions',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class TablesRowsEndpoints: # pylint: disable=missing-class-docstring
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def truncate(self, *,
		account: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Truncates (efficiently clears) all rows of the specified table.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/tables/{name}/rows',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class TablesVersionsEndpoints: # pylint: disable=missing-class-docstring
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		account: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		show_all: Optional[bool] = None,
		page: Optional[PageOptions] = None,
		timeout: Optional[float] = None
	) -> RestListBase[TableVersion]:
		"""
		Get the list of table versions for a specific table.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param show_all: Flag to include hidden table versions in the results. By default, all versions in the past hour, and the past 50 versions, and 1 version from each hour before that are included. All others are hidden.
		:type show_all: bool or None
		:param page:
		:type page: PageOptions or None
		:rtype: RestListBase[TableVersion]
		"""

		return cast(RestListBase[TableVersion], self.client._send_request(
			path='/accounts/{account}/tables/{name}/versions',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'showAll': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'page': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'showAll': show_all,
				'page': page,
			},
			result_type="RestListBase",
			item_type="TableVersion",
			timeout=timeout
		))
	def get(self, *,
		account: str,
		name: str,
		version: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TableVersion:
		"""
		Get a specific table version.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param version: The table version number (a 64 bit integer) or the string "latest".
		:type version: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TableVersion
		"""

		return cast(TableVersion, self.client._send_request(
			path='/accounts/{account}/tables/{name}/versions/{version}',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'version': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'version': version,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TableVersion",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		name: str,
		version: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete the specified table version.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param version: The table version number (a 64 bit integer) or the string "latest".
		:type version: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/tables/{name}/versions/{version}',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'version': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'name': name,
				'version': version,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def export(self, *,
		account: str,
		name: str,
		version: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		export: Optional[ExportSettings] = None,
		accept: Optional[TablesVersionsExportAcceptType] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		Download table data. Specify export format with the `Accept` header.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param version: The table version number (a 64 bit integer) or the string "latest".
		:type version: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param export:
		:type export: ExportSettings or None
		:param accept: The desired response content type.
		:type accept: TablesVersionsExportAcceptType or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/accounts/{account}/tables/{name}/versions/{version}/export',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'version': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'export': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'accept': { 'in': ParameterLocation.HEADER, 'style': ParameterStyle.SIMPLE, 'explode': False },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.BINARY,
			request={
				'account': account,
				'name': name,
				'version': version,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'export': export,
				'accept': accept,
			},
			result_type="bytes",
			item_type=None,
			timeout=timeout
		))
	def export_url(self, *,
		account: str,
		name: str,
		version: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		export: Optional[ExportSettings] = None,
		accept: Optional[TablesVersionsExportAcceptType] = None,
	) -> str:
		"""Build a URL for this Rest endpoint."""
		return self.client._get_url(
			path='/accounts/{account}/tables/{name}/versions/{version}/export',
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'version': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'export': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'accept': { 'in': ParameterLocation.HEADER, 'style': ParameterStyle.SIMPLE, 'explode': False },
			},
			request={
				'account': account,
				'name': name,
				'version': version,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'export': export,
				'accept': accept,
			}
		)
	def active(self, *,
		account: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TableVersionActive:
		"""
		Get the active table version for a specific table.

		:param account: Account id or code
		:type account: str
		:param name: The table name. Just the name - no account code or table version.
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TableVersionActive
		"""

		return cast(TableVersionActive, self.client._send_request(
			path='/accounts/{account}/tables/{name}/versions/active',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TableVersionActive",
			item_type=None,
			timeout=timeout
		))
class TablesTagsEndpoints: # pylint: disable=missing-class-docstring
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		account: str,
		table: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[TableTag]:
		"""
		Get the list of tags for a specific table.

		:param account: Account id or code
		:type account: str
		:param table: The table name. Just the name - no account code or table version.
		:type table: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[TableTag]
		"""

		return cast(RestList[TableTag], self.client._send_request(
			path='/accounts/{account}/tables/{table}/tags',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'table': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'table': table,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="TableTag",
			timeout=timeout
		))
	def get(self, *,
		account: str,
		table: str,
		key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TableTag:
		"""
		Get a specific table tag.

		:param account: Account id or code
		:type account: str
		:param table: The table name. Just the name - no account code or table version.
		:type table: str
		:param key: The key which identifies this tag.
		:type key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TableTag
		"""

		return cast(TableTag, self.client._send_request(
			path='/accounts/{account}/tables/{table}/tags/{key}',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'table': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'key': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'table': table,
				'key': key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TableTag",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		account: str,
		table: str,
		key: str,
		body: UpdateTableTagRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TableTag:
		"""
		Create or modify a table tag.

		:param account: Account id or code
		:type account: str
		:param table: The table name. Just the name - no account code or table version.
		:type table: str
		:param key: The key which identifies this tag.
		:type key: str
		:param body:
		:type body: UpdateTableTagRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TableTag
		"""

		return cast(TableTag, self.client._send_request(
			path='/accounts/{account}/tables/{table}/tags/{key}',
			method=HttpMethod.PUT,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'table': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'key': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'table': table,
				'key': key,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TableTag",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		table: str,
		key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete a table tag.

		:param account: Account id or code
		:type account: str
		:param table: The table name. Just the name - no account code or table version.
		:type table: str
		:param key: The key which identifies this tag.
		:type key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/tables/{table}/tags/{key}',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'table': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'key': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'table': table,
				'key': key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class TileSetsEndpoints:
	"""
	Tile sets are custom map layers composed of uploaded imagery, pre-sliced into slippy map tiles. If instead you want to import a GeoTiff file as an Image column in a MapLarge table, use the `/restapi/v1/accounts/{account}/tables/{name}` (CreateTable, etc.) endpoints instead.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		account: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[TileSet]:
		"""
		Get a list of tile sets belonging to an account.

		:param account: Account id or code
		:type account: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[TileSet]
		"""

		return cast(RestList[TileSet], self.client._send_request(
			path='/accounts/{account}/tilesets',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="TileSet",
			timeout=timeout
		))
	def get(self, *,
		account: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TileSet:
		"""
		Get a specific tile set.

		:param account: Account id or code
		:type account: str
		:param name: The name of the tile set.
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TileSet
		"""

		return cast(TileSet, self.client._send_request(
			path='/accounts/{account}/tilesets/{name}',
			method=HttpMethod.GET,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TileSet",
			item_type=None,
			timeout=timeout
		))
	def post(self, *,
		account: str,
		name: str,
		body: CreateOrUpdateTileSetRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Import:
		"""
		Create or update a tile set asynchronously. Poll `imports/{importGuid}` for status updates.

		:param account: Account id or code
		:type account: str
		:param name: The name of the tile set.
		:type name: str
		:param body:
		:type body: CreateOrUpdateTileSetRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Import
		"""

		return cast(Import, self.client._send_request(
			path='/accounts/{account}/tilesets/{name}',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Import",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		account: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete a specific tile set.

		:param account: Account id or code
		:type account: str
		:param name: The name of the tile set.
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/accounts/{account}/tilesets/{name}',
			method=HttpMethod.DELETE,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'account': account,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def upload(self, *,
		account: str,
		name: str,
		body: CreateOrUpdateTileSetFromFileUploadRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Import:
		"""
		Create or update a tile set by file upload asynchronously. Poll `imports/{importGuid}` for status updates.

		:param account: Account id or code
		:type account: str
		:param name: The name of the tile set.
		:type name: str
		:param body:
		:type body: CreateOrUpdateTileSetFromFileUploadRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Import
		"""

		return cast(Import, self.client._send_request(
			path='/accounts/{account}/tilesets/{name}/upload',
			method=HttpMethod.POST,
			parameters={
				'account': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.MULTI_PART_FORM_DATA,
			response_body=ResponseBodyType.JSON,
			request={
				'account': account,
				'name': name,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Import",
			item_type=None,
			timeout=timeout
		))
class AichatEndpoints:
	"""
	Provides access to AI chat workloads.
	:ivar AichatChatsEndpoints chats: Provides access to AI chat workloads.
	:ivar AichatOpenaiapiEndpoints openaiapi: Provides access to AI chat workloads.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.chats = AichatChatsEndpoints(self.client)
		self.openaiapi = AichatOpenaiapiEndpoints(self.client)
class AichatChatsEndpoints:
	"""
	Provides access to AI chat workloads.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def post(self, *,
		body: ChatRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		
Post a chat message to an LLM and get a response.
The response can optionally be streamed. To do so either leave the chatInfo.stream property unset or set it to true.
If streaming is enabled the server will return a jsonlines formatted list (see: https://jsonlines.org/) of partial chat responses instead of one chat response containing the entire result.
If tools are supplied streaming will be disabled.


		:param body:
		:type body: ChatRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/aichat/chat',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.BINARY,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="bytes",
			item_type="OllamaChatResponse",
			timeout=timeout
		))
class AichatOpenaiapiEndpoints:
	"""
	Provides access to AI chat workloads.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		base_url: Optional[str] = None,
		token: Optional[str] = None,
		relative_path: Optional[str] = None,
		workload_id: Optional[str] = None,
		workload_name: Optional[str] = None,
		workload_port: Optional[int] = None,
		workload_use_https: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		Proxies a request to a Open AI compatible endpoint. Copies the body of the request and usually returns a application/json or text/event-stream.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param base_url:
		:type base_url: str or None
		:param token:
		:type token: str or None
		:param relative_path:
		:type relative_path: str or None
		:param workload_id:
		:type workload_id: str or None
		:param workload_name:
		:type workload_name: str or None
		:param workload_port:
		:type workload_port: int or None
		:param workload_use_https:
		:type workload_use_https: bool or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/aichat/openaiapi',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'baseUrl': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'token': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'relativePath': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadName': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadPort': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadUseHttps': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'baseUrl': base_url,
				'token': token,
				'relativePath': relative_path,
				'workloadId': workload_id,
				'workloadName': workload_name,
				'workloadPort': workload_port,
				'workloadUseHttps': workload_use_https,
			},
			result_type="File",
			item_type=None,
			timeout=timeout
		))
	def post(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		base_url: Optional[str] = None,
		token: Optional[str] = None,
		relative_path: Optional[str] = None,
		workload_id: Optional[str] = None,
		workload_name: Optional[str] = None,
		workload_port: Optional[int] = None,
		workload_use_https: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		Proxies a request to a Open AI compatible endpoint. Copies the body of the request and usually returns a application/json or text/event-stream.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param base_url:
		:type base_url: str or None
		:param token:
		:type token: str or None
		:param relative_path:
		:type relative_path: str or None
		:param workload_id:
		:type workload_id: str or None
		:param workload_name:
		:type workload_name: str or None
		:param workload_port:
		:type workload_port: int or None
		:param workload_use_https:
		:type workload_use_https: bool or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/aichat/openaiapi',
			method=HttpMethod.POST,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'baseUrl': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'token': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'relativePath': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadName': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadPort': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'workloadUseHttps': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'baseUrl': base_url,
				'token': token,
				'relativePath': relative_path,
				'workloadId': workload_id,
				'workloadName': workload_name,
				'workloadPort': workload_port,
				'workloadUseHttps': workload_use_https,
			},
			result_type="File",
			item_type=None,
			timeout=timeout
		))
class AlertTriggersEndpoints:
	"""
	Alerts are events that trigger when a new table is created or data is added to an existing table
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[AlertTrigger]:
		"""
		Get the list of existing alert triggers.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[AlertTrigger]
		"""

		return cast(RestList[AlertTrigger], self.client._send_request(
			path='/alerttrigger',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="AlertTrigger",
			timeout=timeout
		))
	def post(self, *,
		body: AlertRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> AlertTrigger:
		"""
		Create a new alert trigger.

		:param body:
		:type body: AlertRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: AlertTrigger
		"""

		return cast(AlertTrigger, self.client._send_request(
			path='/alerttrigger',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="AlertTrigger",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> AlertTrigger:
		"""
		Get a specific alert trigger.

		:param id_:
		:type id_: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: AlertTrigger
		"""

		return cast(AlertTrigger, self.client._send_request(
			path='/alerttrigger/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="AlertTrigger",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: int,
		body: AlertRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> AlertTrigger:
		"""
		Update an existing alert trigger.

		:param id_:
		:type id_: int
		:param body:
		:type body: AlertRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: AlertTrigger
		"""

		return cast(AlertTrigger, self.client._send_request(
			path='/alerttrigger/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="AlertTrigger",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing alert trigger.

		:param id_:
		:type id_: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/alerttrigger/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class BasemapEndpoints:
	"""
	Retrieve tiles for MapLarge basemaps
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def debugtileprojectionandkey(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		projection: str,
		projection_options_key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param projection: The desired projection of the basemap.  Defaults to Web Mercator.  Available options are "wgs84" or an EPSG code.
		:type projection: str
		:param projection_options_key: A key to look up and use stored projection options on the basemap server
		:type projection_options_key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/debug/v{dataVersion}/{theme}/v{themeVersion}/{projection}/{projectionOptionsKey}/{z}/{x}/{y}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projection': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projectionOptionsKey': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'projection': projection,
				'projectionOptionsKey': projection_options_key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def debugtilefullspec(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		format_: ImageFormatType,
		projection: str,
		projection_options_key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param format_: The desired format of the tile image. Supported extensions are "png", "jpeg", and "webp".
		:type format_: ImageFormatType
		:param projection: The desired projection of the basemap.  Defaults to Web Mercator.  Available options are "wgs84" or an EPSG code.
		:type projection: str
		:param projection_options_key: A key to look up and use stored projection options on the basemap server
		:type projection_options_key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/debug/v{dataVersion}/{theme}/v{themeVersion}/{projection}/{projectionOptionsKey}/{z}/{x}/{y}.{format}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projection': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projectionOptionsKey': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'format': format_,
				'projection': projection,
				'projectionOptionsKey': projection_options_key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def debugtileprojection(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		projection: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param projection: The desired projection of the basemap.  Defaults to Web Mercator.  Available options are "wgs84" or an EPSG code.
		:type projection: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/debug/v{dataVersion}/{theme}/v{themeVersion}/{projection}/{z}/{x}/{y}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projection': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'projection': projection,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def debugtile(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are v[numbers >=1] and the word 'vlatest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/debug/v{dataVersion}/{theme}/v{themeVersion}/{z}/{x}/{y}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def debugtileformat(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		format_: ImageFormatType,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param format_: The desired format of the tile image. Supported extensions are "png", "jpeg", and "webp".
		:type format_: ImageFormatType
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/debug/v{dataVersion}/{theme}/v{themeVersion}/{z}/{x}/{y}.{format}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'format': format_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def themelist(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		debug: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> RestListBase[BasemapTheme]:
		"""
		Gets a list of available basemap themes

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param debug:
		:type debug: bool or None
		:rtype: RestListBase[BasemapTheme]
		"""

		return cast(RestListBase[BasemapTheme], self.client._send_request(
			path='/basemap/themes',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'debug': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'debug': debug,
			},
			result_type="RestListBase",
			item_type="BasemapTheme",
			timeout=timeout
		))
	def themeversionlist(self, *,
		theme_name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		debug: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> BasemapThemeAvailableVersions:
		"""
		Get the available versions for a theme

		:param theme_name: The name of the theme to get available versions for
		:type theme_name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param debug:
		:type debug: bool or None
		:rtype: BasemapThemeAvailableVersions
		"""

		return cast(BasemapThemeAvailableVersions, self.client._send_request(
			path='/basemap/themes/{themeName}',
			method=HttpMethod.GET,
			parameters={
				'themeName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'debug': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'themeName': theme_name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'debug': debug,
			},
			result_type="BasemapThemeAvailableVersions",
			item_type=None,
			timeout=timeout
		))
	def themeversion(self, *,
		theme_name: str,
		theme_version: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		debug: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> BasemapThemeDetail:
		"""
		Get the details of the theme with the corresponding name at the corresponding version

		:param theme_name: The name of the theme to get details for
		:type theme_name: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param debug:
		:type debug: bool or None
		:rtype: BasemapThemeDetail
		"""

		return cast(BasemapThemeDetail, self.client._send_request(
			path='/basemap/themes/{themeName}/v{themeVersion}',
			method=HttpMethod.GET,
			parameters={
				'themeName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'debug': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'themeName': theme_name,
				'themeVersion': theme_version,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'debug': debug,
			},
			result_type="BasemapThemeDetail",
			item_type=None,
			timeout=timeout
		))
	def tileprojectionandkey(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		projection: str,
		projection_options_key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param projection: The desired projection of the basemap.  Defaults to Web Mercator.  Available options are "wgs84" or an EPSG code.
		:type projection: str
		:param projection_options_key: A key to look up and use stored projection options on the basemap server
		:type projection_options_key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/v{dataVersion}/{theme}/v{themeVersion}/{projection}/{projectionOptionsKey}/{z}/{x}/{y}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projection': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projectionOptionsKey': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'projection': projection,
				'projectionOptionsKey': projection_options_key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def tilefullspec(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		format_: ImageFormatType,
		projection: str,
		projection_options_key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param format_: The desired format of the tile image. Supported extensions are "png", "jpeg", and "webp".
		:type format_: ImageFormatType
		:param projection: The desired projection of the basemap.  Defaults to Web Mercator.  Available options are "wgs84" or an EPSG code.
		:type projection: str
		:param projection_options_key: A key to look up and use stored projection options on the basemap server
		:type projection_options_key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/v{dataVersion}/{theme}/v{themeVersion}/{projection}/{projectionOptionsKey}/{z}/{x}/{y}.{format}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projection': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projectionOptionsKey': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'format': format_,
				'projection': projection,
				'projectionOptionsKey': projection_options_key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def tileprojection(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		projection: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param projection: The desired projection of the basemap.  Defaults to Web Mercator.  Available options are "wgs84" or an EPSG code.
		:type projection: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/v{dataVersion}/{theme}/v{themeVersion}/{projection}/{z}/{x}/{y}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'projection': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'projection': projection,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def tile(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are v[numbers >=1] and the word 'vlatest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/v{dataVersion}/{theme}/v{themeVersion}/{z}/{x}/{y}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def tileformat(self, *,
		data_version: str,
		theme: str,
		theme_version: str,
		z: str,
		x: str,
		y: str,
		format_: ImageFormatType,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get the basemap tile at the specified x/y/z

		:param data_version: The desired data version.  Valid values are v[numbers > 1] and the word 'vlatest'
		:type data_version: str
		:param theme: The named theme of the basemap
		:type theme: str
		:param theme_version: The desired theme version. Valid values are numbers >=1 and the word 'latest'
		:type theme_version: str
		:param z: The zoom level of the requested tile
		:type z: str
		:param x: The X coordinate of the requested tile
		:type x: str
		:param y: The Y coordinate of the requested tile
		:type y: str
		:param format_: The desired format of the tile image. Supported extensions are "png", "jpeg", and "webp".
		:type format_: ImageFormatType
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/basemap/v{dataVersion}/{theme}/v{themeVersion}/{z}/{x}/{y}.{format}',
			method=HttpMethod.GET,
			parameters={
				'dataVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'theme': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'themeVersion': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'z': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'dataVersion': data_version,
				'theme': theme,
				'themeVersion': theme_version,
				'z': z,
				'x': x,
				'y': y,
				'format': format_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class CatalogEndpoints:
	"""
	Catalog of data sources (tables, layers, queries) available by standard services.
	:ivar CatalogEntriesEndpoints entries: Catalog of data sources (tables, layers, queries) available by standard services.
	:ivar CatalogDetailsEndpoints details: Catalog of data sources (tables, layers, queries) available by standard services.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.entries = CatalogEntriesEndpoints(self.client)
		self.details = CatalogDetailsEndpoints(self.client)
class CatalogEntriesEndpoints:
	"""
	Catalog of data sources (tables, layers, queries) available by standard services.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestListBase[CatalogEntry]:
		"""
		Get list of catalog current catalog entries, active or not

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestListBase[CatalogEntry]
		"""

		return cast(RestListBase[CatalogEntry], self.client._send_request(
			path='/catalog',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestListBase",
			item_type="CatalogEntry",
			timeout=timeout
		))
	def post(self, *,
		body: CatalogEntry,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> CatalogEntry:
		"""
		Add a new catalog entry

		:param body:
		:type body: CatalogEntry
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: CatalogEntry
		"""

		return cast(CatalogEntry, self.client._send_request(
			path='/catalog',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="CatalogEntry",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		body: CatalogEntry,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> CatalogEntry:
		"""
		Update an existing entry

		:param body:
		:type body: CatalogEntry
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: CatalogEntry
		"""

		return cast(CatalogEntry, self.client._send_request(
			path='/catalog',
			method=HttpMethod.PUT,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="CatalogEntry",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		published_id: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> CatalogEntry:
		"""
		Get a specific entry

		:param published_id: Catalog Entry Id
		:type published_id: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: CatalogEntry
		"""

		return cast(CatalogEntry, self.client._send_request(
			path='/catalog/{publishedId}',
			method=HttpMethod.GET,
			parameters={
				'publishedId': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'publishedId': published_id,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="CatalogEntry",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		body: CatalogEntry,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing entry

		:param body:
		:type body: CatalogEntry
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/catalog/{publishedId}',
			method=HttpMethod.DELETE,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.NONE,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class CatalogDetailsEndpoints:
	"""
	Catalog of data sources (tables, layers, queries) available by standard services.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		id_: Optional[str] = None,
		timeout: Optional[float] = None
	) -> CatalogDetails:
		"""
		Get GIS and schema information regarding a specific catalog entry

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param id_: Id of the catalog entry to be viewed
		:type id_: str or None
		:rtype: CatalogDetails
		"""

		return cast(CatalogDetails, self.client._send_request(
			path='/catalog/{publishedId}/details',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'id': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'id': id_,
			},
			result_type="CatalogDetails",
			item_type=None,
			timeout=timeout
		))
class ClusterEndpoints:
	"""
	Manage cluster-based administrative operations.
	:ivar ClusterNodesEndpoints nodes: Manage cluster-based administrative operations.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.nodes = ClusterNodesEndpoints(self.client)
class ClusterNodesEndpoints:
	"""
	Manage cluster-based administrative operations.
	:ivar ClusterNodesRoleEndpoints role: Manage cluster-based administrative operations.
	:ivar ClusterNodesSnapshotsEndpoints snapshots: Manage cluster-based administrative operations.
	:ivar ClusterNodesTransactionsEndpoints transactions: Manage cluster-based administrative operations.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.role = ClusterNodesRoleEndpoints(self.client)
		self.snapshots = ClusterNodesSnapshotsEndpoints(self.client)
		self.transactions = ClusterNodesTransactionsEndpoints(self.client)
	def purge_node(self, *,
		address: str,
		body: ClusterOptions,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Creates a purge node request on a single cluster node

		:param address: Node address for the purge request
		:type address: str
		:param body:
		:type body: ClusterOptions
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/cluster/nodes/{address}/purge',
			method=HttpMethod.POST,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.NONE,
			request={
				'address': address,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def recycle_app(self, *,
		address: str,
		body: ClusterOptions,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Creates a recycle request on a single cluster node

		:param address: Node address for recycle address
		:type address: str
		:param body:
		:type body: ClusterOptions
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/cluster/nodes/{address}/recycle',
			method=HttpMethod.POST,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.NONE,
			request={
				'address': address,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def take_snapshot(self, *,
		address: str,
		body: ClusterOptions,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Snapshot]:
		"""
		Create a snapshot on a single cluster node

		:param address: Node address for the snapshot
		:type address: str
		:param body:
		:type body: ClusterOptions
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Snapshot]
		"""

		return cast(RestList[Snapshot], self.client._send_request(
			path='/cluster/nodes/{address}/snapshots',
			method=HttpMethod.POST,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'address': address,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Snapshot",
			timeout=timeout
		))
	def stop_app(self, *,
		address: str,
		body: ClusterOptions,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Creates a stopapp request on a single cluster node

		:param address: Node address for stop request
		:type address: str
		:param body:
		:type body: ClusterOptions
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/cluster/nodes/{address}/stopapp',
			method=HttpMethod.POST,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.NONE,
			request={
				'address': address,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class ClusterNodesRoleEndpoints:
	"""
	Manage cluster-based administrative operations.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def add(self, *,
		address: str,
		body: Role,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Node:
		"""
		Add a new raft role.

		:param address: Node address
		:type address: str
		:param body:
		:type body: Role
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Node
		"""

		return cast(Node, self.client._send_request(
			path='/cluster/nodes/{address}/roles',
			method=HttpMethod.POST,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'address': address,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Node",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		address: str,
		name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Remove a raft role.

		:param address: Node address
		:type address: str
		:param name: Name of the role to be deleted
		:type name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/cluster/nodes/{address}/roles/{name}',
			method=HttpMethod.DELETE,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'name': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'address': address,
				'name': name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class ClusterNodesSnapshotsEndpoints:
	"""
	Manage cluster-based administrative operations.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		address: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Snapshot]:
		"""
		Get available snapshots for a specific node.

		:param address: Node address
		:type address: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Snapshot]
		"""

		return cast(RestList[Snapshot], self.client._send_request(
			path='/cluster/nodes/{address}/snapshots',
			method=HttpMethod.GET,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'address': address,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Snapshot",
			timeout=timeout
		))
class ClusterNodesTransactionsEndpoints:
	"""
	Manage cluster-based administrative operations.
	:ivar ClusterNodesTransactionsFailedEndpoints failed: Manage cluster-based administrative operations.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.failed = ClusterNodesTransactionsFailedEndpoints(self.client)
class ClusterNodesTransactionsFailedEndpoints:
	"""
	Manage cluster-based administrative operations.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		address: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[FailedTransactionsOptions] = None,
		timeout: Optional[float] = None
	) -> RestList[FailedTransaction]:
		"""
		Get failed transactions for a specific node address

		:param address: The address of the cluster node
		:type address: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param options:
		:type options: FailedTransactionsOptions or None
		:rtype: RestList[FailedTransaction]
		"""

		return cast(RestList[FailedTransaction], self.client._send_request(
			path='/cluster/nodes/{address}/transactions/failed',
			method=HttpMethod.GET,
			parameters={
				'address': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'address': address,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			},
			result_type="RestList",
			item_type="FailedTransaction",
			timeout=timeout
		))
class DatastreamEndpoints:
	"""
	Manage re-usable resources for datastreams pipeline.
	:ivar DatastreamResourcesEndpoints resources: Manage re-usable resources for datastreams pipeline.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.resources = DatastreamResourcesEndpoints(self.client)
class DatastreamResourcesEndpoints:
	"""
	Manage re-usable resources for datastreams pipeline.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[DataStreamResource]:
		"""
		Get the list of existing Datastream Resources.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[DataStreamResource]
		"""

		return cast(RestList[DataStreamResource], self.client._send_request(
			path='/datastreams/resources',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="DataStreamResource",
			timeout=timeout
		))
	def post(self, *,
		body: CreateDataStreamResourceRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> DataStreamResource:
		"""
		Create a new datastream resource.

		:param body:
		:type body: CreateDataStreamResourceRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: DataStreamResource
		"""

		return cast(DataStreamResource, self.client._send_request(
			path='/datastreams/resources',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="DataStreamResource",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: str,
		body: UpdateDataStreamResourceRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> DataStreamResource:
		"""
		Update an existing pipeline.

		:param id_: The unique resource id
		:type id_: str
		:param body:
		:type body: UpdateDataStreamResourceRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: DataStreamResource
		"""

		return cast(DataStreamResource, self.client._send_request(
			path='/datastreams/resources/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="DataStreamResource",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing resource.

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/datastreams/resources/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_or_name: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> DataStreamResource:
		"""
		Get a specific resource using name or id.

		:param id_or_name: The unique ID or unique name of the Resource
		:type id_or_name: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: DataStreamResource
		"""

		return cast(DataStreamResource, self.client._send_request(
			path='/datastreams/resources/{idOrName}',
			method=HttpMethod.GET,
			parameters={
				'idOrName': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'idOrName': id_or_name,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="DataStreamResource",
			item_type=None,
			timeout=timeout
		))
class DiagnosticsEndpoints:
	"""
	Provides access to statistical information
	:ivar DiagnosticsStatusEndpoints status: Provides access to statistical information
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.status = DiagnosticsStatusEndpoints(self.client)
class DiagnosticsStatusEndpoints:
	"""
	Provides access to statistical information
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Node]:
		"""
		Get cluster health and statistics for all nodes.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Node]
		"""

		return cast(RestList[Node], self.client._send_request(
			path='/diagnostics/status',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Node",
			timeout=timeout
		))
	def get(self, *,
		node_id: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Node:
		"""
		Get cluster health and statistics.

		:param node_id:
		:type node_id: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Node
		"""

		return cast(Node, self.client._send_request(
			path='/diagnostics/status/{nodeId}',
			method=HttpMethod.GET,
			parameters={
				'nodeId': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'nodeId': node_id,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Node",
			item_type=None,
			timeout=timeout
		))
class ImportsEndpoints:
	"""
	Manage long-running import processes.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[GetImportOptions] = None,
		timeout: Optional[float] = None
	) -> Import:
		"""
		Check the status of an import.

		:param id_: Unique string id of the import. A guid with no dashes, 32 hexadecimal digits.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param options:
		:type options: GetImportOptions or None
		:rtype: Import
		"""

		return cast(Import, self.client._send_request(
			path='/imports/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			},
			result_type="Import",
			item_type=None,
			timeout=timeout
		))
	def result(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[TableVersion]:
		"""
		Get the results of an import.

		:param id_: Unique string id of the import. A guid with no dashes, 32 hexadecimal digits.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[TableVersion]
		"""

		return cast(RestList[TableVersion], self.client._send_request(
			path='/imports/{id}/result',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="TableVersion",
			timeout=timeout
		))
class BandwidthLimitsEndpoints:
	"""
	Manage data synchronization between clusters of MapLarge server.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[SyncedAccountPair]:
		"""
		Get the list of bandwidth limits

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[SyncedAccountPair]
		"""

		return cast(RestList[SyncedAccountPair], self.client._send_request(
			path='/intercluster/bandwidthlmits',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="SyncedAccountPair",
			timeout=timeout
		))
	def post(self, *,
		body: CreateBandwidthLimitRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> BandwidthLimit:
		"""
		Create a new bandwidth limit.

		:param body:
		:type body: CreateBandwidthLimitRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: BandwidthLimit
		"""

		return cast(BandwidthLimit, self.client._send_request(
			path='/intercluster/bandwidthlmits',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="BandwidthLimit",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> BandwidthLimit:
		"""
		Get an existing bandwidth limit.

		:param id_: Id of the intercluster bandwidth limit.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: BandwidthLimit
		"""

		return cast(BandwidthLimit, self.client._send_request(
			path='/intercluster/bandwidthlmits/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="BandwidthLimit",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: str,
		body: UpdateBandwidthLimitRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> CentralServer:
		"""
		Modify an existing bandwidth limit.

		:param id_:
		:type id_: str
		:param body:
		:type body: UpdateBandwidthLimitRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: CentralServer
		"""

		return cast(CentralServer, self.client._send_request(
			path='/intercluster/bandwidthlmits/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="CentralServer",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing bandwidth limit.

		:param id_: Id of the intercluster bandwidth limit.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/intercluster/bandwidthlmits/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class ServersEndpoints:
	"""
	Manage data synchronization between clusters of MapLarge server.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[CentralServer]:
		"""
		Get the list of existing intercluster servers.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[CentralServer]
		"""

		return cast(RestList[CentralServer], self.client._send_request(
			path='/intercluster/servers',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="CentralServer",
			timeout=timeout
		))
	def post(self, *,
		body: CreateCentralServerRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> CentralServer:
		"""
		Create a new intercluster server.

		:param body:
		:type body: CreateCentralServerRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: CentralServer
		"""

		return cast(CentralServer, self.client._send_request(
			path='/intercluster/servers',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="CentralServer",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> CentralServer:
		"""
		Get an existing intercluster server.

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: CentralServer
		"""

		return cast(CentralServer, self.client._send_request(
			path='/intercluster/servers/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="CentralServer",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: str,
		body: UpdateCentralServerRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> CentralServer:
		"""
		Modify an existing intercluster server.

		:param id_:
		:type id_: str
		:param body:
		:type body: UpdateCentralServerRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: CentralServer
		"""

		return cast(CentralServer, self.client._send_request(
			path='/intercluster/servers/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="CentralServer",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing intercluster server.

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/intercluster/servers/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class AccountPairsEndpoints:
	"""
	Manage data synchronization between clusters of MapLarge server.
	:ivar AccountPairsSynchronizedEndpoints synchronized: Manage data synchronization between clusters of MapLarge server.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.synchronized = AccountPairsSynchronizedEndpoints(self.client)
	def list(self, *,
		server: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[SyncedAccountPair]:
		"""
		Get the list of synced accounts belonging to an intercluster server

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[SyncedAccountPair]
		"""

		return cast(RestList[SyncedAccountPair], self.client._send_request(
			path='/intercluster/servers/{server}/accountpairs',
			method=HttpMethod.GET,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="SyncedAccountPair",
			timeout=timeout
		))
	def post(self, *,
		server: str,
		body: CreateSyncedAccountPairRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> SyncedAccountPair:
		"""
		Create a new intercluster account pair.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param body:
		:type body: CreateSyncedAccountPairRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: SyncedAccountPair
		"""

		return cast(SyncedAccountPair, self.client._send_request(
			path='/intercluster/servers/{server}/accountpairs',
			method=HttpMethod.POST,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="SyncedAccountPair",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		server: str,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> SyncedAccountPair:
		"""
		Get an existing intercluster account pair.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param id_: Id of the intercluster account pair.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: SyncedAccountPair
		"""

		return cast(SyncedAccountPair, self.client._send_request(
			path='/intercluster/servers/{server}/accountpairs/{id}',
			method=HttpMethod.GET,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="SyncedAccountPair",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		server: str,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing intercluster account pair.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param id_: Id of the intercluster account pair.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/intercluster/servers/{server}/accountpairs/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'server': server,
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class AccountPairsSynchronizedEndpoints:
	"""
	Manage data synchronization between clusters of MapLarge server.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		server: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[SyncedAccountPair]:
		"""
		Get the list of all synchronized account pairs belonging to an intercluster server, with info about synchronization status.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[SyncedAccountPair]
		"""

		return cast(RestList[SyncedAccountPair], self.client._send_request(
			path='/intercluster/servers/{server}/accountpairs/synchronized',
			method=HttpMethod.GET,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="SyncedAccountPair",
			timeout=timeout
		))
class TablePairsEndpoints:
	"""
	Manage data synchronization between clusters of MapLarge server.
	:ivar TablePairsSynchronizedEndpoints synchronized: Manage data synchronization between clusters of MapLarge server.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.synchronized = TablePairsSynchronizedEndpoints(self.client)
	def list(self, *,
		server: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[SyncedTablePair]:
		"""
		Get the list of tables belonging to an intercluster server, with info about synchronization status if the table is part of a synchronized table pair.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[SyncedTablePair]
		"""

		return cast(RestList[SyncedTablePair], self.client._send_request(
			path='/intercluster/servers/{server}/tablepairs',
			method=HttpMethod.GET,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="SyncedTablePair",
			timeout=timeout
		))
	def post(self, *,
		server: str,
		body: CreateSyncedTablePairRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> SyncedTablePair:
		"""
		Create a new intercluster table pair.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param body:
		:type body: CreateSyncedTablePairRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: SyncedTablePair
		"""

		return cast(SyncedTablePair, self.client._send_request(
			path='/intercluster/servers/{server}/tablepairs',
			method=HttpMethod.POST,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="SyncedTablePair",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		server: str,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> SyncedTablePair:
		"""
		Get an existing intercluster table pair.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param id_: Id of the intercluster table pair.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: SyncedTablePair
		"""

		return cast(SyncedTablePair, self.client._send_request(
			path='/intercluster/servers/{server}/tablepairs/{id}',
			method=HttpMethod.GET,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="SyncedTablePair",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		server: str,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing intercluster table pair.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param id_: Id of the intercluster table pair.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/intercluster/servers/{server}/tablepairs/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'server': server,
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def sync(self, *,
		server: str,
		id_: str,
		body: SyncSyncedTablePairRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Force an intercluster table pair to sync.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param id_: Id of the intercluster table pair.
		:type id_: str
		:param body:
		:type body: SyncSyncedTablePairRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/intercluster/servers/{server}/tablepairs/{id}/sync',
			method=HttpMethod.POST,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.NONE,
			request={
				'server': server,
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class TablePairsSynchronizedEndpoints:
	"""
	Manage data synchronization between clusters of MapLarge server.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		server: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[SyncedTablePair]:
		"""
		Get the list of all synchronized tables belonging to an intercluster server, with info about synchronization status.

		:param server: Id of the central (remote) intercluster server.
		:type server: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[SyncedTablePair]
		"""

		return cast(RestList[SyncedTablePair], self.client._send_request(
			path='/intercluster/servers/{server}/tablepairs/synchronized',
			method=HttpMethod.GET,
			parameters={
				'server': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'server': server,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="SyncedTablePair",
			timeout=timeout
		))
class LayersEndpoints:
	"""
	Create visualizations of geospatial data.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def post(self, *,
		body: Layer,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> LayerResponse:
		"""
		Prepare a layer for display.

		:param body:
		:type body: Layer
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: LayerResponse
		"""

		return cast(LayerResponse, self.client._send_request(
			path='/layers',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="LayerResponse",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> LayerDefinitionResponse:
		"""
		Get the definition of an existing layer.

		:param hash_: The layer hash. An MD5 hash of a JSON object containing a single 'layer' property containing the Layer object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: LayerDefinitionResponse
		"""

		return cast(LayerDefinitionResponse, self.client._send_request(
			path='/layers/{hash}',
			method=HttpMethod.GET,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="LayerDefinitionResponse",
			item_type=None,
			timeout=timeout
		))
	def exists_by_head(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> bool:
		"""
		Check the existence of a layer.

		:param hash_: The layer hash. An MD5 hash of a JSON object containing a single 'layer' property containing the Layer object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: bool
		"""

		return cast(bool, self.client._send_request(
			path='/layers/{hash}',
			method=HttpMethod.HEAD,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="bool",
			item_type=None,
			timeout=timeout
		))
	def exists(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> bool:
		"""
		Check the existence of a layer.

		:param hash_: The layer hash. An MD5 hash of a JSON object containing a single 'layer' property containing the Layer object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: bool
		"""

		return cast(bool, self.client._send_request(
			path='/layers/{hash}/exists',
			method=HttpMethod.GET,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="bool",
			item_type=None,
			timeout=timeout
		))
	def click(self, *,
		hashes: List[str],
		zoom: int,
		lat: float,
		lng: float,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Dict[str, RowResponse]:
		"""
		

		:param hashes: Comma separated list of the layer hashes.
		:type hashes: List[str]
		:param zoom: Map zoom level. 0 = Whole world in one tile (1x1). 1 = Whole world in 4 tiles (2x2), etc...
		:type zoom: int
		:param lat: The latitude of the point that was clicked.
		:type lat: float
		:param lng: The longitude of the point that was clicked.
		:type lng: float
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Dict[str, RowResponse]
		"""

		return cast(Dict[str, RowResponse], self.client._send_request(
			path='/layers/click',
			method=HttpMethod.GET,
			parameters={
				'hashes': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': False },
				'zoom': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'lat': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'lng': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hashes': hashes,
				'zoom': zoom,
				'lat': lat,
				'lng': lng,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="dict",
			item_type="RowResponse",
			timeout=timeout
		))
	def hover_grid(self, *,
		hashes: List[str],
		zoom: int,
		x: int,
		y: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		labels: Optional[List[str]] = None,
		timeout: Optional[float] = None
	) -> Dict[str, HoverGridData]:
		"""
		Get information to be displayed when the mouse cursor hovers over map data.

		:param hashes: Comma separated list of the layer hashes.
		:type hashes: List[str]
		:param zoom: Map zoom level. 0 = Whole world in one tile (1x1). 1 = Whole world in 4 tiles (2x2), etc...
		:type zoom: int
		:param x: X-coordinate of the tile, numbered west-to-east (left-to-right). Tiles at X = 0 are bordered by 180° W longitude on their west (left) edge. Min = 0. Max = 2^zoom - 1.
		:type x: int
		:param y: Y-coordinate of the tile, numbered north-to-south (top-to-bottom). Tiles at Y = 0 are bordered by 90° N latitude on their north (top) edge. Min = 0. Max = 2^zoom - 1.
		:type y: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param labels: For each layer requested, the column to use for hoverText (the third element in the `data` arrays in the response). See HoverGridData for more information.
		:type labels: List[str] or None
		:rtype: Dict[str, HoverGridData]
		"""

		return cast(Dict[str, HoverGridData], self.client._send_request(
			path='/layers/hovergrids/{zoom}/{x}/{y}',
			method=HttpMethod.GET,
			parameters={
				'hashes': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': False },
				'zoom': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'labels': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hashes': hashes,
				'zoom': zoom,
				'x': x,
				'y': y,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'labels': labels,
			},
			result_type="dict",
			item_type="HoverGridData",
			timeout=timeout
		))
	def image(self, *,
		hashes: List[str],
		format_: ImageFormatType,
		dimensions: MapImageDimensions,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[MapImageOptions] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		Fetch arbitrary sized rendered map image.

		:param hashes: Comma separated list of the layer hashes.
		:type hashes: List[str]
		:param format_: The file type of the image.
		:type format_: ImageFormatType
		:param dimensions:
		:type dimensions: MapImageDimensions
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param options:
		:type options: MapImageOptions or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/layers/image.{format}',
			method=HttpMethod.GET,
			parameters={
				'hashes': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'dimensions': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.BINARY,
			request={
				'hashes': hashes,
				'format': format_,
				'dimensions': dimensions,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			},
			result_type="bytes",
			item_type=None,
			timeout=timeout
		))
	def image_url(self, *,
		hashes: List[str],
		format_: ImageFormatType,
		dimensions: MapImageDimensions,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[MapImageOptions] = None,
	) -> str:
		"""Build a URL for this Rest endpoint."""
		return self.client._get_url(
			path='/layers/image.{format}',
			parameters={
				'hashes': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'dimensions': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request={
				'hashes': hashes,
				'format': format_,
				'dimensions': dimensions,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			}
		)
	def tile(self, *,
		hashes: List[str],
		zoom: int,
		x: int,
		y: int,
		format_: ImageFormatType,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[MapTileOptions] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		Fetch rendered map tiles. 256x256 pixels.

		:param hashes: Comma separated list of the layer hashes.
		:type hashes: List[str]
		:param zoom: Map zoom level. 0 = Whole world in one tile (1x1). 1 = Whole world in 4 tiles (2x2), etc...
		:type zoom: int
		:param x: X-coordinate of the tile, numbered west-to-east (left-to-right). Tiles at X = 0 are bordered by 180° W longitude on their west (left) edge. Min = 0. Max = 2^zoom - 1.
		:type x: int
		:param y: Y-coordinate of the tile, numbered north-to-south (top-to-bottom). Tiles at Y = 0 are bordered by 90° N latitude on their north (top) edge. Min = 0. Max = 2^zoom - 1.
		:type y: int
		:param format_: The file type of the image.
		:type format_: ImageFormatType
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param options:
		:type options: MapTileOptions or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/layers/tiles/{zoom}/{x}/{y}.{format}',
			method=HttpMethod.GET,
			parameters={
				'hashes': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': False },
				'zoom': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.BINARY,
			request={
				'hashes': hashes,
				'zoom': zoom,
				'x': x,
				'y': y,
				'format': format_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			},
			result_type="bytes",
			item_type=None,
			timeout=timeout
		))
	def tile_url(self, *,
		hashes: List[str],
		zoom: int,
		x: int,
		y: int,
		format_: ImageFormatType,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[MapTileOptions] = None,
	) -> str:
		"""Build a URL for this Rest endpoint."""
		return self.client._get_url(
			path='/layers/tiles/{zoom}/{x}/{y}.{format}',
			parameters={
				'hashes': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': False },
				'zoom': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'x': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'y': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'format': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request={
				'hashes': hashes,
				'zoom': zoom,
				'x': x,
				'y': y,
				'format': format_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			}
		)
	@staticmethod
	def hash(layer: Layer) -> str:
		"""Generate a hash from the layer definition."""
		return hash_request({ "layer": layer })

	def ensure(self, layer: Layer) -> str:
		"""Ensure that the layer exists on the server, creating it if it does not exist. Returns the hash."""
		hash_ = LayersEndpoints.hash(layer)
		if self.exists(hash_=hash_):
			return hash_
		response = self.post(body=layer)
		return response.hash_
class NotebooksEndpoints:
	"""
	Provides access to notebooks
	:ivar NotebooksKernelsEndpoints kernels: Provides access to notebooks
	:ivar NotebooksKernelSpecsEndpoints kernel_specs: Provides access to notebooks
	:ivar NotebooksSessionsEndpoints sessions: Provides access to notebooks
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.kernels = NotebooksKernelsEndpoints(self.client)
		self.kernel_specs = NotebooksKernelSpecsEndpoints(self.client)
		self.sessions = NotebooksSessionsEndpoints(self.client)
	def api(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> str:
		"""
		Base api

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: str
		"""

		return cast(str, self.client._send_request(
			path='/notebooks/api',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="str",
			item_type=None,
			timeout=timeout
		))
class NotebooksKernelsEndpoints:
	"""
	Provides access to notebooks
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Kernel:
		"""
		Get kernel

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Kernel
		"""

		return cast(Kernel, self.client._send_request(
			path='/notebooks/api/kernels/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Kernel",
			item_type=None,
			timeout=timeout
		))
class NotebooksKernelSpecsEndpoints:
	"""
	Provides access to notebooks
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> KernelSpecsResponse:
		"""
		Get kernel specs

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: KernelSpecsResponse
		"""

		return cast(KernelSpecsResponse, self.client._send_request(
			path='/notebooks/api/kernelspecs',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="KernelSpecsResponse",
			item_type=None,
			timeout=timeout
		))
class NotebooksSessionsEndpoints:
	"""
	Provides access to notebooks
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> List[Session]:
		"""
		Get sessions

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: List[Session]
		"""

		return cast(List[Session], self.client._send_request(
			path='/notebooks/api/sessions',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="list",
			item_type="Session",
			timeout=timeout
		))
	def post(self, *,
		body: Session,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Session:
		"""
		Create session

		:param body:
		:type body: Session
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Session
		"""

		return cast(Session, self.client._send_request(
			path='/notebooks/api/sessions',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Session",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Session:
		"""
		Get session

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Session
		"""

		return cast(Session, self.client._send_request(
			path='/notebooks/api/sessions/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Session",
			item_type=None,
			timeout=timeout
		))
class OfframpsEndpoints:
	"""
	Provides access to OffRamps which combine observers and pipelines.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Ramp]:
		"""
		Get the list of existing Off Ramps.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Ramp]
		"""

		return cast(RestList[Ramp], self.client._send_request(
			path='/offramps',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Ramp",
			timeout=timeout
		))
	def post(self, *,
		body: CreateRampRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Create a new of off ramp.

		:param body:
		:type body: CreateRampRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/offramps',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Get a specific off ramp.

		:param id_: The unique ID of the Off Ramp
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/offramps/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: str,
		body: UpdateRampRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Update an existing off ramp.

		:param id_: The unique off ramp id
		:type id_: str
		:param body:
		:type body: UpdateRampRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/offramps/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing off ramp.

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/offramps/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def export_ramp(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RampExport:
		"""
		Request an onramp to export.

		:param id_: The unique onramp id
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RampExport
		"""

		return cast(RampExport, self.client._send_request(
			path='/offramps/{id}/export',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RampExport",
			item_type=None,
			timeout=timeout
		))
	def start(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Request an off ramp to start executing.

		:param id_: The unique off ramp id
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/offramps/{id}/start',
			method=HttpMethod.POST,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def stop(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Request an off ramp to stop executing.

		:param id_: The unique off ramp id
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/offramps/{id}/stop',
			method=HttpMethod.POST,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def import_ramp(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		file: Optional[File] = None,
		overwrite_if_exists: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Request a ramp export be imported.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param file: The ramp to import
		:type file: File or None
		:param overwrite_if_exists: Overwrite if a ramp with the same name already exists
		:type overwrite_if_exists: bool or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/offramps/import',
			method=HttpMethod.POST,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'file': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'overwriteIfExists': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'file': file,
				'overwriteIfExists': overwrite_if_exists,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
class OnboardingEndpoints:
	"""
	Copy selected tables and tags to the local cluster from a remote database using various mechanisms (Network filesystem access, Intercluster data mover, etc.)
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def post(self, *,
		body: OnboardingRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> OnboardingResponse:
		"""
		Kick off an onboarding job.

		:param body:
		:type body: OnboardingRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: OnboardingResponse
		"""

		return cast(OnboardingResponse, self.client._send_request(
			path='/onboarding',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="OnboardingResponse",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[GetOnboardingOptions] = None,
		timeout: Optional[float] = None
	) -> OnboardingResponse:
		"""
		Check the status of an onboarding job.

		:param id_: Unique string id of the onboarding job. A guid with no dashes, 32 hexadecimal digits.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param options:
		:type options: GetOnboardingOptions or None
		:rtype: OnboardingResponse
		"""

		return cast(OnboardingResponse, self.client._send_request(
			path='/onboarding/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			},
			result_type="OnboardingResponse",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		options: Optional[GetOnboardingOptions] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Cancel an onboarding job.

		:param id_: Unique string id of the onboarding job. A guid with no dashes, 32 hexadecimal digits.
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param options:
		:type options: GetOnboardingOptions or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/onboarding/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'options': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'options': options,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class OnrampsEndpoints:
	"""
	Provides access to OnRamps which combine connectors and pipelines.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Ramp]:
		"""
		Get the list of existing OnRamps.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Ramp]
		"""

		return cast(RestList[Ramp], self.client._send_request(
			path='/onramps',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Ramp",
			timeout=timeout
		))
	def post(self, *,
		body: CreateRampRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Create a new onramp.

		:param body:
		:type body: CreateRampRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/onramps',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Get a specific onramp.

		:param id_: The unique ID of the OnRamp
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/onramps/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: str,
		body: UpdateRampRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Update an existing onramp.

		:param id_: The unique onramp id
		:type id_: str
		:param body:
		:type body: UpdateRampRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/onramps/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing onramp.

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/onramps/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def export_ramp(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RampExport:
		"""
		Request an onramp to export.

		:param id_: The unique onramp id
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RampExport
		"""

		return cast(RampExport, self.client._send_request(
			path='/onramps/{id}/export',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RampExport",
			item_type=None,
			timeout=timeout
		))
	def start(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Request an onramp to start executing.

		:param id_: The unique onramp id
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/onramps/{id}/start',
			method=HttpMethod.POST,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def stop(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Request an onramp to stop executing.

		:param id_: The unique onramp id
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/onramps/{id}/stop',
			method=HttpMethod.POST,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
	def import_ramp(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		file: Optional[File] = None,
		overwrite_if_exists: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> Ramp:
		"""
		Request a ramp export be imported.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param file: The ramp to import
		:type file: File or None
		:param overwrite_if_exists: Overwrite if a ramp with the same name already exists
		:type overwrite_if_exists: bool or None
		:rtype: Ramp
		"""

		return cast(Ramp, self.client._send_request(
			path='/onramps/import',
			method=HttpMethod.POST,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'file': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'overwriteIfExists': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'file': file,
				'overwriteIfExists': overwrite_if_exists,
			},
			result_type="Ramp",
			item_type=None,
			timeout=timeout
		))
class OpsEndpoints:
	"""
	Provides access to ops functionality
	:ivar OpsImagesEndpoints images: Provides access to ops functionality
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.images = OpsImagesEndpoints(self.client)
class OpsImagesEndpoints:
	"""
	Provides access to ops functionality
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> List[ContainerImage]:
		"""
		

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: List[ContainerImage]
		"""

		return cast(List[ContainerImage], self.client._send_request(
			path='/ops/images',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="list",
			item_type="ContainerImage",
			timeout=timeout
		))
	def post(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> ContainerImage:
		"""
		

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: ContainerImage
		"""

		return cast(ContainerImage, self.client._send_request(
			path='/ops/images',
			method=HttpMethod.POST,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="ContainerImage",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[CentralServer]:
		"""
		

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[CentralServer]
		"""

		return cast(RestList[CentralServer], self.client._send_request(
			path='/ops/images/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="CentralServer",
			timeout=timeout
		))
	def put(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> ContainerImage:
		"""
		

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: ContainerImage
		"""

		return cast(ContainerImage, self.client._send_request(
			path='/ops/images/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="ContainerImage",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/ops/images/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class PackagesEndpoints:
	"""
	Request package export and installation
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def requestexport(self, *,
		body: PackageToExport,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> str:
		"""
		Request a package export

		:param body:
		:type body: PackageToExport
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: str
		"""

		return cast(str, self.client._send_request(
			path='/packages/requestexport',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="str",
			item_type=None,
			timeout=timeout
		))
	def requestinstall(self, *,
		body: PackageToInstall,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> str:
		"""
		Request a package installation

		:param body:
		:type body: PackageToInstall
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: str
		"""

		return cast(str, self.client._send_request(
			path='/packages/requestinstall',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="str",
			item_type=None,
			timeout=timeout
		))
class PipelinesEndpoints:
	"""
	Provides access to pipelines which are used by ramps.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Pipeline]:
		"""
		Get the list of existing Pipelines.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Pipeline]
		"""

		return cast(RestList[Pipeline], self.client._send_request(
			path='/pipelines',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Pipeline",
			timeout=timeout
		))
	def post(self, *,
		body: CreatePipelineRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Pipeline:
		"""
		Create a new pipeline.

		:param body:
		:type body: CreatePipelineRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Pipeline
		"""

		return cast(Pipeline, self.client._send_request(
			path='/pipelines',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Pipeline",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Pipeline:
		"""
		Get a specific pipeline.

		:param id_: The unique ID of the Pipeline
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Pipeline
		"""

		return cast(Pipeline, self.client._send_request(
			path='/pipelines/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Pipeline",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: str,
		body: UpdatePipelineRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Pipeline:
		"""
		Update an existing pipeline.

		:param id_: The unique pipeline id
		:type id_: str
		:param body:
		:type body: UpdatePipelineRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Pipeline
		"""

		return cast(Pipeline, self.client._send_request(
			path='/pipelines/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Pipeline",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing pipeline.

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/pipelines/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def export_pipeline(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> PipelineExport:
		"""
		Request a pipline export.

		:param id_: The unique pipeline id
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: PipelineExport
		"""

		return cast(PipelineExport, self.client._send_request(
			path='/pipelines/{id}/export',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="PipelineExport",
			item_type=None,
			timeout=timeout
		))
	def import_pipeline(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		file: Optional[File] = None,
		overwrite_if_exists: Optional[bool] = None,
		timeout: Optional[float] = None
	) -> Pipeline:
		"""
		Request a pipeline be imported.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param file: The pipeline to import
		:type file: File or None
		:param overwrite_if_exists: Overwrite if a pipeline with the same name already exists
		:type overwrite_if_exists: bool or None
		:rtype: Pipeline
		"""

		return cast(Pipeline, self.client._send_request(
			path='/pipelines/import',
			method=HttpMethod.POST,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'file': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'overwriteIfExists': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'file': file,
				'overwriteIfExists': overwrite_if_exists,
			},
			result_type="Pipeline",
			item_type=None,
			timeout=timeout
		))
class QueriesEndpoints:
	"""
	Execute queries against the MapLarge database.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def post(self, *,
		body: Query,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> QueryResponse:
		"""
		Create a query.

		:param body:
		:type body: Query
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: QueryResponse
		"""

		return cast(QueryResponse, self.client._send_request(
			path='/queries',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="QueryResponse",
			item_type=None,
			timeout=timeout
		))
	def exists_by_head(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> bool:
		"""
		Check the existence of a query.

		:param hash_: The query hash. An MD5 hash of a JSON object containing a single 'query' property containing the Query object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: bool
		"""

		return cast(bool, self.client._send_request(
			path='/queries/{hash}',
			method=HttpMethod.HEAD,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="bool",
			item_type=None,
			timeout=timeout
		))
	def exists(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> bool:
		"""
		Check the existence of a query.

		:param hash_: The query hash. An MD5 hash of a JSON object containing a single 'query' property containing the Query object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: bool
		"""

		return cast(bool, self.client._send_request(
			path='/queries/{hash}/exists',
			method=HttpMethod.GET,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="bool",
			item_type=None,
			timeout=timeout
		))
	def export(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		export: Optional[QueryExportSettings] = None,
		accept: Optional[QueriesExportAcceptType] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		Download query results.

		:param hash_: The query hash. An MD5 hash of a JSON object containing a single 'query' property containing the Query object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param export:
		:type export: QueryExportSettings or None
		:param accept: The desired response content type.
		:type accept: QueriesExportAcceptType or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/queries/{hash}/export',
			method=HttpMethod.GET,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'export': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'accept': { 'in': ParameterLocation.HEADER, 'style': ParameterStyle.SIMPLE, 'explode': False },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.BINARY,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'export': export,
				'accept': accept,
			},
			result_type="bytes",
			item_type=None,
			timeout=timeout
		))
	def export_url(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		export: Optional[QueryExportSettings] = None,
		accept: Optional[QueriesExportAcceptType] = None,
	) -> str:
		"""Build a URL for this Rest endpoint."""
		return self.client._get_url(
			path='/queries/{hash}/export',
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'export': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'accept': { 'in': ParameterLocation.HEADER, 'style': ParameterStyle.SIMPLE, 'explode': False },
			},
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'export': export,
				'accept': accept,
			}
		)
	def result(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> DBResult:
		"""
		Fetch query results.

		:param hash_: The query hash. An MD5 hash of a JSON object containing a single 'query' property containing the Query object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: DBResult
		"""

		return cast(DBResult, self.client._send_request(
			path='/queries/{hash}/result',
			method=HttpMethod.GET,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="DBResult",
			item_type=None,
			timeout=timeout
		))
	def delete_data(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TableModification:
		"""
		Delete data that matches a query.

		:param hash_: The query hash. An MD5 hash of a JSON object containing a single 'query' property containing the Query object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TableModification
		"""

		return cast(TableModification, self.client._send_request(
			path='/queries/{hash}/result',
			method=HttpMethod.DELETE,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TableModification",
			item_type=None,
			timeout=timeout
		))
	def export_direct(self, *,
		body: Query,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		export: Optional[QueryExportSettings] = None,
		accept: Optional[QueriesExportDirectAcceptType] = None,
		timeout: Optional[float] = None
	) -> File:
		"""
		Directly execute a query and download the results.

		:param body:
		:type body: Query
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param export:
		:type export: QueryExportSettings or None
		:param accept: The desired response content type.
		:type accept: QueriesExportDirectAcceptType or None
		:rtype: File
		"""

		return cast(File, self.client._send_request(
			path='/queries/export',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'export': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'accept': { 'in': ParameterLocation.HEADER, 'style': ParameterStyle.SIMPLE, 'explode': False },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.BINARY,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'export': export,
				'accept': accept,
			},
			result_type="bytes",
			item_type=None,
			timeout=timeout
		))
	def result_direct(self, *,
		body: Query,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> DBResult:
		"""
		Directly execute a query.

		:param body:
		:type body: Query
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: DBResult
		"""

		return cast(DBResult, self.client._send_request(
			path='/queries/result',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="DBResult",
			item_type=None,
			timeout=timeout
		))
	def delete_data_direct(self, *,
		body: Query,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TableModification:
		"""
		Delete data that matches a query directly.

		:param body:
		:type body: Query
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TableModification
		"""

		return cast(TableModification, self.client._send_request(
			path='/queries/result',
			method=HttpMethod.DELETE,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TableModification",
			item_type=None,
			timeout=timeout
		))
	def validate(self, *,
		body: Query,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> QueryResponse:
		"""
		Validate a query without adding it to the cache.

		:param body:
		:type body: Query
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: QueryResponse
		"""

		return cast(QueryResponse, self.client._send_request(
			path='/queries/validate',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="QueryResponse",
			item_type=None,
			timeout=timeout
		))
	@staticmethod
	def hash(query: Query) -> str:
		"""Generate a hash from the query definition."""
		return hash_request({
			"action": "table/query", "query": query
		})

	def ensure(self, query: Query) -> str:
		"""Ensure that the query exists on the server, creating it if it does not exist. Returns the hash."""
		hash_ = QueriesEndpoints.hash(query)
		if self.exists(hash_=hash_):
			return hash_
		response = self.post(body=query)
		return response.hash_
class SqlEndpoints:
	"""
	Execute SQL queries against the MapLarge database.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def post(self, *,
		body: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> QueryResponse:
		"""
		Create a sql query.

		:param body:
		:type body: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: QueryResponse
		"""

		return cast(QueryResponse, self.client._send_request(
			path='/sql',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="QueryResponse",
			item_type=None,
			timeout=timeout
		))
	def result(self, *,
		hash_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> DBResult:
		"""
		Fetch sql query results.

		:param hash_: The query hash. An MD5 hash of a JSON object containing a single 'query' property containing the Query object.
		:type hash_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: DBResult
		"""

		return cast(DBResult, self.client._send_request(
			path='/sql/{hash}/result',
			method=HttpMethod.GET,
			parameters={
				'hash': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'hash': hash_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="DBResult",
			item_type=None,
			timeout=timeout
		))
	def result_direct(self, *,
		body: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> DBResult:
		"""
		Directly execute a query.

		:param body:
		:type body: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: DBResult
		"""

		return cast(DBResult, self.client._send_request(
			path='/sql/result',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="DBResult",
			item_type=None,
			timeout=timeout
		))
class TinyurlEndpoints:
	"""
	Creates and retrieves short URL keys that redirect to full URLs.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def getorcreatekey(self, *,
		body: TinyUrlRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> str:
		"""
		Returns an existing TinyUrl key or genrerates a new key if it does not exist.

		:param body:
		:type body: TinyUrlRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: str
		"""

		return cast(str, self.client._send_request(
			path='/u',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="str",
			item_type=None,
			timeout=timeout
		))
	def createkey(self, *,
		body: TinyUrlRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> str:
		"""
		Create a new TinyUrl key.

		:param body:
		:type body: TinyUrlRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: str
		"""

		return cast(str, self.client._send_request(
			path='/u',
			method=HttpMethod.PUT,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="str",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get a redirect response to the full URL based on the given key.

		:param key: The short URL key
		:type key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/u/{key}',
			method=HttpMethod.GET,
			parameters={
				'key': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'key': key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def getentity(self, *,
		key: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> TinyUrlEntity:
		"""
		Get a TinyUrl entity based on the given key.

		:param key: The short URL key
		:type key: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: TinyUrlEntity
		"""

		return cast(TinyUrlEntity, self.client._send_request(
			path='/u/{key}/entity',
			method=HttpMethod.GET,
			parameters={
				'key': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'key': key,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="TinyUrlEntity",
			item_type=None,
			timeout=timeout
		))
class UsersEndpoints:
	"""
	Manage the credentials that are used to authenticate with MapLarge.
	:ivar UsersSelfEndpoints self: Manage the credentials that are used to authenticate with MapLarge.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
		self.self = UsersSelfEndpoints(self.client)
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[User]:
		"""
		Get the list of all users.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[User]
		"""

		return cast(RestList[User], self.client._send_request(
			path='/users',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="User",
			timeout=timeout
		))
	def post(self, *,
		body: CreateUserRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> User:
		"""
		Create a new user.

		:param body:
		:type body: CreateUserRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: User
		"""

		return cast(User, self.client._send_request(
			path='/users',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="User",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> User:
		"""
		Get a specific user.

		:param id_: Numeric user id
		:type id_: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: User
		"""

		return cast(User, self.client._send_request(
			path='/users/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="User",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: int,
		body: UpdateUserRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> User:
		"""
		Update an existing user.

		:param id_: Numeric user id
		:type id_: int
		:param body:
		:type body: UpdateUserRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: User
		"""

		return cast(User, self.client._send_request(
			path='/users/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="User",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing user.

		:param id_: Numeric user id
		:type id_: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/users/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def post_many(self, *,
		body: List[CreateUserRequest],
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> List[User]:
		"""
		Create several new users.

		:param body:
		:type body: List[CreateUserRequest]
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: List[User]
		"""

		return cast(List[User], self.client._send_request(
			path='/users/many',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="list",
			item_type="User",
			timeout=timeout
		))
class UsersSelfEndpoints:
	"""
	Manage the credentials that are used to authenticate with MapLarge.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> User:
		"""
		Get details about the currently authenticated user.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: User
		"""

		return cast(User, self.client._send_request(
			path='/users/self',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="User",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		body: UpdateSelfRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> User:
		"""
		Modify the currently authenticated user.

		:param body:
		:type body: UpdateSelfRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: User
		"""

		return cast(User, self.client._send_request(
			path='/users/self',
			method=HttpMethod.PUT,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="User",
			item_type=None,
			timeout=timeout
		))
	def groups(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Group]:
		"""
		Get the list of groups that the currently authenticated user belongs to.

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Group]
		"""

		return cast(RestList[Group], self.client._send_request(
			path='/users/self/groups',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Group",
			timeout=timeout
		))
class UserGroupsEndpoints:
	"""
	Manage which groups each user belongs to.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		user: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Group]:
		"""
		Get the list of groups that a user belongs to.

		:param user: Numeric user id
		:type user: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Group]
		"""

		return cast(RestList[Group], self.client._send_request(
			path='/users/{user}/groups',
			method=HttpMethod.GET,
			parameters={
				'user': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'user': user,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Group",
			timeout=timeout
		))
	def post(self, *,
		user: int,
		body: GroupReference,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Group:
		"""
		Add a user to a group.

		:param user: Numeric user id
		:type user: int
		:param body:
		:type body: GroupReference
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Group
		"""

		return cast(Group, self.client._send_request(
			path='/users/{user}/groups',
			method=HttpMethod.POST,
			parameters={
				'user': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'user': user,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Group",
			item_type=None,
			timeout=timeout
		))
	def put_many(self, *,
		user: int,
		body: List[GroupReference],
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Group]:
		"""
		Set the groups a user belongs to, within the accounts you are allowed to manage. Any new groups will be added. Any groups not listed will be removed.

		:param user: Numeric user id
		:type user: int
		:param body:
		:type body: List[GroupReference]
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Group]
		"""

		return cast(RestList[Group], self.client._send_request(
			path='/users/{user}/groups',
			method=HttpMethod.PUT,
			parameters={
				'user': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'user': user,
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Group",
			timeout=timeout
		))
	def delete_all(self, *,
		user: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Group]:
		"""
		Delete all the groups a user belongs to, within the accounts you are allowed to manage.

		:param user: Numeric user id
		:type user: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Group]
		"""

		return cast(RestList[Group], self.client._send_request(
			path='/users/{user}/groups',
			method=HttpMethod.DELETE,
			parameters={
				'user': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'user': user,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Group",
			timeout=timeout
		))
	def get(self, *,
		id_: int,
		user: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Group:
		"""
		Get the details of a specific group a user belongs to.

		:param id_: Group id
		:type id_: int
		:param user: Numeric user id
		:type user: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Group
		"""

		return cast(Group, self.client._send_request(
			path='/users/{user}/groups/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'user': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'user': user,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Group",
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		id_: int,
		user: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Group:
		"""
		Add a user to a group.

		:param id_: Group id
		:type id_: int
		:param user: Numeric user id
		:type user: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Group
		"""

		return cast(Group, self.client._send_request(
			path='/users/{user}/groups/{id}',
			method=HttpMethod.PUT,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'user': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'id': id_,
				'user': user,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Group",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: int,
		user: int,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Remove a user from a group.

		:param id_: Group id
		:type id_: int
		:param user: Numeric user id
		:type user: int
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/users/{user}/groups/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'user': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'user': user,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class VfsEndpoints:
	"""
	Provides access to the Virtual File System
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def get(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		path: Optional[str] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Execute REST GET request

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:param path: VFS path
		:type path: str or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/vfs/{*path}',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'path': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
				'path': path,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def createdirectory(self, *,
		body: VfsCreateDirectory,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> VFSControllerCreateDirectoryResult:
		"""
		Create an empty directory in the virtual file system.

		:param body:
		:type body: VfsCreateDirectory
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: VFSControllerCreateDirectoryResult
		"""

		return cast(VFSControllerCreateDirectoryResult, self.client._send_request(
			path='/vfs/createdirectory',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="VFSControllerCreateDirectoryResult",
			item_type=None,
			timeout=timeout
		))
	def deletedirectories(self, *,
		paths: List[str],
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> VFSControllerDeleteDirectoryResult:
		"""
		Delete a list of directories in the virtual file system.

		:param paths: VFS directory paths
		:type paths: List[str]
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: VFSControllerDeleteDirectoryResult
		"""

		return cast(VFSControllerDeleteDirectoryResult, self.client._send_request(
			path='/vfs/deletedirectories',
			method=HttpMethod.DELETE,
			parameters={
				'paths': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'paths': paths,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="VFSControllerDeleteDirectoryResult",
			item_type=None,
			timeout=timeout
		))
	def deletefiles(self, *,
		paths: List[str],
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> VFSControllerDeleteFileResult:
		"""
		Delete a list of files in the virtual file system.

		:param paths: VFS file paths
		:type paths: List[str]
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: VFSControllerDeleteFileResult
		"""

		return cast(VFSControllerDeleteFileResult, self.client._send_request(
			path='/vfs/deletefiles',
			method=HttpMethod.DELETE,
			parameters={
				'paths': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'paths': paths,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="VFSControllerDeleteFileResult",
			item_type=None,
			timeout=timeout
		))
	def renamedirectory(self, *,
		body: VfsEditDirectory,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Execute REST POST requests

		:param body:
		:type body: VfsEditDirectory
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/vfs/renamedirectory',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.NONE,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class WorkflowsEndpoints:
	"""
	Manage alter trigger workflows.
	"""
	# pylint: disable=protected-access

	def __init__(self, client: "RestClient"):
		self.client = client
	def list(self, *,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> RestList[Workflow]:
		"""
		Get the list of existing alert trigger workflows

		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: RestList[Workflow]
		"""

		return cast(RestList[Workflow], self.client._send_request(
			path='/workflows',
			method=HttpMethod.GET,
			parameters={
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.JSON,
			request={
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="RestList",
			item_type="Workflow",
			timeout=timeout
		))
	def post(self, *,
		body: CreateWorkflowRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Workflow:
		"""
		Create a new workflow.

		:param body:
		:type body: CreateWorkflowRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Workflow
		"""

		return cast(Workflow, self.client._send_request(
			path='/workflows',
			method=HttpMethod.POST,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Workflow",
			item_type=None,
			timeout=timeout
		))
	def get(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Get a specific workflow by id

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/workflows/{id}',
			method=HttpMethod.GET,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
	def put(self, *,
		body: CreateWorkflowRequest,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> Workflow:
		"""
		Update an existing Workflow.

		:param body:
		:type body: CreateWorkflowRequest
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: Workflow
		"""

		return cast(Workflow, self.client._send_request(
			path='/workflows/{id}',
			method=HttpMethod.PUT,
			parameters={
				'body': { 'in': ParameterLocation.BODY, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.JSON,
			response_body=ResponseBodyType.JSON,
			request={
				'body': body,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type="Workflow",
			item_type=None,
			timeout=timeout
		))
	def delete(self, *,
		id_: str,
		ml_server_fwd: Optional[str] = None,
		proxy_to_domain: Optional[str] = None,
		proxy_to_cluster_key: Optional[str] = None,
		wait_for_transaction_id: Optional[float] = None,
		timeout: Optional[float] = None
	) -> None:
		"""
		Delete an existing workflow.

		:param id_:
		:type id_: str
		:param ml_server_fwd: The node within this MapLarge cluster that this request should ultimately be executed on.
		:type ml_server_fwd: str or None
		:param proxy_to_domain: The URL of a different MapLarge cluster that this request should be executed on.
		:type proxy_to_domain: str or None
		:param proxy_to_cluster_key: An identifier representing a different MapLarge cluster that this request should be executed on.
		:type proxy_to_cluster_key: str or None
		:param wait_for_transaction_id: The required transactionId that must be present on the processing node before the request can be started.
		:type wait_for_transaction_id: float or None
		:rtype: None
		"""

		return cast(None, self.client._send_request(
			path='/workflows/{id}',
			method=HttpMethod.DELETE,
			parameters={
				'id': { 'in': ParameterLocation.PATH, 'style': ParameterStyle.SIMPLE, 'explode': False },
				'mlServerFwd': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToDomain': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'proxyToClusterKey': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
				'waitForTransactionId': { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True },
			},
			request_body=RequestBodyType.NONE,
			response_body=ResponseBodyType.NONE,
			request={
				'id': id_,
				'mlServerFwd': ml_server_fwd,
				'proxyToDomain': proxy_to_domain,
				'proxyToClusterKey': proxy_to_cluster_key,
				'waitForTransactionId': wait_for_transaction_id,
			},
			result_type=None,
			item_type=None,
			timeout=timeout
		))
class PasswordCredentials:
	"""Credentials for accessing the MapLarge server, consisting of a username and password."""
	def __init__(self, name: str, password: str) -> None:
		self._name = name
		self._password = password

	@property
	def name(self) -> str:
		"""The user's email address."""
		return self._name

	@property
	def password(self) -> str:
		"""The user's password."""
		return self._password

class TokenCredentials:
	"""Credentials for accessing the MapLarge server, consisting of a username and authentication token."""
	def __init__(self, name: str, token: str) -> None:
		self._name = name
		self._token = token

	@property
	def name(self) -> str:
		"""The user's email address."""
		return self._name

	@property
	def token(self) -> str:
		"""An authentication token for the user."""
		return self._token

Credentials = Union[PasswordCredentials, TokenCredentials]
CredentialsCallback = Callable[[], Credentials]

class HttpMethod(str, Enum):
	"""The HTTP verbs used by the MapLarge Rest API."""
	GET = 'GET'
	POST = 'POST'
	PUT = 'PUT'
	DELETE = 'DELETE'
	HEAD = 'HEAD'

class ParameterLocation(Enum):
	"""Indicates where a parameter will be used in a Rest API request."""
	PATH = auto()
	QUERY = auto()
	HEADER = auto()
	BODY = auto()

class ParameterStyle(Enum):
	"""Indicates how a parameter should be serialized."""
	SIMPLE = auto()
	FORM = auto()

class RequestBodyType(Enum):
	"""Indicates the format of the body of a Rest API request."""
	NONE = auto()
	JSON = auto()
	MULTI_PART_FORM_DATA = auto()
	BINARY = auto()

class ResponseBodyType(Enum):
	"""Indicates the format of the body of a Rest API response."""
	NONE = auto()
	JSON = auto()
	BINARY = auto()

class MultiPartFormData:
	"""Builds a multipart/form-data request."""
	def __init__(self) -> None:
		self.fields = [] # type: List[Tuple[str, str]]
		self.files = [] # type: List[Tuple[str, File]]
		self.boundary = uuid.uuid4().hex.encode('utf-8')

	def get_content_type(self) -> str:
		"""Return the value that should be passed via the HTTP request's Content-Type header."""
		return f'multipart/form-data; boundary={self.boundary.decode("utf-8")}'

	def add_field(self, name: str, value: str) -> None:
		"""Add a string key/value pair to the request."""
		self.fields.append((name, value))

	def add_file(self, name: str, upload: File) -> None:
		"""Add a file to the request."""
		self.files.append((name, upload))

	def __bytes__(self) -> bytes:
		buffer = BytesIO()
		boundary = b'--' + self.boundary + b'\r\n'

		for name, value in self.fields:
			buffer.write(boundary)
			buffer.write(f'Content-Disposition: form-data; name="{name}"\r\n'.encode('utf-8'))
			buffer.write(b'\r\n')
			buffer.write(value.encode('utf-8'))
			buffer.write(b'\r\n')

		for name, upload in self.files:
			buffer.write(boundary)
			filename = upload.name or 'upload'
			buffer.write(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode('utf-8'))
			buffer.write(f'Content-Type: {upload.content_type or "application/octet-stream"}\r\n'.encode('utf-8'))
			buffer.write(b'\r\n')
			if isinstance(upload.file, bytes):
				buffer.write(upload.file)
			else:
				buffer.write(upload.file.read())
			buffer.write(b'\r\n')

		buffer.write(b'--' + self.boundary + b'--\r\n')
		return buffer.getvalue()

class No303RedirectHandler(HTTPRedirectHandler):
	"""Causes the URL Opener to not follow 303 "See Other" redirects, returning the 303 status as-is instead."""
	def http_error_303(self, req, fp, code, msg, headers): # type: ignore[no-untyped-def] # pylint: disable=unused-argument
		"""Return the 303 status as-is."""
		return addinfourl(fp, headers, req.get_full_url(), code)

class NoErrorHandler(HTTPDefaultErrorHandler):
	"""Causes the URL Opener to not throw an exception for error codes."""
	def http_error_default(self, req, fp, code, msg, hdrs): # type: ignore[no-untyped-def] # pylint: disable=unused-argument
		"""Do not throw exception."""
		return addinfourl(fp, hdrs, req.get_full_url(), code)

def jsonify(value: Any) -> Any:
	"""
	Prepares a value to be sent to the MapLarge server, converting property names from Python-style
	lowercase_with_underscores, to JSON-style mixedCase.
	"""
	def props(x: object) -> Mapping[str, Any]:
		"""Like the built-in vars function, but this returns the names and values of properties, not attributes."""
		typ = type(x)
		return {
			k:getattr(x, k)
			for k in dir(typ)
			if not k.startswith('__') and hasattr(typ, k) and isinstance(getattr(typ, k), property)
		}

	if isinstance(value, Enum):
		return value.value
	if value is None or isinstance(value, (str, int, float, bool)):
		return value
	if isinstance(value, datetime):
		return value.isoformat()
	if isinstance(value, File):
		return value
	if isinstance(value, bytes):
		return value
	if isinstance(value, dict):
		return { k:jsonify(v) for k,v in value.items() }
	if isinstance(value, tuple):
		return tuple( jsonify(v) for v in value )
	if isinstance(value, Iterable):
		return [ jsonify(v) for v in value ]
	if hasattr(value, 'JSON_NAMES'):
		return {
			value.JSON_NAMES[k][0]:jsonify(v)
			for k,v in props(value).items()
			if v is not None and v != ''
		}
	raise ValueError(f'Unable to convert {value} to JSON.')

NATIVE_TYPES = {
	"str": str,
	"int": int,
	"float": float,
	"bool": bool,
	"datetime": datetime,
	"dict": dict,
	"tuple": tuple,
	"list": list
}
def unjsonify(value: Any, type_: Optional[Union[Type[Any], str]], item_type: Optional[Union[Type[Any], str]] = None, context: Optional[Deque[str]] = None) -> Any:
	"""
	Processes a value received from the MapLarge server, instantiating the correct classes, and
	converting property names from JSON-style mixedCase to Python-style lowercase_with_underscores.
	"""
	if value is None or type_ is None:
		return value
	guaranteed_context = context if context is not None else deque()
	class_ = None # type: Optional[Type[Any]]
	if isinstance(type_, str):
		if type_ in NATIVE_TYPES:
			class_ = NATIVE_TYPES[type_]
		elif hasattr(maplargerest.models, type_):
			class_ = getattr(maplargerest.models, type_)
	else:
		class_ = type_
	if not isclass(class_) and isinstance(type_, str):
		class_, item_type_2 = discriminate(type_, item_type, value, guaranteed_context)
		if not class_:
			raise ValueError(f'{type_} is not a class that can be unjsonified. Context: {"".join(guaranteed_context)}')
		if item_type_2:
			item_type = item_type_2
	guaranteed_class = cast(Type[Any], class_)
	if issubclass(guaranteed_class, Enum):
		return guaranteed_class(value)
	if issubclass(guaranteed_class, (str, int, float, bool)):
		return value
	if issubclass(guaranteed_class, datetime):
		return isoparse(value)
	if issubclass(guaranteed_class, dict):
		dict_result = {}
		for k,v in value.items():
			guaranteed_context.append(f'["{k}"]')
			dict_result[k] = unjsonify(v, item_type, context=guaranteed_context)
			guaranteed_context.pop()
		return dict_result
	if issubclass(guaranteed_class, tuple):
		def unjsonify_with_context(i: int, v: Any) -> Any:
			guaranteed_context.append(f'[{i}]')
			res = unjsonify(v, item_type, context=guaranteed_context)
			guaranteed_context.pop()
			return res
		return tuple(unjsonify_with_context(i, v) for i, v in enumerate(value))
	if issubclass(guaranteed_class, Iterable):
		list_result = []
		for i, v in enumerate(value):
			guaranteed_context.append(f'[{i}]')
			list_result.append(unjsonify(v, item_type, context=guaranteed_context))
			guaranteed_context.pop()
		return list_result
	if hasattr(guaranteed_class, 'JSON_NAMES'):
		kwargs, extra_data = get_init_args(value, guaranteed_class, item_type, guaranteed_context)
		try:
			result = guaranteed_class(**kwargs)
		except Exception as ex:
			raise ValueError(f'Cannot construct {type_}. Context: {"".join(guaranteed_context)}. Error: {ex}') from ex
		for k,v in extra_data.items():
			setattr(result, k, v)
		return result
	return value

def get_init_args(value: Any, typ: Optional[Union[str, Type[Any]]], item_type: Optional[Union[str, Type[Any]]] = None, context: Optional[Deque[str]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
	"""
	Converts a parsed JSON value into the arguments needed to construct and initialize a MapLarge
	model object. Returns a tuple with two elements. The first element is the kwargs dictionary for
	the constructor, and the second element are extra attributes found in the JSON but not
	available in the constructor.
	"""
	if context is None:
		context = deque()
	class_ = getattr(maplargerest.models, typ) if isinstance(typ, str) else typ
	kwargs = {}
	extra_data = {}
	for k,v in value.items():
		if k in class_.JSON_NAMES_INVERSE:
			prop = class_.JSON_NAMES_INVERSE[k]
			_, child_type, child_item_type = class_.JSON_NAMES[prop]
			context.append("." + k)
			kwargs[prop] = unjsonify(v, child_type, child_item_type or item_type, context)
			context.pop()
		else:
			extra_data[k] = v
	return kwargs, extra_data

RestParameter = TypedDict('RestParameter', { 'in': ParameterLocation, 'style': ParameterStyle, 'explode': bool, 'isJson': bool }, total=False)
DEFAULT_PARAM = { 'in': ParameterLocation.QUERY, 'style': ParameterStyle.FORM, 'explode': True } # type: RestParameter

DataT = TypeVar('DataT')
ResourceT = TypeVar('ResourceT')

class RestClient:
	"""
	The MapLarge Rest API client.

	:ivar AccountsEndpoints accounts: Accounts are the top-level organizational structure in the MapLarge API.
	:ivar FoldersEndpoints folders: Resources are used to manage fine-grained access control to various items (currently just tables, but perhaps other things in the future).
	:ivar GroupsEndpoints groups: Create and delete groups. Groups are used to manage user access to accounts.
	:ivar IndexesEndpoints indexes:
	:ivar ResourcesEndpoints resources: Resources are used to manage fine-grained access control to various items (currently just tables, but perhaps other things in the future).
	:ivar TablesEndpoints tables:
	:ivar TileSetsEndpoints tile_sets: Tile sets are custom map layers composed of uploaded imagery, pre-sliced into slippy map tiles. If instead you want to import a GeoTiff file as an Image column in a MapLarge table, use the `/restapi/v1/accounts/{account}/tables/{name}` (CreateTable, etc.) endpoints instead.
	:ivar AichatEndpoints aichat: Provides access to AI chat workloads.
	:ivar AlertTriggersEndpoints alert_triggers: Alerts are events that trigger when a new table is created or data is added to an existing table
	:ivar BasemapEndpoints basemap: Retrieve tiles for MapLarge basemaps
	:ivar CatalogEndpoints catalog: Catalog of data sources (tables, layers, queries) available by standard services.
	:ivar ClusterEndpoints cluster: Manage cluster-based administrative operations.
	:ivar DatastreamEndpoints datastream: Manage re-usable resources for datastreams pipeline.
	:ivar DiagnosticsEndpoints diagnostics: Provides access to statistical information
	:ivar ImportsEndpoints imports: Manage long-running import processes.
	:ivar BandwidthLimitsEndpoints bandwidth_limits: Manage data synchronization between clusters of MapLarge server.
	:ivar ServersEndpoints servers: Manage data synchronization between clusters of MapLarge server.
	:ivar AccountPairsEndpoints account_pairs: Manage data synchronization between clusters of MapLarge server.
	:ivar TablePairsEndpoints table_pairs: Manage data synchronization between clusters of MapLarge server.
	:ivar LayersEndpoints layers: Create visualizations of geospatial data.
	:ivar NotebooksEndpoints notebooks: Provides access to notebooks
	:ivar OfframpsEndpoints offramps: Provides access to OffRamps which combine observers and pipelines.
	:ivar OnboardingEndpoints onboarding: Copy selected tables and tags to the local cluster from a remote database using various mechanisms (Network filesystem access, Intercluster data mover, etc.)
	:ivar OnrampsEndpoints onramps: Provides access to OnRamps which combine connectors and pipelines.
	:ivar OpsEndpoints ops: Provides access to ops functionality
	:ivar PackagesEndpoints packages: Request package export and installation
	:ivar PipelinesEndpoints pipelines: Provides access to pipelines which are used by ramps.
	:ivar QueriesEndpoints queries: Execute queries against the MapLarge database.
	:ivar SqlEndpoints sql: Execute SQL queries against the MapLarge database.
	:ivar TinyurlEndpoints tinyurl: Creates and retrieves short URL keys that redirect to full URLs.
	:ivar UsersEndpoints users: Manage the credentials that are used to authenticate with MapLarge.
	:ivar UserGroupsEndpoints user_groups: Manage which groups each user belongs to.
	:ivar VfsEndpoints vfs: Provides access to the Virtual File System
	:ivar WorkflowsEndpoints workflows: Manage alter trigger workflows.
	"""
	def __init__(self, url: str, username: str, password: str, min_remaining_life: float = 0.5):
		self.url = url
		self.username = username
		self.password = password
		self.min_remaining_life = min_remaining_life
		self._credentials = None # type: Optional[TokenCredentials]
		self._lifespan = None    # type: Optional[int]
		self._expires = None     # type: Optional[datetime]
		self._opener = build_opener(No303RedirectHandler, NoErrorHandler)
		self._path_regex = re.compile("\\{([^\\}]+)\\}")
		self.accounts = AccountsEndpoints(self)
		self.folders = FoldersEndpoints(self)
		self.groups = GroupsEndpoints(self)
		self.indexes = IndexesEndpoints(self)
		self.resources = ResourcesEndpoints(self)
		self.tables = TablesEndpoints(self)
		self.tile_sets = TileSetsEndpoints(self)
		self.aichat = AichatEndpoints(self)
		self.alert_triggers = AlertTriggersEndpoints(self)
		self.basemap = BasemapEndpoints(self)
		self.catalog = CatalogEndpoints(self)
		self.cluster = ClusterEndpoints(self)
		self.datastream = DatastreamEndpoints(self)
		self.diagnostics = DiagnosticsEndpoints(self)
		self.imports = ImportsEndpoints(self)
		self.bandwidth_limits = BandwidthLimitsEndpoints(self)
		self.servers = ServersEndpoints(self)
		self.account_pairs = AccountPairsEndpoints(self)
		self.table_pairs = TablePairsEndpoints(self)
		self.layers = LayersEndpoints(self)
		self.notebooks = NotebooksEndpoints(self)
		self.offramps = OfframpsEndpoints(self)
		self.onboarding = OnboardingEndpoints(self)
		self.onramps = OnrampsEndpoints(self)
		self.ops = OpsEndpoints(self)
		self.packages = PackagesEndpoints(self)
		self.pipelines = PipelinesEndpoints(self)
		self.queries = QueriesEndpoints(self)
		self.sql = SqlEndpoints(self)
		self.tinyurl = TinyurlEndpoints(self)
		self.users = UsersEndpoints(self)
		self.user_groups = UserGroupsEndpoints(self)
		self.vfs = VfsEndpoints(self)
		self.workflows = WorkflowsEndpoints(self)
	def credentials(self) -> Optional[TokenCredentials]:
		"""Return current credentials, fetching a new token if needed."""
		if not self.are_credentials_current():
			self.login()
		return self._credentials

	def are_credentials_current(self, min_remaining_life: Optional[float] = None) -> bool:
		"""Indicates whether the currently cached token still has enough remaining life."""
		if not self._credentials:
			return False
		assert isinstance(self._lifespan, int)
		assert isinstance(self._expires, datetime)
		remaining_life = timedelta(seconds = self._lifespan * (min_remaining_life or self.min_remaining_life))
		# utcnow is deprecated as of 3.12, but the new code to use `datetime.now(UTC)` doesn't work until 3.11, so we can't fix this until 2026-10 when 3.10 goes out of support.
		return (datetime.utcnow() + remaining_life) <= self._expires

	def login(self, username: Optional[str] = None, password: Optional[str] = None) -> Optional[TokenCredentials]:
		"""Validates the configured credentials and caches the resulting authentication token."""
		if username is not None and self.username != username:
			self.username = username
			self.clear_credentials()
		if password is not None and self.password != password:
			self.password = password
			self.clear_credentials()

		if not self.username or not self.password:
			self.clear_credentials()
			return None

		headers = { "mluser": self.username }
		if self.are_credentials_current(self.min_remaining_life / 2):
			assert isinstance(self._credentials, TokenCredentials)
			headers["mltoken"] = self._credentials.token
		else:
			headers["mlpass"] = self.password

		request = Request(url=self.url + "/Auth/Login", headers=headers, method=HttpMethod.POST.value)
		with self._opener.open(request) as response:
			try:
				response_text = response.read()
			except: # pylint: disable=bare-except
				response_text = None
			response_json = None
			if response_text:
				try:
					response_json = json.loads(response_text)
				except: # pylint: disable=bare-except
					pass
			if response.status < 200 or response.status >= 300 or not response_json or not response_json.get("success"):
				raise AuthenticationError(request.full_url, response.status, response.headers, response_text)
			lifespan = cast(int, response_json["expiresInSeconds"])
			self._lifespan = lifespan
			# utcnow is deprecated as of 3.12, but the new code to use `datetime.now(UTC)` doesn't work until 3.11, so we can't fix this until 2026-10 when 3.10 goes out of support.
			self._expires = datetime.utcnow() + timedelta(seconds=lifespan)
			self._credentials = TokenCredentials(response_json["user"], response_json["token"])
			return self._credentials

	def clear_credentials(self) -> None:
		"""Forget the currently cached token."""
		self._credentials = None
		self._lifespan = None
		self._expires = None

	def _send_request(self,
		path: str,
		method: HttpMethod,
		parameters: Mapping[str, RestParameter],
		request_body: RequestBodyType,
		response_body: ResponseBodyType,
		request: Mapping[str, Any],
		result_type: Optional[Union[str, Type[Any]]],
		item_type: Optional[Union[str, Type[Any]]] = None,
		timeout: Optional[float] = None
	) -> Any:
		"""Send a Rest API request to the server."""

		def success(status: int) -> bool:
			return 200 <= status < 300 or status == 303

		headers = {} # type: Dict[str, str]
		body = None # type: Optional[bytes]

		header_params = [x for x, y in ((key, (parameters.get(key) or DEFAULT_PARAM)) for key in request.keys()) if y['in'] is ParameterLocation.HEADER]
		for key in header_params:
			value = request[key]
			if value is not None and value != '':
				headers[key] = request[key]
		credentials = self.credentials()
		if credentials is not None:
			headers['mluser'] = credentials.name
			if isinstance(credentials, TokenCredentials) and credentials.token is not None:
				headers['mltoken'] = credentials.token
			elif isinstance(credentials, PasswordCredentials) and credentials.password is not None: # pylint: disable=no-member
				headers['mlpass'] = credentials.password # pylint: disable=no-member
		if request.get('body') is not None:
			content_type, body = RestClient._prepare_body(request_body, request["body"])
			headers['Content-Type'] = content_type

		path = self._get_url(
			path=path,
			parameters=parameters,
			request=request
		)

		# print(f'DEBUG: requesting {path}')
		req = Request(url=path, data=body, headers=headers, method=method.value)
		response = self._opener.open(req, timeout=timeout) if timeout is not None else self._opener.open(req)
		if response_body == ResponseBodyType.BINARY and success(response.status):
			content_disposition = response.headers.get('Content-Disposition')
			filename = ''
			if content_disposition and content_disposition.startswith('attachment'):
				parts = content_disposition.split(';')
				for part in parts:
					stripped = part.strip()
					if stripped.startswith('filename='):
						filename = stripped[9:]
						break
			return File(response, filename, response.headers.get('Content-Type'))
		with response:
			if method is HttpMethod.HEAD:
				if success(response.status):
					return True
				if response.status == 404:
					return False
			if not success(response.status):
				try:
					response_text = response.read()
				except: # pylint: disable=bare-except
					response_text = None
				if response.status == 400:
					raise RestValidationError(req.full_url, response.status, response.headers, response_text)
				raise RestError(req.full_url, response.status, response.headers, response_text)
			if response.status == 204:
				return None
			response_text = response.read()
			parsed = json.loads(response_text)
			# self_href = ('_links' in parsed and 'self' in parsed['_links'] and 'href' in parsed['_links']['self'] or None) and parsed['_links']['self']['href']
			# print(f'DEBUG: _links.self.href: {self_href}')
			return unjsonify(parsed, result_type, item_type)

	@staticmethod
	def _prepare_body(request_body_type: RequestBodyType, request_body: Any) -> Tuple[str, bytes]:
		"""Prepares the request body bytes and determines the content type."""
		content_type = None # type: Optional[str]
		body_bytes = None # type: Optional[bytes]
		if request_body_type is RequestBodyType.JSON:
			jsonified_body = cast(Mapping[str, Any], jsonify(request_body))
			content_type = 'application/json'
			body_bytes = json.dumps(jsonified_body, sort_keys=True, separators=(',', ':')).encode("utf-8")
		elif request_body_type is RequestBodyType.MULTI_PART_FORM_DATA:
			jsonified_body = cast(Mapping[str, Any], jsonify(request_body))
			form_data = MultiPartFormData()
			def append_form_data(key: str, value: Any) -> None:
				if value is None:
					return
				if isinstance(value, str):
					if value != '':
						form_data.add_field(key, value)
				elif isinstance(value, File):
					form_data.add_file(key, value)
				elif isinstance(value, IO):
					form_data.add_file(key, File(value, "upload"))
				elif isinstance(value, (int, float, bool)):
					form_data.add_field(key, str(value))
				else:
					form_data.add_field(key, json.dumps(value))
			for key, value in jsonified_body.items():
				if isinstance(value, Iterable) and not isinstance(value, (str, dict)):
					# In multi part form data, lists are sent as multiple occurrances of the same field.
					for element in value:
						append_form_data(key, element)
				else:
					append_form_data(key, value)
			content_type = form_data.get_content_type()
			body_bytes = bytes(form_data)
		elif request_body_type is RequestBodyType.BINARY:
			content_type = 'application/octet-stream'
			value = request_body
			if isinstance(value, bytes):
				body_bytes = value
			else:
				body_bytes = value.read()
		else:
			raise ValueError('unrecognized request body type: ' + str(request_body_type))
		return (content_type, cast(bytes, body_bytes))

	def _get_url(self,
		path: str,
		parameters: Mapping[str, RestParameter],
		request: Mapping[str, Any]
	) -> str:
		"""Get the URL for a Rest API request."""
		if request is None:
			request = {}

		path_template = path
		query_params = dict(request)

		keys = self._path_regex.findall(path_template)
		for key in keys:
			value = jsonify(request.get(key))
			if value is None or value == '':
				raise ValueError(f'{path} requires a {key} parameter which was not provided.')
			if isinstance(value, list):
				value = quote(",".join(value))
			else:
				value = quote(str(value))
			path = path.replace('{' + key + '}', value)

			del query_params[key]
		query_pairs = [] # type: List[str]
		for key, value in query_params.items():
			param = parameters.get(key)
			if param is None:
				param = DEFAULT_PARAM
			if param['in'] is not ParameterLocation.QUERY or value is None or value == '':
				continue
			value = jsonify(value)
			if isinstance(value, list):
				if param['explode']:
					for element in value:
						if element is not None and element != '':
							query_pairs.append(f'{quote(key)}={quote(str(element))}')
				else:
					query_pairs.append(f'{quote(key)}={",".join([quote(x) if x is not None else "" for x in value])}')
			elif isinstance(value, dict):
				for child_key, element in value.items():
					if element is not None and element != '':
						query_pairs.append(f'{quote(child_key)}={quote(str(element))}')
			else:
				query_pairs.append(f'{quote(key)}={quote(str(value))}')
		if query_pairs:
			path = path + '?' + '&'.join(query_pairs)
		if '/restapi/v1' not in path:
			path = '/restapi/v1' + path
		if not path.startswith('http'):
			if self.url.endswith('/'):
				path = self.url[:-1] + path
			else:
				path = self.url + path
		return path

	def follow_items(self, obj: RestList[DataT]) -> List[DataT]:
		"""
		`maplargerest.items` is a simpler alternative.
		
		Follow a JSON HAL "items" link to retrieve the items contained in a RestList. Usually
		"items" is embedded, so this call should return immediately without sending a web request.
		"""
		return items(obj)

	def follow_next(self, obj: Page[DataT], *, item_type: Union[str, Type[DataT]], timeout: Optional[float] = None) -> Page[DataT]:
		"""
		Follow a JSON HAL "next" link, returning the next page of data.

		:param item_type: The type of item contained in the list.
		"""
		return cast(Page[DataT], self.follow(obj, 'next', result_type="Page", item_type=item_type, timeout=timeout))

	def follow_prev(self, obj: Page[DataT], *, item_type: Union[str, Type[DataT]], timeout: Optional[float] = None) -> Page[DataT]:
		"""
		Follow a JSON HAL "prev" link, returning the previous page of data.

		:param item_type: The type of item contained in the list.
		"""
		return cast(Page[DataT], self.follow(obj, 'prev', result_type="Page", item_type=item_type, timeout=timeout))

	def follow_self(self, obj: ResourceT, *, result_type: Union[str, Type[ResourceT]], item_type: Optional[Union[str, Type[Any]]] = None, force: bool = False, timeout: Optional[float] = None) -> ResourceT:
		"""
		Follow a JSON HAL "self" link, echoing back the original object.

		:param force: Instead of echoing back the original object, send a web request to fetch a fresh copy of the object.
		"""
		return cast(ResourceT, self.follow(obj, 'self', result_type=result_type, item_type=item_type, force=force, timeout=timeout))

	def follow(self, obj: Any, link: str, *,
		result_type: Optional[Union[str, Type[Any]]] = None,
		item_type: Optional[Union[str, Type[Any]]] = None,
		response_body: Optional[ResponseBodyType] = None,
		request: Optional[Mapping[str, Any]] = None,
		force: bool = False,
		status_update: Optional[Callable[[Import], None]] = None,
		timeout: Optional[float] = None
	) -> Any:
		"""
		Follow a JSON HAL link or return the already embedded link if available.

		:param result_type: The type of object to be returned.
		:param item_type: The type of item contained in the list or the generic type argument.
		:param response_body: Either 'JSON' or 'BINARY'.
		:param request: Parameters to use in the placeholders of a templated link. See https://tools.ietf.org/html/draft-kelly-json-hal-08#section-5.2
		:param force: For a "self" link, fetch a fresh copy of the object instead of echoing back the original.
		:param status_update: For a "result" link, a callback function that can receive status updates.
		"""

		ml_server_fwd = None # type: Optional[str]

		def append_query(path: str, key: str, value: str) -> str:
			if "?" in path:
				return f"{path}&{quote(key)}={quote(value)}"
			return f"{path}?{quote(key)}={quote(value)}"

		def send_request(link_key: str, link_value: Link) -> Any:
			# print(f'DEBUG: fetching link {link_key}')
			if link_key in ('self', 'next', 'prev'):
				checked_result_type = type(obj)
			elif isinstance(result_type, type):
				checked_result_type = result_type
			else:
				checked_result_type = None
			path = link_value.href
			if link_key == "self" and "/imports/" in path:
				if "noRedirect" not in path:
					path = append_query(path, "noRedirect", "true")
				if ml_server_fwd and "mlServerFwd" not in path:
					path = append_query(path, "mlServerFwd", ml_server_fwd)
			return self._send_request(
				path=path,
				method=HttpMethod.GET,
				response_body=response_body or ResponseBodyType.JSON,
				parameters={},
				request_body=RequestBodyType.NONE,
				request=request if request is not None else {},
				result_type=checked_result_type,
				item_type=item_type,
				timeout=timeout
			)

		def get_container(container_key: str) -> Any:
			if hasattr(obj, container_key):
				container_value = getattr(obj, container_key)
				if container_value:
					return container_value
			if hasattr(obj, "_" + container_key):
				container_value = getattr(obj, "_" + container_key)
				if container_value:
					return container_value
			return None

		def get_link(container: Any, link_key: str) -> Any:
			if hasattr(container, link_key):
				link_value = getattr(container, link_key)
				if link_value:
					return link_value
			if hasattr(container, link_key + "_"):
				link_value = getattr(container, link_key + "_")
				if link_value:
					return link_value
			return None

		def force_fetch_self() -> Any:
			link_value = get_link(get_container("links"), "self")
			return send_request("self", link_value)

		def check_links() -> Any:
			embedded = get_container("embedded")
			if embedded:
				link_value = get_link(embedded, link)
				if link_value:
					return link_value
			links = get_container("links")
			if links:
				link_value = get_link(links, link)
				if link_value:
					return send_request(link, link_value)
			return None

		def get_preferred_host() -> Optional[str]:
			links = get_container("links")
			if links:
				link_value = get_link(links, "self")
				if link_value:
					qs = parse_qs(urlparse(link_value.href).query)
					value = qs.get('mlServerFwd')
					if value:
						return value[0]
			return None

		if link == 'self':
			return force_fetch_self() if force else obj
		value = check_links()
		if value:
			return value
		if link == "result" and isinstance(obj, Import):
			ml_server_fwd = get_preferred_host()
			while True:
				sleep(0.5)
				obj = force_fetch_self()
				if status_update:
					status_update(obj)
				value = check_links()
				if value:
					return value

		return None

def items(obj: RestList[DataT]) -> List[DataT]:
	"""Return the items contained in a RestList."""
	return obj._embedded.items # pylint: disable=protected-access

def hash_request(obj: Any) -> str:
	"""Return a stable MD5 hash of the request object."""
	jsonified = jsonify(obj)
	json_str = json.dumps(jsonified, sort_keys=True, separators=(',', ':'))
	json_bytes = json_str.encode("utf-8")
	hash_ = md5(json_bytes)
	return hash_.hexdigest()
class RestError(Exception, ProblemDetails): # pylint: disable=too-many-ancestors
	"""An HTTP error returned from the MapLarge Rest API."""
	def __init__(self, url: str, status: int, headers: Mapping[str, str], body_text: Optional[bytes], type_: Optional[Type[ProblemDetails]] = ProblemDetails) -> None:
		self.url = url
		self.status = status
		self.headers = headers
		self.body_text = body_text
		self.body_json = None
		self.body_parsed = False
		message = None # type: Optional[str]
		if body_text:
			try:
				self.body_json = json.loads(body_text)
				if isinstance(self.body_json, dict):
					kwargs, extra_data = get_init_args(self.body_json, type_)
					type_.__init__(self, **kwargs) # type: ignore[misc] # pylint: disable=missing-kwoa
					for k,v in extra_data.items():
						setattr(self, k, v)
					self.body_parsed = True
					message = self.detail
			except: # pylint: disable=bare-except
				pass
			if not message:
				if isinstance(body_text, bytes):
					try:
						content_type = headers.get("Content-Type")
						charset = "utf-8"
						if content_type:
							parts = content_type.split(';')
							for part in parts:
								trimmed = part.strip()
								if trimmed.startswith("charset"):
									charset = trimmed.split("=")[1]
									break
						message = body_text.decode(charset)
					except: # pylint: disable=bare-except
						pass
		if not message:
			message = f'MapLarge Rest Api Error: {status}'
		Exception.__init__(self, message)

class RestValidationError(RestError, ValidationProblemDetails): # pylint: disable=too-many-ancestors
	"""An HTTP status 400 error returned from the MapLarge Rest API indicating a validation error."""
	def __init__(self, url: str, status: int, headers: Mapping[str, str], body_text: Optional[bytes]) -> None: # pylint: disable=super-init-not-called
		RestError.__init__(self, url, status, headers, body_text, ValidationProblemDetails)

class AuthenticationError(Exception): # pylint: disable=too-many-ancestors
	"""An error that occurred while authenticating with the MapLarge server."""
	def __init__(self, url: str, status: int, headers: Mapping[str, str], body_text: Optional[bytes]) -> None:
		self.url = url
		self.status = status
		self.headers = headers
		self.body_text = body_text
		self.body_json = None

		if body_text:
			try:
				self.body_json = json.loads(body_text)
			except: # pylint: disable=bare-except
				pass
		errors = self.body_json and self.body_json.get("errors")
		message = None # type: Optional[str]
		if errors and errors[0]:
			message = errors[0]
		elif isinstance(body_text, bytes):
			try:
				content_type = headers.get("Content-Type")
				charset = "utf-8"
				if content_type:
					parts = content_type.split(';')
					for part in parts:
						trimmed = part.strip()
						if trimmed.startswith("charset"):
							charset = trimmed.split("=")[1]
							break
				message = body_text.decode(charset)
			except: # pylint: disable=bare-except
				pass
		if not message:
			message = "MapLarge authentication failed."

		Exception.__init__(self, message)
def discriminate(type_: str, item_type: Optional[Union[str, Type[Any]]], value: Any, context: Deque[str]) -> Tuple[Optional[Type[Any]], Optional[Union[str, Type[Any]]]]:
	"""Resolve a polymorphic type."""
	if type_ == "ResourceReferenceBase":
		item_type = value["itemType"]
		if item_type == "folder":
			return maplargerest.models.ResourceFolderReference, None
		if item_type == "resource":
			return maplargerest.models.ResourceReference, None
	if type_ == "ResourceBase":
		item_type = value["itemType"]
		if item_type == "folder":
			return maplargerest.models.ResourceFolder, None
		if item_type == "resource":
			return maplargerest.models.Resource, None
	if type_ == "QueryWhere":
		if isinstance(value, Iterable):
			return list, "QueryWhereAnd"
		if "expression" in value:
			return maplargerest.models.QueryWhereExpression, None
		if "test" in value:
			return maplargerest.models.QueryWhereTest, None
		raise ValueError(f"Expected a list (representing an 'or' clause), a dictionary with an 'expression', or a dictionary with a 'test'. Context: {''.join(context)}")
	if type_ == "QueryWhereAnd":
		return list, "QueryWhereAndElement"
	if type_ == "QueryWhereAndElement":
		if "expression" in value:
			return maplargerest.models.QueryWhereExpression, None
		if "test" in value:
			return maplargerest.models.QueryWhereTest, None
		raise ValueError(f"Expected a list (representing an 'or' clause), a dictionary with an 'expression', or a dictionary with a 'test'. Context: {''.join(context)}")
	if type_ == "QueryWhereValue":
		if isinstance(value, (str, int, float, datetime)):
			return type(value), None
		if isinstance(value, Iterable):
			return list, "QueryWhereValueArrayElement"
		if "query" in value:
			return maplargerest.models.QueryWhereValueQuery, None
		if "min" in value:
			return maplargerest.models.QueryWhereValueMinMax, None
		raise ValueError(f"Expected a literal value, a list of literals, a dictionary with a 'query', or a dictionary with a 'min' and 'max'. Context: {''.join(context)}")
	if type_ == "QueryWhereValueArrayElement":
		if isinstance(value, (str, int, float, datetime)):
			return type(value), None
		if "min" in value:
			return maplargerest.models.QueryWhereValueMinMax, None
		raise ValueError(f"Expected a literal value, or a dictionary with a 'min' and 'max'. Context: {''.join(context)}")
	if type_ == "RestListBase":
		if "size" in value:
			return maplargerest.models.Page, item_type
		return maplargerest.models.RestList, item_type
	return None, None
