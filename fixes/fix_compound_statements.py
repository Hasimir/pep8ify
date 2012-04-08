from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import find_indentation
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as symbols
from lib2to3.pytree import Node, Leaf


class FixCompoundStatements(BaseFix):
    u''' Compound statements (multiple statements on the same line) are
    generally discouraged.

    While sometimes it's okay to put an if/for/while with a small body
    on the same line, never do this for multi-clause statements. Also
    avoid folding such long lines!

    Node(if_stmt, [
        Leaf(1, u'if'), 
        Node(comparison, 
                [
                    Leaf(1, u'foo'), Leaf(28, u'=='), Leaf(3, u"'blah'")
                ]
        ),
        Leaf(11, u':'),
        Node(suite,
            [
                Leaf(4, u'\n'),
                Leaf(5, u'    '),
                Node(simple_stmt, 
                    [
                        Node(power,
                            [
                                Leaf(1, u'do_blah_thing'), Node(trailer, [Leaf(7, u'('), Leaf(8, u')')])
                            ]
                        ),
                        Leaf(4, u'\n')]
                ),
                Leaf(6, '')
            ]
        )]
    )
        
    Node(if_stmt, [
        Leaf(1, u'if'),
        Node(comparison,
            [
                Leaf(1, u'foo'), Leaf(28, u'=='), Leaf(3, u"'blah'")
            ]
        ),
        Leaf(11, u':'),
        
        Node(simple_stmt,
            [
                Node(power,
                    [
                        Leaf(1, u'do_blah_thing'), Node(trailer, [Leaf(7, u'('), Leaf(8, u')')])
                    ]
                ),
                Leaf(4, u'\n')]
        )
    ])

    '''
    
    def match(self, node):
        results = {}
        if node.prev_sibling and isinstance(node.prev_sibling, Leaf) and node.prev_sibling.type == token.COLON and node.type != symbols.suite:
            # If it's inside a lambda definition, leave it alone
            if node.parent.type == symbols.lambdef:
                pass
            else:
                results["colon"] = True
        if node.type == symbols.simple_stmt and Leaf(token.SEMI, u';') in node.children:
            results["semi"] = True
        return results
    
    def transform(self, node, results):
        if results.get("colon"):
            node_copy = node.clone()
            # Strip any whitespace that could have been there
            node_copy.prefix = node_copy.prefix.lstrip()
            old_depth = find_indentation(node)
            new_indent = u'%s%s' % ((u' ' * 4), old_depth)
            new_node = Node(symbols.suite, [Leaf(token.NEWLINE, u'\n'), Leaf(token.INDENT, new_indent), node_copy, Leaf(token.DEDENT, u'')])
            node.replace(new_node)
            node.changed()
            
            # Replace node with new_node in case semi
            node = node_copy
            
        if results.get("semi"):
            for child in node.children:
                if child.type == token.SEMI:
                    # Strip any whitespace from the next sibling
                    child.next_sibling.prefix = child.next_sibling.prefix.lstrip()
                    child.next_sibling.changed()
                    # Replace the semi with a newline
                    old_depth = find_indentation(child)
                    
                    child.replace([Leaf(token.NEWLINE, u'\n'), Leaf(token.INDENT, old_depth)])
                    child.changed()
