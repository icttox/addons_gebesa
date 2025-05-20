# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
Adds a new "exercise" admonition type
"""

def setup(app):
    app.add_directive('exercise', Exercise)
    app.add_node(exercise, html=(
        lambda self, node: self.visit_admonition(node, 'exercise'),
        lambda self, node: self.depart_admonition(node)
    ), latex=(
        lambda self, node: self.visit_admonition(node),
        lambda self, node: self.depart_admonition(node)
    ))

from docutils import nodes
from docutils.parsers.rst.directives import admonitions
from sphinx.locale import admonitionlabels, l_


class exercise(nodes.Admonition, nodes.Element): pass
class Exercise(admonitions.BaseAdmonition):
    node_class = exercise

admonitionlabels['exercise'] = l_('Exercise')
