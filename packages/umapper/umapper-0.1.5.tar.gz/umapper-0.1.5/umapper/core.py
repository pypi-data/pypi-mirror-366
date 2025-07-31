
import humps
import collections

class Case:

	'''Different types of case.

	CAMEL is the case used in Java and JavaScript methods, somethingLikeThis().
	SNAKE is usually utilized in C/C++ and Python methods, something_like_this().
	PASCAL is CapitalCamelCase, often used in class names and Pascal derivatives.
	Kebab case is many times used in Scheme and other Lisp dialects, but was not
	included in this library

	'''

	CAMEL = 1
	SNAKE = 2
	PASCAL = 3


_transforms = {
	Case.CAMEL: humps.camelize,
	Case.SNAKE: lambda x : humps.decamelize(humps.camelize(x)),
	Case.PASCAL: humps.pascalize,
}


_sequences = tuple([tuple, list])
_mappings = tuple([collections.abc.Mapping])

def register_mapping_class(cls): # pragma: no cover

	'''Registers classes that should be recursively mapped.

	By default, umapper navigates dictionaries and built in sequences
	(lists and tuples), recursively mapping their contents. Often libraries
	offer utility classes that behave like dictionaries (mappings) but are
	not themselves either child classes of dictionaries nor inherit
	from collections.abc.Mapping. This method is used to register such
	classes, which must have a .items() method that iterates over its
	(key,value) entries.

	Args:
	  cls (class): class to register.

	'''

	global _mappings

	new_mappings = set(_mappings)
	new_mappings.add(cls)
	_mappings = tuple(new_mappings)


def _create_case_mapping(fields, output_case):
	method = _transforms[output_case]
	mapping = dict()

	for field in fields:
		mapped_field = method(field)
		mapping[mapped_field] = field

	return mapping


def translate_case(value, desired_case):

	'''Translate names of keys from dictionary-like (mapping) objects to a
	desired case.

	Args:
		value (dict-like): mapping object to translate case.
		deseired_case (int): value of Case indicating what case to map to.

	Returns:
	  dict: a copy of the passed dictionary with the keys translated.

	'''

	if isinstance(value, _sequences):
		result = list()

		for item in value:
			translated = translate_case(item, desired_case)
			result.append(translated)

		return result

	if not isinstance(value, _mappings):
		return value

	source_mapping = value
	mapping = _create_case_mapping(value.keys(),
		desired_case)

	converted_dict = dict()
	for output_key, input_key in mapping.items():
		input_content = source_mapping[input_key]

		if isinstance(input_content, _sequences):
			translated_values = list()

			for item in input_content:
				translated = translate_case(item, desired_case)
				translated_values.append(translated)

			input_content = translated_values

		if isinstance(input_content, _mappings):
			input_content = translate_case(input_content,
				desired_case)

		converted_dict[output_key] = input_content

	return converted_dict

#-------------------------------------------------------------------------------

class _convert_mapping:
	def __init__(self, mapping):
		complex_values = dict()
		sane = dict()

		_complex_types = (
			*_mappings,
			*_sequences
		)

		for key, value in mapping.items():
			dst = complex_values if isinstance(value, _complex_types) else sane
			dst[key] = value

		for key, value in complex_values.items():
			sane[key] = convert_to_object(value)

		self.__dict__.update(sane)

	def keys(self): return self.__dict__.keys()
	def values(self): return self.__dict__.values()
	def items(self): return self.__dict__.items()


def convert_to_object(value):
	'''Transform dictionaries or dictionary-like objects into objects.
	The keys of the dictionary will become the fields of the newly generated
	object. This function will recursively convert the dictionary.

	Args:
		value (dict-like): mapping object to convert to an object.

	Returns:
		object: raw object with the contents of the dictionary.

	'''

	if isinstance(value, _mappings):
		return _convert_mapping(value)

	if isinstance(value, list):

		return [
			convert_to_object(element)
			for element in value
		]

	return value


def assemble_dicts(*bases,
	include_nones=True,
	mapping_case=Case.CAMEL,
	**named):

	'''Merges dictionaries into one final dictionary.
	This method does a couple of things: firsly, it'll merge separated
	dictionaties into one single dictionary, and if the same key is present
	in multiple dicts, the last ones will overwrite any previously processed
	key; secondly, it'll convert the keys of the dictionaries to an specific
	case, which can be be configured by the key parameter 'mapping_case', which
	defaults to camel case; thirdly, it can skip including keys which have
	null values emplyoing the key parameter 'include_nones', that defaults to
	true; and lastly, any other key parameter will be included in the final
	result.

	Args:
		bases ([dict]): list of dictionaries to merge/assemble.
		include_nones (boolean): whether to include keys with null values, defaults to true.
		mapping_case (int): which case to map the keys to, defaults to camel case.
		named: any other key=value key parameter that should be included in the merged dict

	Returns:
		dict: a dictionary with the list of dicts joined.

	'''

	result = dict()
	for entry in bases:
		for key, value in entry.items():
			if value is not None or include_nones:
				result[key] = value

	for field, entry in named.items():
		if isinstance(entry, _sequences):
			scoped = list()

			for item in entry:
				if isinstance(item, _mappings):
					assembled = assemble_dicts(item)
					scoped.append(assembled)

				else:
					scoped.append(item)

			result[field] = scoped

		elif isinstance(entry, _mappings):
			scoped = dict()

			for key, value in entry.items():
				if value is not None:
					scoped[key] = value

			result[field] = scoped

		else:
			result[field] = entry

	mapped = (
		translate_case(result, mapping_case)
			if mapping_case is not None
			else mapped
	)

	return mapped

#-------------------------------------------------------------------------------

__all__ = [
	"Case",
	"register_mapping_class",
	"translate_case",
	"convert_to_object",
	"assemble_dicts"
]

