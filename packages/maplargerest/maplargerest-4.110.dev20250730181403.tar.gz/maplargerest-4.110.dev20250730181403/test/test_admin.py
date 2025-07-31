"""Tests of the admin-related functionality of the Rest API, such as accounts, users, and groups."""

import json
from   os.path           import join
from   typing            import Optional
import unittest

from maplargerest.endpoints import RestClient, RestError, items
from maplargerest.models import Account, CreateAccountRequest, CreateGroupRequest, CreateUserRequest, Group, UpdateAccountRequest, UpdateGroupRequest, User
# pylint: disable=wrong-import-order
from test.shared_test import ClientTest

ACCOUNT_CODE = "testPythonClient"

class TestAccounts(ClientTest):
	"""Tests for the account-related endpoints."""

	def setUp(self) -> None:
		"""Set up before each test."""
		super().setUp()
		self.cleanup_account()

	def create_account(self) -> Account:
		"""Create an account for testing."""
		return self.client.accounts.post(
			body=CreateAccountRequest(
				code=ACCOUNT_CODE,
				name="Test Python Client",
				description="Account for testing the Python Rest API Client")
		)

	def cleanup_account(self) -> None:
		"""Delete the account used for testing."""
		try:
			self.client.accounts.delete(id_or_code=ACCOUNT_CODE)
		except RestError as ex:
			if ex.status != 404:
				raise

	def test_list_accounts(self) -> None:
		"""Verify that GET /accounts successfully returns a list of accounts."""
		accounts = items(self.client.accounts.list())
		self.assertGreaterEqual(len(accounts), 2)

	def test_create_account(self) -> None:
		"""Verify that POST /accounts successfully creates an account."""
		try:
			account = self.create_account()
			self.assertIsInstance(account.id_, int)
			self.assertNotEqual(account.id_, 0)
		finally:
			self.cleanup_account()

	def test_update_account(self) -> None:
		"""Verify that PUT /accounts/{idOrCode} successfully updates an account."""
		try:
			account = self.create_account()
			id_ = str(account.id_)
			self.client.accounts.put(
				id_or_code=id_,
				body=UpdateAccountRequest(
					max_row_limit=42
				)
			)
			modified_account = self.client.accounts.get(id_or_code=id_)
			self.assertEqual(modified_account.max_row_limit, 42)
		finally:
			self.cleanup_account()

	def test_delete_account(self) -> None:
		"""Verify that DELETE /accounts/{idOrCode} successfully deletes an account."""
		try:
			account = self.create_account()
			id_ = str(account.id_)
			self.client.accounts.delete(id_or_code=id_)
			try:
				self.client.accounts.get(id_or_code=id_)
			except RestError as ex:
				self.assertEqual(ex.status, 404)
		finally:
			self.cleanup_account()

class TestGroups(ClientTest):
	"""Tests for the group-related endpoints."""

	def setUp(self) -> None:
		"""Set up before each test."""
		super().setUp()
		self.ensure_account()

	def tearDown(self) -> None:
		"""Clean up after each test."""
		self.cleanup_account()

	def ensure_account(self) -> Account:
		"""Create an account for testing if it does not exist yet."""
		try:
			return self.client.accounts.get(id_or_code=ACCOUNT_CODE)
		except RestError as ex:
			if ex.status != 404:
				raise
			return self.client.accounts.post(
				body=CreateAccountRequest(
					code=ACCOUNT_CODE,
					name="Test Python Client",
					description="Account for testing the Python Rest API Client")
			)

	def cleanup_account(self) -> None:
		"""Delete the account used for testing."""
		try:
			self.client.accounts.delete(id_or_code=ACCOUNT_CODE)
		except RestError as ex:
			if ex.status != 404:
				raise

	def cleanup_group(self, id_or_name: str) -> None:
		"""Delete the group used for testing."""
		try:
			self.client.groups.delete(account=ACCOUNT_CODE, id_or_name=id_or_name)
		except RestError as ex:
			if ex.status != 404:
				raise

	def test_list_groups(self) -> None:
		"""Verify that GET /accounts/{account}/groups successfully returns a list of groups."""
		groups = items(self.client.groups.list(account="nobody"))
		self.assertGreaterEqual(len(groups), 1)
		self.assertEqual(groups[0].name, "nobody")

	def test_get_group(self) -> None:
		"""Verify that GET /accounts/{account}/groups/{idOrName} successfully returns a single group."""
		group = self.client.groups.get(account="nobody", id_or_name="nobody")
		self.assertEqual(group.name, "nobody")

	def test_create_group(self) -> None:
		"""Verify that POST /accounts/{account}/groups successfully creates a group."""
		group = self.create_group()
		id_ = str(group.id_)
		self.cleanup_group(id_)

	def create_group(self) -> Group:
		"""Create a group for testing."""
		return self.client.groups.post(
			account=ACCOUNT_CODE,
			body=CreateGroupRequest(
				name="Test group"
			))

	def test_update_group(self) -> None:
		"""Verify that PUT /accounts/{account}/groups/{idOrName} successfully updates a group."""
		group = self.create_group()
		id_ = str(group.id_)
		try:
			modified_group = self.client.groups.put(
				account=ACCOUNT_CODE,
				id_or_name=id_,
				body=UpdateGroupRequest(
					description="modified"
				))
			modified_group = self.client.groups.get(account=ACCOUNT_CODE, id_or_name=id_)
			self.assertEqual(modified_group.description, "modified")
		finally:
			self.cleanup_group(id_)

class TestUsers(ClientTest):
	"""Tests for the user-related endpoints."""

	def setUp(self) -> None:
		"""Set up before each test."""
		super().setUp()
		self.cleanup_user()

	def cleanup_user(self) -> None:
		"""Delete the user used for testing."""
		user = self.find_user_by_email("test_user_python@example.com")
		if user is not None:
			self.client.users.delete(id_=user.id_)

	def test_list_users(self) -> None:
		"""Verify that GET /users successfully returns a list of users."""
		users = items(self.client.users.list())
		self.assertGreaterEqual(len(users), 1)

	def test_get_user(self) -> None:
		"""Verify that GET /users/{id} successfully returns a single user."""
		nobody = self.find_user_by_email("nobody@ml.com")
		assert isinstance(nobody, User)
		user = self.client.users.get(id_=nobody.id_)
		self.assertEqual(user.id_, nobody.id_)
		self.assertEqual(user.name, "nobody")
		self.assertEqual(user.email, "nobody@ml.com")

	def find_user_by_email(self, email: str) -> Optional[User]:
		"""Return the user uniquely identified by the specified email address, or None if not found."""
		users = items(self.client.users.list())
		try:
			return next(filter(lambda x: x.email == email, users))
		except StopIteration:
			return None

	def test_create_user(self) -> None:
		"""Verify that POST /users successfully creates a user."""
		user = self.create_user()
		try:
			id_ = user.id_
			self.assertIsInstance(id_, int)
			self.assertNotEqual(id_, 0)
		finally:
			self.client.users.delete(id_=id_)

	def create_user(self) -> User:
		"""Create a user for testing."""
		return self.client.users.post(body=CreateUserRequest(
			email="test_user_python@example.com",
			name="test_user_python",
			password="NQCyNdKEgrIICnY5zG5F"
		))

	def test_delete_user(self) -> None:
		"""Verify that DELETE /users/{id} successfully deletes a user."""
		user = self.create_user()
		id_ = user.id_
		self.client.users.delete(id_=id_)
		deleted_user = self.find_user_by_email("test_user_python@example.com")
		self.assertIsNone(deleted_user)
