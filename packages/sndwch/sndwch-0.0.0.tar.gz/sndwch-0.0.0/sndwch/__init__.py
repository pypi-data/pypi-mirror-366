import re

def sub(pattern, repl, text, flags=0):
	escaped_pattern = re.escape(pattern)
	result = re.sub(escaped_pattern, repl, text, flags=flags)
	return result


def split(pattern, text, maxsplit=0, flags=0):
	escaped_pattern = re.escape(pattern)
	result_list = re.split(escaped_pattern, text, maxsplit=maxsplit, flags=flags)
	return result_list


def search(pattern, text, flags=0):
	escaped_pattern = re.escape(pattern)
	match_obj = re.search(escaped_pattern, text, flags=flags)
	return match_obj


def match(pattern, text, flags=0):
	escaped_pattern = re.escape(pattern)
	match_obj = re.match(escaped_pattern, text, flags=flags)
	return match_obj


def findall(pattern, text, flags=0):
	escaped_pattern = re.escape(pattern)
	results = re.findall(escaped_pattern, text, flags=flags)
	return results


def fullmatch(pattern, text, flags=0):
	escaped_pattern = re.escape(pattern)
	match_obj = re.fullmatch(escaped_pattern, text, flags=flags)
	return match_obj
