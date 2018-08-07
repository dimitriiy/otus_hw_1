import ast
import os
import collections
from nltk import pos_tag
import glob

def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] in ('VB', 'VBD', 'VBG', 'VBN', 'VBP')


def get_python_files():
    filenames = [file_name for file_name in glob.glob(path + '/**/*.py', recursive=True)]
    return filenames


def get_file_content(filename):
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        main_file_content = attempt_handler.read()
    try:
        tree = ast.parse(main_file_content)
    except SyntaxError as e:
        print(e)
        tree = None
    return main_file_content, tree


def get_trees(_path, with_filenames=False, with_file_content=False):
    trees = []
    filenames = get_python_files()
    for filename in filenames:
        main_file_content, tree = get_file_content(filename)
        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    return trees


def get_all_names(tree):
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]


def magic_name(f):
    return not (f.startswith('__') and f.endswith('__'))


def separate_to_node(t):
    return [node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)]


def get_all_words_in_path(path):
    trees = [t for t in get_trees(path) if t]
    function_names = [func for func in flat([get_all_names(t) for t in trees]) if magic_name(func)]
    def split_snake_case_name_to_words(name):
        return [n for n in name.split('_') if n]
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def get_top_verbs_in_path(path, top_size=10):
    trees = [t for t in get_trees(path) if t]
    functions = [func for func in flat([separate_to_node(t) for t in trees]) if magic_name(func)]
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in functions])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    t = get_trees(path)
    names = [f for f in flat([separate_to_node(t) for t in t]) if magic_name(f)]
    return collections.Counter(names).most_common(top_size)


if __name__ == "__main__":
    words = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
]
    for project in projects:
        path = os.path.join('.', project)
        words += get_top_verbs_in_path(path)

    top_size = 200
    print('total %s words, %s unique' % (len(words), len(set(words))))
    for word, occurence in collections.Counter(words).most_common(top_size):
        print(word, occurence)
