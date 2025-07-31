"""Unit tests for serialization-related classes and methods, such as jsonify."""

from io import BytesIO
from json import dumps
import unittest

from maplargerest.endpoints import RequestBodyType, RestClient, jsonify, unjsonify
from maplargerest.models import (
	Account, AccountLinks, CreateAccountRequest, CreateTableFromFileUploadRequest, File,
	FileImportOptions, Link, Query, QueryTable, QueryWhereTest, Resource, ResourceBase,
	ResourceFolder, ResourceFolderContents, RestList, TestSymbol, UserReference
)
# pylint: disable=wrong-import-order

class TestJsonify(unittest.TestCase):
	"""Tests for the jsonify method, which prepares model objects for JSON serialization."""

	def test_jsonify_create_account_request(self) -> None:
		"""Verify whether a simple object like CreateAccountRequest can be serialized."""
		account = CreateAccountRequest(
			code="theaccount",
			name="The Account",
			description="Test account",
			estimated_size_limit=100,
			max_row_limit=1000,
			use_resource_permissions=True
		)
		result = jsonify(account)
		self.assertIsInstance(result, dict)
		self.assertEqual(result["code"], "theaccount")
		self.assertEqual(result["name"], "The Account")
		self.assertEqual(result["description"], "Test account")
		self.assertEqual(result["estimatedSizeLimit"], 100)
		self.assertEqual(result["maxRowLimit"], 1000)
		self.assertEqual(result["useResourcePermissions"], True)
		json_result = dumps(result)
		self.assertEqual(json_result, '{"code": "theaccount", "description": "Test account", "estimatedSizeLimit": 100, "maxRowLimit": 1000, "name": "The Account", "useResourcePermissions": true}')

	def test_jsonify_query(self) -> None:
		"""Verify whether a more complex object like Query can be serialized."""
		query = Query(
			table=QueryTable(name="hms/hotels"),
			where=[[QueryWhereTest(column="HotelName", test=TestSymbol.EQUAL, value="B")]]
		)
		result = jsonify(query)
		self.assertIsInstance(result, dict)
		self.assertIsInstance(result["table"], dict)
		self.assertEqual(result["table"]["name"], "hms/hotels")
		self.assertIsInstance(result["where"], list)
		self.assertIsInstance(result["where"][0], list)
		self.assertIsInstance(result["where"][0][0], dict)
		self.assertEqual(result["where"][0][0]["column"], "HotelName")
		self.assertEqual(result["where"][0][0]["test"], "Equal")
		self.assertEqual(result["where"][0][0]["value"], "B")

class TestUnjsonify(unittest.TestCase):
	"""Tests for the unjsonify method, which prepares converts deserialized JSON into model objects."""

	def test_unjsonify_account(self) -> None:
		"""Verify whether a simple object like Account can be deserialized."""
		account = {
			"id": 1234,
			"code": "testaccount",
			"name": "Test Account",
			"description": "A test account",
			"useResourcePermissions": True,
			"totalEstimatedSize": 100,
			"estimatedSizeLimit": 200,
			"maxRowLimit": 1000,
			"owner": {
				"id": 4321,
				"email": "user@example.com"
			},
			"_links": {
				"self": { "href": "/restapi/v1/accounts/testaccount" },
				"owner": { "href": "/restapi/v1/users/4321" },
				"groups": { "href": "/restapi/v1/accounts/testaccount/groups" },
				"tables": { "href": "/restapi/v1/accounts/testaccount/tables" },
				"rootResourceFolder": { "href": "/restapi/v1/accounts/testaccount/folders?idOrPath=%2f" },
				"tileSets": { "href": "/restapi/v1/accounts/testaccount/tilesets" },
			}
		}
		result: Account = unjsonify(account, "Account")
		self.assertIsInstance(result, Account)
		self.assertEqual(result.id_, 1234)
		self.assertEqual(result.code, "testaccount")
		self.assertEqual(result.name, "Test Account")
		self.assertEqual(result.description, "A test account")
		self.assertEqual(result.use_resource_permissions, True)
		self.assertEqual(result.total_estimated_size, 100)
		self.assertEqual(result.estimated_size_limit, 200)
		assert isinstance(result.owner, UserReference)
		self.assertEqual(result.owner.id_, 4321)
		self.assertEqual(result.owner.email, "user@example.com")
		self.assertIsInstance(result.links, AccountLinks)
		self.assertIsInstance(result.links.self_, Link)
		self.assertEqual(result.links.self_.href, "/restapi/v1/accounts/testaccount")
		assert isinstance(result.links.owner, Link)
		self.assertEqual(result.links.owner.href, "/restapi/v1/users/4321")

	def test_unjsonify_rest_list(self) -> None:
		"""Verify whether a slightly complex object like RestList[Account] can be deserialized."""
		rest_list = {
			"count": 2,
			"_embedded": {
				"items": [
					{
						"id": 1234,
						"code": "testaccount",
						"name": "Test Account",
						"description": "A test account",
						"useResourcePermissions": True,
						"totalEstimatedSize": 100,
						"estimatedSizeLimit": 200,
						"maxRowLimit": 1000,
						"owner": {
							"id": 4321,
							"email": "user@example.com"
						},
						"_links": {
							"self": { "href": "/restapi/v1/accounts/testaccount" },
							"owner": { "href": "/restapi/v1/users/4321" },
							"groups": { "href": "/restapi/v1/accounts/testaccount/groups" },
							"tables": { "href": "/restapi/v1/accounts/testaccount/tables" },
							"rootResourceFolder": { "href": "/restapi/v1/accounts/testaccount/folders?idOrPath=%2f" },
							"tileSets": { "href": "/restapi/v1/accounts/testaccount/tilesets" },
						}
					},
					{
						"id": 5678,
						"code": "account2",
						"name": "Test Account 2",
						"description": "Another test account",
						"useResourcePermissions": False,
						"totalEstimatedSize": 1,
						"estimatedSizeLimit": 2,
						"maxRowLimit": 10,
						"owner": {
							"id": 9876,
							"email": "user2@example.com"
						},
						"_links": {
							"self": { "href": "/restapi/v1/accounts/account2" },
							"owner": { "href": "/restapi/v1/users/9876" },
							"groups": { "href": "/restapi/v1/accounts/account2/groups" },
							"tables": { "href": "/restapi/v1/accounts/account2/tables" },
							"rootResourceFolder": { "href": "/restapi/v1/accounts/account2/folders?idOrPath=%2f" },
							"tileSets": { "href": "/restapi/v1/accounts/account2/tilesets" },
						}
					}
				]
			},
			"_links": {
				"self": { "href": "/restapi/v1/accounts" }
			}
		}
		result: RestList[Account] = unjsonify(rest_list, "RestList", "Account")
		self.assertIsInstance(result, RestList)
		self.assertEqual(result.count, 2)
		self.assertIsInstance(result.embedded.items, list)
		self.assertIsInstance(result.embedded.items[0], Account)
		self.assertEqual(result.embedded.items[0].id_, 1234)
		self.assertEqual(result.embedded.items[1].id_, 5678)

	def test_unjsonify_folder(self) -> None:
		"""Verify whether an object with polymorphic children like ResourceFolder can be deserialized."""
		account = {
			"id": 2345,
			"code": "test"
		}
		folder = {
			"id": 1234,
			"account": account,
			"itemType": "folder",
			"name": None,
			"description": "root folder",
			"path": "/",
			"inheritPermissions": False,
			"permissions": [
				{
					"id": "3456",
					"group": {
						"id": 4567,
						"account": account,
						"name": "viewers"
					},
					"user": None,
					"permissions": [ "Read" ],
					"isExplicit": True,
					"effect": "Allow"
				}
			],
			"contents": [
				{
					"account": account,
					"id": 5678,
					"urn": "maplarge://test/table/mytable",
					"itemType": "resource"
				},
				{
					"account": account,
					"id": 6789,
					"path": "/subfolder",
					"itemType": "folder"
				}
			],
			"parent": None,
			"_links": {
				"self": { "href": "/restapi/v1/accounts/test/folders?idOrPath=%2f" },
				"account": { "href": "/restapi/v1/accounts/test" }
			},
			"_embedded": {
				"contents": {
					"count": 2,
					"_embedded": {
						"items": [
							{
								"account": account,
								"id": 5678,
								"urn": "maplarge://test/table/mytable",
								"itemType": "resource",
								"type": "Table",
								"name": "mytable",
								"description": "A table",
								"path": "/mytable",
								"inheritPermissions": True,
								"parent": {
									"id": 1234,
									"account": account,
									"itemType": "folder",
									"path": "/",
								},
								"_links": {
									"self": { "href": "/restapi/v1/accounts/test/resources?idOrUrn=5678" },
									"account": { "href": "/restapi/v1/accounts/test" },
								}
							},
							{
								"account": account,
								"id": 6789,
								"path": "/subfolder",
								"itemType": "folder",
								"description": "A sub-folder",
								"inheritPermissions": True,
								"parent": {
									"id": 1234,
									"account": account,
									"itemType": "folder",
									"path": "/",
								},
								"_links": {
									"self": { "href": "/restapi/v1/accounts/test/folders?idOrPath=%2fsubfolder" },
									"account": { "href": "/restapi/v1/accounts/test" },
									"contents": { "href": "/restapi/v1/accounts/test/folders/contents?idOrPath=%2fsubfolder" }
								}
							}
						]
					},
					"_links": {
						"self": { "href": "/restapi/v1/accounts/test/folders/contents?idOrPath=%2f" }
					}
				}
			}
		}
		result: ResourceFolder = unjsonify(folder, "ResourceFolder")
		assert isinstance(result.embedded, ResourceFolderContents)
		assert isinstance(result.embedded.contents, RestList)
		self.assertIsInstance(result.embedded.contents.embedded.items[0], Resource)
		self.assertIsInstance(result.embedded.contents.embedded.items[1], ResourceFolder)

	def test_unjsonify_query(self) -> None:
		"""Verify whether a very complex object like Query can be deserialized."""
		query = {
			"table": {
				"name": "hms/hotels"
			},
			"where": [[{"column": "HotelName", "test": "StartsWith", "value": "B" }]]
		}
		result = unjsonify(query, Query)
		self.assertIsInstance(result, Query)
		self.assertIsInstance(result.where, list)
		self.assertIsInstance(result.where[0], list)
		self.assertIsInstance(result.where[0][0], QueryWhereTest)
		self.assertEqual(result.where[0][0].column, "HotelName")
		self.assertEqual(result.where[0][0].test, TestSymbol.STARTS_WITH)
		self.assertEqual(result.where[0][0].value, "B")

class TestPrepareBody(unittest.TestCase):
	"""Tests for RestClient._prepare_body."""

	def test_prepare_body_file_import_options(self) -> None:
		"""Object properties should be allowed to be passed as strongly typed objects, and will be serialized as JSON."""
		request = CreateTableFromFileUploadRequest(
			options=FileImportOptions(
				well_known_pipeline_name="Spoofing",
				pipeline_start_step="ParseIt",
				pipeline_parameters={
					"SPOOF_ACCT": "test",
					"SPOOF_TBL": "spoof_pipeline1"
				}
			)
		)

		# pylint: disable=protected-access
		content_type, result = RestClient._prepare_body(RequestBodyType.MULTI_PART_FORM_DATA, request)

		str_result = result.decode('utf-8')
		self.assertIn("multipart/form-data;", content_type)
		self.assertIn('"wellKnownPipelineName": "Spoofing"', str_result)

	def test_prepare_body_json_options(self) -> None:
		"""Object properties should be allowed to be passed as python dicts and lists, and will be serialized as JSON."""
		request = CreateTableFromFileUploadRequest(
			options={
				"wellKnownPipelineName": "Spoofing",
				"pipelineStartStep": "ParseIt",
				"pipelineParameters": {
					"SPOOF_ACCT": "test",
					"SPOOF_TBL": "spoof_pipeline1"
				}
			}
		)

		# pylint: disable=protected-access
		content_type, result = RestClient._prepare_body(RequestBodyType.MULTI_PART_FORM_DATA, request)

		str_result = result.decode('utf-8')
		self.assertIn("multipart/form-data;", content_type)
		self.assertIn('"wellKnownPipelineName": "Spoofing"', str_result)

	def test_prepare_body_one_file(self) -> None:
		"""List properties should be prepared to accept a single value outside of a list."""
		file_bytes = BytesIO("It is a file!".encode())
		request = CreateTableFromFileUploadRequest(
			files=File(file_bytes, "upload")
		)

		# pylint: disable=protected-access
		content_type, result = RestClient._prepare_body(RequestBodyType.MULTI_PART_FORM_DATA, request)

		str_result = result.decode('utf-8')
		self.assertIn("multipart/form-data;", content_type)
		self.assertIn('Content-Disposition: form-data; name="files"; filename="upload"\r\nContent-Type: application/octet-stream\r\n\r\nIt is a file!', str_result)

	def test_prepare_body_multiple_files(self) -> None:
		"""Each value of a list property should be sent as another instance of the field."""
		file1_bytes = BytesIO("It is a file!".encode())
		file2_bytes = BytesIO("It is another file!".encode())
		request = CreateTableFromFileUploadRequest(
			files=[File(file1_bytes, "upload"),File(file2_bytes, "upload")]
		)

		# pylint: disable=protected-access
		content_type, result = RestClient._prepare_body(RequestBodyType.MULTI_PART_FORM_DATA, request)

		str_result = result.decode('utf-8')
		self.assertIn("multipart/form-data;", content_type)
		self.assertIn('Content-Disposition: form-data; name="files"; filename="upload"\r\nContent-Type: application/octet-stream\r\n\r\nIt is a file!', str_result)
		self.assertIn('Content-Disposition: form-data; name="files"; filename="upload"\r\nContent-Type: application/octet-stream\r\n\r\nIt is another file!', str_result)
