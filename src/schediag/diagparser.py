# -*- coding: utf-8 -*-

import codecs
from re import MULTILINE, DOTALL
from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
    oneplus, forward_decl, NoParseError)
from blockdiag.utils.namedtuple import namedtuple


ENCODING = 'utf-8'

Chart = namedtuple('Chart', 'type id stmts')
Node = namedtuple('Node', 'id attrs')
Attr = namedtuple('Attr', 'name value')
DefAttrs = namedtuple('DefAttrs', 'object attrs')


class ParseException(Exception):
    pass


def tokenize(str):
    'str -> Sequence(Token)'
    specs = [
        ('Comment', (r'/\*(.|[\r\n])*?\*/', MULTILINE)),
        ('Comment', (r'//.*',)),
        ('NL',      (r'[\r\n]+',)),
        ('Space',   (r'[ \t\r\n]+',)),
        ('Name',    (ur'[A-Za-z_\u0080-\uffff][A-Za-z_0-9\.\u0080-\uffff]*',)),
        ('Op',      (r'[{}():;,\-=\[\]]',)),
        ('Date',    (r'[0-9]+(/[0-9]+){1,2}',)),
        ('Number',  (r'-?(\.[0-9]+)|([0-9]+(\.[0-9]*)?)',)),
        ('String',  (r'(?P<quote>"|\').*?(?<!\\)(?P=quote)', DOTALL)),
    ]
    useless = ['Comment', 'NL', 'Space']
    t = make_tokenizer(specs)
    return [x for x in t(str) if x.type not in useless]


def parse(seq):
    'Sequence(Token) -> object'
    unarg = lambda f: lambda args: f(*args)
    tokval = lambda x: x.value
    flatten = lambda list: sum(list, [])
    n = lambda s: a(Token('Name', s)) >> tokval
    op = lambda s: a(Token('Op', s)) >> tokval
    op_ = lambda s: skip(op(s))
    date = some(lambda s: a(Token('Date', s))).named('date') >> tokval
    id = some(lambda t:
        t.type in ['Name', 'Number', 'String']).named('id') >> tokval
    make_chart_attr = lambda args: DefAttrs(u'chart', [Attr(*args)])

    node_id = id  # + maybe(port)
    term = date + op_('-') + date
    value = (id | term | date)
    a_list = (
        id +
        maybe(op_('=') + id) +
        skip(maybe(op(',')))
        >> unarg(Attr))
    attr_list = (
        many(op_('[') + many(a_list) + op_(']'))
        >> flatten)
    chart_attr = id + (op_('=') | op_(':')) + value >> make_chart_attr
    node_stmt = node_id + attr_list >> unarg(Node)

    stmt = (
        chart_attr
        | node_stmt
    )
    stmt_list = many(stmt + skip(maybe(op(';'))))
    chart = (
        maybe(n('diagram')) +
        maybe(id) +
        op_('{') +
        stmt_list +
        op_('}')
        >> unarg(Chart))
    dotfile = chart + skip(finished)

    return dotfile.parse(seq)


def parse_file(path):
    try:
        input = codecs.open(path, 'r', 'utf-8').read()
        return parse(tokenize(input))
    except LexerError, e:
        message = "Got unexpected token at line %d column %d" % e.place
        raise ParseException(message)
    except Exception, e:
        raise ParseException(str(e))
