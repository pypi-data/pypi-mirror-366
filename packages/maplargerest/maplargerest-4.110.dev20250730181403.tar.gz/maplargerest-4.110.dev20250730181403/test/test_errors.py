"""Tests of the error handling code."""
import unittest

from   maplargerest.endpoints import RestError, RestValidationError
from   maplargerest.models    import ProblemDetails, ValidationProblemDetails
# pylint: disable=wrong-import-order

class TestRestError(unittest.TestCase):
	"""Tests for the RestError class."""

	def test_rest_error_ctor(self) -> None:
		"""Verify that the RestError constructor works."""
		json = b'{"messages":["no account found!"],"type":null,"title":"Not found","status":404,"detail":"no account found!","instance":null,"extensions":{}}'
		error = RestError("https://localhost/restapi/v1/accounts/doesnotexist", 404, {}, json)
		self.assertIsInstance(error, Exception)
		self.assertIsInstance(error, ProblemDetails)
		self.assertEqual(error.status, 404)
		self.assertEqual(error.body_text, json)
		self.assertEqual(error.messages[0], "no account found!")
		self.assertEqual(error.title, "Not found")
		self.assertEqual(error.detail, "no account found!")

class TestRestValidationError(unittest.TestCase):
	"""Tests for the RestValidationError class."""

	def test_rest_validation_error_ctor(self) -> None:
		"""Verify that the RestValidationError constructor works."""
		json = b"""
			{
				"errors": {
					"name": [ "You must provide a name for this account." ],
					"description": [ "You must provide a description for this account." ],
					"code": [ "You must provide an account code for this account." ]
				},
				"type": null,
				"title": "Validation errors",
				"status": 400,
				"detail": "You must provide a name for this account. ... and other issues.",
				"instance": null,
				"extensions": {}
			}"""
		error = RestValidationError("https://localhost/restapi/v1/accounts", 400, {}, json)
		self.assertIsInstance(error, RestError)
		self.assertIsInstance(error, ValidationProblemDetails)
		self.assertEqual(error.status, 400)
		self.assertEqual(error.body_text, json)
		self.assertEqual(error.errors["name"][0], "You must provide a name for this account.")
		self.assertEqual(error.errors["description"][0], "You must provide a description for this account.")
		self.assertEqual(error.errors["code"][0], "You must provide an account code for this account.")
		self.assertEqual(error.title, "Validation errors")
		self.assertEqual(error.detail, "You must provide a name for this account. ... and other issues.")
