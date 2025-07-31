"""Tests of the table endpoints of the Rest API."""

import json
from   os.path import join
from   typing  import Any, Tuple, cast, Dict, Optional
import unittest

from PIL import Image

from maplargerest.endpoints import RestClient, RestError, items
from maplargerest.models import BorderClipping, ImageFormatType, Layer, LayerColorTransformValues, LayerType, LineDashStyle, MapTileOptions, PolyGradientStyle, Query, QuerySelect, QueryTable, QueryWhereTest, ShadeMethod, Style, StyleRule, StyleRuleConstraint, TestSymbol
# pylint: disable=wrong-import-order
from test.shared_test import ClientTest

class TestLayers(ClientTest):
	"""Tests of the layer endpoints of the Rest API."""

	def setUp(self) -> None:
		"""Set up before each test."""
		super().setUp()
		self.import_test_data(['census/Counties'])

	def test_get_tile_strong_type(self) -> None:
		"""Verify that /layers/{hashes}/tiles/{zoom}/{x}/{y}.{format} successfully returns a PNG object."""
		hash_ = self.client.layers.ensure(Layer(
			query=Query(
				select=QuerySelect(
					type_=LayerType.GEO_POLY
				),
				table=QueryTable(
					name="census/Counties"
				)
			),
			style=Style(
				method=ShadeMethod.RULES,
				rules=[
					StyleRule(
						style=Style(
							fill_color="127-255-0-0",
							poly_gradient_style=PolyGradientStyle.LINEAR,
							border_color_offset=75,
							line_dash=LineDashStyle.SOLID,
							border_clipping=BorderClipping.NONE
						),
						where=[
							[
								QueryWhereTest(
									column="AREA",
									test=TestSymbol.GREATER,
									value=2.5
								)
							]
						],
						constraint=StyleRuleConstraint()
					),
					StyleRule(
						style=Style(
							fill_color="127-0-255-0",
							poly_gradient_style=PolyGradientStyle.LINEAR,
							border_color_offset=75,
							line_dash=LineDashStyle.SOLID,
							border_clipping=BorderClipping.NONE
						),
						where=[
							[
								QueryWhereTest(
									column="*",
									test=TestSymbol.CATCH_ALL,
									value=0
								)
							]
						],
						constraint=StyleRuleConstraint()
					)
				],
				color_transform=LayerColorTransformValues(
					alpha=1
				)
			)
		))

		with self.client.layers.tile(
			hashes=[hash_],
			zoom=7, # Palm Bay, FL
			x=35,
			y=53,
			format_=ImageFormatType.PNG,
			options=MapTileOptions(
				w=1,
				h=1,
				layer_only=True,
				debug=False
			)
		) as tile:

			self.assertEqual(tile.content_type, "image/png")
			png = Image.open(tile.file)
			width, height = png.size
			self.assertEqual(width, 256)
			self.assertEqual(height, 256)
			transparency = transparent_percent(png)
			self.assertGreater(transparency, 0.25, "Expected image to have some transparent pixels.")
			self.assertLess(transparency, 1.0, "Tile should not have been all transparent.")

	def test_get_tile_weak_type(self) -> None:
		"""Verify that /layers/{hashes}/tiles/{zoom}/{x}/{y}.{format} successfully returns a PNG object."""
		hash_ = self.client.layers.ensure(cast(Any, {
			'query': {
				'select': {
					'type': 'geo.poly'
				},
				'table': {
					'name': 'census/Counties'
				}
			},
			'style': {
				'colorTransform': {
					'Alpha': 1
				},
				'method': 'rules',
				'rules': [
					{
						'constraint': {},
						'style': {
							'borderClipping': 'None',
							'borderColorOffset': 75,
							'fillColor': '127-255-0-0',
							'lineDash': 'Solid',
							'polyGradientStyle': 'Linear'
						},
						'where': [
							[
								{
									'column': 'AREA',
									'test': 'Greater',
									'value': 2.5
								}
							]
						]
					},
					{
						'constraint': {},
						'style': {
							'borderClipping': 'None',
							'borderColorOffset': 75,
							'fillColor': '127-0-255-0',
							'lineDash': 'Solid',
							'polyGradientStyle': 'Linear'
						},
						'where': [
							[
								{
									'column': '*',
									'test': 'CatchAll',
									'value': 0
								}
							]
						]
					}
				]
			}
		}))

		with self.client.layers.tile(
			hashes=[hash_],
			zoom=7, # Palm Bay, FL
			x=35,
			y=53,
			format_=ImageFormatType.PNG,
			options=MapTileOptions(
				w=1,
				h=1,
				layer_only=True,
				debug=False
			)
		) as tile:

			#with open('debug.png', 'wb') as debug_file:
			#	debug_file.write(tile.file.read())
			self.assertEqual(tile.content_type, "image/png")
			png = Image.open(tile.file)
			width, height = png.size
			self.assertEqual(width, 256)
			self.assertEqual(height, 256)
			transparency = transparent_percent(png)
			self.assertGreater(transparency, 0.25, "Expected image to have some transparent pixels.")
			self.assertLess(transparency, 1.0, "Tile should not have been all transparent.")

def transparent_percent(image: Image.Image) -> float:
	"""Return a number between 0.0 and 1.0 indicating how much of the image is transparent."""
	width, height = image.size # type: int, int
	transparent = 0
	for y in range(height):
		for x in range(width):
			pixel = cast(Tuple[int, ...], image.getpixel((x, y)))
			if len(pixel) > 3 and pixel[3] < 64:
				transparent += 1
	return transparent / (width * height)
