"""Tests of the table endpoints of the Rest API."""

import json
from   os.path           import join
from   typing            import Dict, Optional, Any

from maplargerest.endpoints import RestClient, RestError, items
from maplargerest.models import (
	ColumnType, CreateTableFromFileUploadRequest, CreateTableRequest, File, FileImportOptions,
	Import, Query, QueryTable, RestList, TableVersion, TableVersionActive, TableVisibility,
	TablesVersionsExportAcceptType
)
# pylint: disable=wrong-import-order
from test.shared_test import ClientTest

TABLE_ACCOUNT = "test"
TABLE_NAME = "wktpoint"
TABLE_FILE_URL = "https://s3-cdn.dev.maplarge.net/maplarge-public/UnitTests/Imports/WKTPoint.csv"
TABLE_FILE_LOCAL = "WKTPoint.csv"
TABLE_JSON_FILE_LOCAL = "WKTPoint.json"

_m: Dict[str, Optional[str]] = {
	'prev_message': None
}
def clear_progress() -> None:
	"""Erase the previous import progress."""
	_m['prev_message'] = None

def print_progress(imp: Import) -> None:
	"""Display the import progress."""
	if _m['prev_message'] != imp.message:
		print(imp.message)
		_m['prev_message'] = imp.message

def create_table(client: RestClient) -> Any:
	"""Create a table for testing."""
	import_ = client.tables.post(
		account=TABLE_ACCOUNT,
		name=TABLE_NAME,
		body=CreateTableRequest(
			file_url=TABLE_FILE_URL))
	clear_progress()
	print_progress(import_)
	tables = items(client.follow(import_, "result",
		result_type=RestList,
		item_type=TableVersion,
		status_update=print_progress))
	return tables[0]

def cleanup_table(client: RestClient, table_name: str = TABLE_NAME) -> None:
	"""Delete the table used for testing."""
	try:
		client.tables.delete(account=TABLE_ACCOUNT, name=table_name)
	except RestError as ex:
		if ex.status != 404:
			raise

class TestTables(ClientTest):
	"""Tests of the table endpoints of the Rest API."""

	def setUp(self) -> None:
		"""Set up before each test."""
		super().setUp()
		self.import_test_data(['hms/hotels'])
		cleanup_table(self.client)

	def assert_table_version(self, table: TableVersion) -> None:
		"""Assert that the object returned from the Rest API is a properly instantiated TableVersion object."""
		self.assertIsInstance(table, TableVersion)
		self.assertEqual(table.account.code, TABLE_ACCOUNT)
		self.assertEqual(table.name, TABLE_NAME)
		self.assertIsInstance(table.visibility, TableVisibility)
		self.assertIsInstance(table.columns, list)
		self.assertIsInstance(table.columns[0].name, str)
		self.assertIsInstance(table.columns[0].type_, (str, ColumnType))

	def assert_table_version_active(self, table_active: TableVersionActive) -> None:
		"""Assert that the object returned from the Rest API is a properly instantiated TableVersionActive object."""
		self.assertIsInstance(table_active, TableVersionActive)
		self.assertIsNotNone(table_active.active_version.id_)
		parts = str(table_active.active_version.id_).split("/")
		self.assertGreaterEqual(len(parts), 3)
		self.assertEqual(table_active.active_version.account.code, TABLE_ACCOUNT)
		self.assertEqual(table_active.active_version.name, TABLE_NAME)
		self.assertIsNotNone(table_active.active_version.version)
		self.assertGreaterEqual(int(table_active.active_version.version), 0)

	def assert_table_create(self, table: Any) -> None:
		"""Assert that the table returned from the Rest API is a properly created."""
		self.assertEqual(table.id_, f"{TABLE_ACCOUNT}/{TABLE_NAME}/{table.version}")
		self.assertIsInstance(table.row_count, int)

	def test_get_table_version(self) -> None:
		"""Verify that GET /accounts/{account}/tables/{name}/versions/{version} successfully returns a single table version."""
		try:
			create_table(self.client)
			table = self.client.tables.versions.get(account=TABLE_ACCOUNT, name=TABLE_NAME, version="latest")
			self.assert_table_version(table)
		finally:
			cleanup_table(self.client)

	def test_list_tables(self) -> None:
		"""Verify that GET /accounts/{account}/tables successfully returns a list of tables."""
		try:
			create_table(self.client)
			tables = items(self.client.tables.list(account=TABLE_ACCOUNT))
			self.assertGreaterEqual(len(tables), 1)
			self.assertTrue(any(t for t in tables if t.account.code == TABLE_ACCOUNT and t.name == TABLE_NAME))
			table = [t for t in tables if t.account.code == TABLE_ACCOUNT and t.name == TABLE_NAME][0]
			self.assert_table_version(table)
		finally:
			cleanup_table(self.client)

	def test_get_table(self) -> None:
		"""Verify that GET /accounts/{account}/tables/{name} successfully returns a single table."""
		try:
			create_table(self.client)
			table = self.client.tables.get(account=TABLE_ACCOUNT, name=TABLE_NAME)
			self.assert_table_version(table)
		finally:
			cleanup_table(self.client)

	def test_get_table_version_active(self) -> None:
		"""Verify that GET /accounts/{account}/tables/{name}/versions/active successfully returns a single table version."""
		try:
			create_table(self.client)
			table_active = self.client.tables.versions.active(account=TABLE_ACCOUNT, name=TABLE_NAME)
			self.assert_table_version_active(table_active)
		finally:
			cleanup_table(self.client)

	def test_create_table(self) -> None:
		"""Verify that POST /accounts/{account}/tables/{name} successfully creates a table."""
		try:
			table = create_table(self.client)
			self.assert_table_create(table)
		finally:
			cleanup_table(self.client)

	def test_create_table_by_upload(self) -> None:
		"""Verify that POST /accounts/{account}/tables/{name}/upload successfully creates a table."""
		try:
			with open(join('test', TABLE_FILE_LOCAL), 'rb') as file:
				import_ = self.client.tables.upload(
					account=TABLE_ACCOUNT,
					name=TABLE_NAME,
					body=CreateTableFromFileUploadRequest(
						files=[File(
							file=file,
							name=TABLE_FILE_LOCAL
						)]))
			clear_progress()
			print_progress(import_)
			tables = items(self.client.follow(import_, "result",
				result_type=RestList,
				item_type=TableVersion,
				status_update=print_progress))
			table = tables[0]
			self.assert_table_create(table)
		finally:
			cleanup_table(self.client)

	def test_create_table_by_upload_with_options(self) -> None:
		"""Verify that POST /accounts/{account}/tables/{name}/upload successfully creates a table
		and respects the specified FileImportOptions."""
		table_name = TABLE_NAME + '_with_options'
		try:
			with open(join('test', TABLE_JSON_FILE_LOCAL), 'rb') as file:
				import_ = self.client.tables.upload(
					account=TABLE_ACCOUNT,
					name=table_name,
					body=CreateTableFromFileUploadRequest(
						files=[File(
							file=file,
							name=TABLE_JSON_FILE_LOCAL
						)],
						options=FileImportOptions(
							excluded_properties=["Description"]
						)))
			clear_progress()
			print_progress(import_)
			tables = items(self.client.follow(import_, "result",
				result_type=RestList,
				item_type=TableVersion,
				status_update=print_progress))
			table = tables[0] # type: TableVersion
			self.assertTrue(any(x for x in table.columns if "Name" in x.name))
			self.assertFalse(any(x for x in table.columns if "Description" in x.name))
		finally:
			cleanup_table(self.client, table_name)

	def test_export_geojson(self) -> None:
		"""Verify that the 'Accept' header works for specifying the export file type on GET /accounts/{account}/tables/{name}/versions/export."""
		with self.client.tables.versions.export(account="hms", name="hotels", version="latest", accept=TablesVersionsExportAcceptType.APPLICATION_GEO_JSON) as response:
			content_type = response.content_type
			self.assertTrue(content_type in ("application/geo+json", "application/vnd.geo+json"), f"Expected response to have GeoJSON content type. Instead was {content_type}")
			geo_json_str = response.file.read().decode('utf-8')
			geo_json = json.loads(geo_json_str)
			self.assertEqual("FeatureCollection", geo_json["type"])

class TestQueries(ClientTest):
	"""Tests of the query-related endpoints of the Rest API."""

	def test_export_query_direct(self) -> None:
		"""Verify that /queries/export successfully returns CSV data."""
		try:
			create_table(self.client)
			with self.client.queries.export_direct(body=Query(
				table=QueryTable(name=f"{TABLE_ACCOUNT}/{TABLE_NAME}"),
				take=10)) as response:

				self.assertEqual(response.content_type, "text/csv")
				self.assertTrue(response.name.endswith(".csv"))
				csv_str = response.file.read().decode('utf-8')
				lines = list(filter(None, csv_str.splitlines()))
				self.assertLessEqual(len(lines), 11)
				self.assertIn(',', lines[0])
		finally:
			cleanup_table(self.client)
