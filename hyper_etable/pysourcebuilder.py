from __future__ import with_statement
import textwrap
from contextlib import contextmanager
from hyper_etable.sourcebuilder import SourceBuilder

INDENT = ' ' * 4
TRIPLE_QUOTES = '"' * 3
DOCSTRING_WIDTH = 72


class PySourceBuilder(SourceBuilder):
    """
    A special SourceBuilder that provides some convenience context managers
    for writing well formatted Python code.

    """
    def __init__(self, indent_with=INDENT):
        super(PySourceBuilder, self).__init__(indent_with=indent_with)

    @contextmanager
    def block(self, code, lines_before=0):
        """
        A context manager for block structures. It's a generic way to start a
        control structure (if, try, while, for etc.) or a class, function or
        method definition.

        The given ``code`` will be printed preceded by 0 or more blank lines,
        controlled by the ``lines_before`` parameter. An indent context is
        then started.

        Example::

            sb = PySourceBuilder()
            >>>
            >>> with sb.block('class Hello(object):', 2):
            ...     with sb.block('def __init__(self, what=\'World\'):', 1):
            ...         sb.writeln('pass')
            ...
            >>> print sb.end()


            class Hello(object):

                def __init__(self, what='World'):
                    pass

        """
        for i in range(lines_before):
            self.writeln()
        self.writeln(code)
        with self.indent:
            yield

    def docstring(self, doc, delimiter=TRIPLE_QUOTES, width=DOCSTRING_WIDTH):
        """
        Write a docstring. The given ``doc`` is surrounded by triple double
        quotes (\"\"\"). This can be changed by passing a different
        ``delimiter`` (e.g. triple single quotes).

        The docstring is formatted to not run past 72 characters per line
        (including indentation). This can be changed by passing a different
        ``width`` parameter.

        """
        doc = textwrap.dedent(doc).strip()
        max_width = width - len(str(self.indent))
        lines = doc.splitlines()
        if len(lines) == 1 and len(doc) < max_width - len(delimiter) * 2:
            self.writeln(u'%s%s%s' % (delimiter, doc, delimiter))
        else:
            self.writeln(delimiter)
            for line in lines:
                if not line.strip():
                    self.writeln()
                for wrap in textwrap.wrap(line, max_width):
                    self.writeln(wrap)
            self.writeln()
            self.writeln(delimiter)

def build_source_from_class(class_instance, allow_attr):
    sb = PySourceBuilder()
# >>> for klass in klasses:
# ...     with sb.block('class {0}(object)'.format(klass):, 2):
# ...         sb.docstring('TODO: Document {0}'.format(klass))
    # import inspect
    # gg = inspect.getmembers(class_instance)

    with sb.block(f'class {class_instance.__name__}({class_instance.__class__.__name__}):'):
        pass_ok = True
        for a, t in getattr(class_instance, '__annotations__', {}).items():
            sb.writeln(f'{a}: {t.__name__}')
            pass_ok = False
        if pass_ok:
            sb.writeln(f'pass')
        with sb.block(f'def __init__(self):'):
            pass_ok = True
            for attr in class_instance.__dict__:
                attr_val = getattr(class_instance, attr, None)
                if attr_val is None or callable(attr_val) or (attr.startswith('__') and attr not in allow_attr) or attr in list(class_instance.__class__.__dict__):
                    continue
                if isinstance(attr_val,str):
                     attr_val = f'"{attr_val}"'
                sb.writeln(f'self.{attr} = {attr_val}')
                pass_ok = False
            if pass_ok:
                sb.writeln(f'pass')
    return sb
