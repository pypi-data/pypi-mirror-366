
import sys
sys.path.append('..')

from umapper import Case
from umapper import translate_case
from umapper import convert_to_object
from umapper import assemble_dicts

orig = {
	'OutterField': { 'inner_field': 123, 'sibling_inner_field': 321 },
	'siblingField': "Some Text"
}

def testCase():
	a = translate_case(orig, Case.SNAKE);  assert a['sibling_field'] == "Some Text"
	b = translate_case(orig, Case.CAMEL);  assert b['outterField']['innerField'] == 123
	c = translate_case(orig, Case.PASCAL); assert c['OutterField']['SiblingInnerField'] == 321
	assert 123 == translate_case(123, Case.PASCAL)


def testConversion():
	snake = translate_case(orig, Case.SNAKE)
	assert convert_to_object(snake).outter_field.inner_field == 123


def testAssemble():
	a = { 'level_one': { 'level_two': "Hello" }}
	b = { 'level_zero': { 'level_one': "World" }}
	c = assemble_dicts(a, b, thirty=30)

	assert "Hello World" == (
		c['levelOne']['levelTwo'] + " " +
		c['levelZero']['levelOne']
	)
	

def testListing():
	test = [orig, orig]
	a = translate_case(test, Case.PASCAL)
	b = convert_to_object(test)

	assert a[0]['SiblingField'] == a[1]['SiblingField']
	assert b[0].OutterField.inner_field == b[1].OutterField.inner_field
	assert 3 == convert_to_object(3)

	c = assemble_dicts({'listage': test}, c=orig, d=test, e=[1, 2, 3])
	assert c['c']['siblingField'] == c['listage'][0]['siblingField']
	assert c['c']['siblingField'] == c['d'][0]['siblingField']
	assert c['e'][0] == 1

