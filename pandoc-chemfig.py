#! /usr/bin/env python3
"""Pandoc filter that provides rudimentary support for two things:
Allows different types of figures (schemes, charts, graphs) to be used
(esp. in LaTeX), and implements cross-referencing for said figures (as a highly
simplified version of the support in pandoc-crossref).

"""

from pandocfilters import toJSONFilters, Str, Image, RawInline
import re, textwrap

# Reference regex pattern used to extract id_tag
REF_PAT = re.compile(r'\[?@([^\s\]]*)\]?')

# Types of chemistry figures supported by LaTeX (e.g., with achemso)
ALT_LATEX_FIGS = ['scheme', 'chart', 'graph']

# Dictionaries to hold id tags and count figure classes.
known_ids = {}
known_classes = {}


def parse_refs(key, val, fmt, meta):
    """Runs through citations in the document, replacing those with ids
    found in known_ids with the appropriate numbers or LaTeX \ref{} commands.

    """

    if key == 'Cite':
        if REF_PAT.match(val[1][0]['c']):
            id_tag = REF_PAT.match(val[1][0]['c']).groups()[0]
            if id_tag in known_ids:
                if fmt in ['latex','pdf']:
                    return RawInline(fmt, '\\ref{{{}}}'.format(id_tag))
                else:
                    return Str(known_ids[id_tag])
        

def process_images(key, val, fmt, meta):
    """Runs through figures in the document, counting figures of a particular
    type. For LaTeX, adds appropriate code for non-"figure" environments and
    leaves normal figures untouched (\label commands are added automatically
    already). For other formats, adds preamble to caption with figure type and
    number.

    """

    if key == 'Image':
        attrs, caption, target = val

        if attrs[1]:
            cls = attrs[1][0] # Class attribute for the image.
        
            if cls in known_classes:
                known_classes[cls] += 1
            else:
                known_classes[cls] = 1

            known_ids[attrs[0]] = str(known_classes[cls])

            if fmt in ['latex','pdf']:
                if cls not in ALT_LATEX_FIGS:
                    return Image(attrs, caption, target)
                else:
                    return [RawInline(fmt, textwrap.dedent("""\
                        \\begin{{{cls}}}
                        \\centering
                        \\caption{{""".format(cls=cls)))] \
                        + caption \
                        + [RawInline(fmt, textwrap.dedent("""\
                        }}\\label{{{id_tag}}}
                        \\includegraphics{{{file}}}
                        \\end{{{cls}}}
                            """.format(cls=cls, file=target[0], 
                                       id_tag=attrs[0])))]
            else:
                new_caption = [Str("{} ".format(cls.capitalize()) \
                               + known_ids[attrs[0]] + ". ")] + caption
                return Image(attrs, new_caption, target)

if __name__ == '__main__':
    toJSONFilters([process_images, parse_refs])