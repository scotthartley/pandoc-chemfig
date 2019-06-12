"""Pandoc filter that provides rudimentary support for three things:
Allows different types of figures (schemes, charts, graphs) to be used
(esp. in LaTeX), implements cross-referencing for said figures (as a
highly simplified version of the support in pandoc-crossref), and
supports the wrapfig LaTeX package to wrap text around figures in pdf
(and LaTeX) output.

"""

from pandocfilters import toJSONFilters, Str, Image, Strong, Emph, RawInline
import re, textwrap

# Reference regex pattern used to extract id_tag (for cross-referencing)
REF_PAT = re.compile(r'\[?@([^\s\]]*)\]?')

# Types of chemistry figures supported by LaTeX (e.g., with achemso)
ALT_LATEX_FIGS = ['scheme', 'chart', 'graph']

# Dictionaries to hold id tags and count figure classes.
known_ids = {}
known_classes = {}


def parse_refs(key, val, fmt, meta):
    """Runs through citations in the document, replacing those with ids
    found in known_ids with the appropriate numbers or LaTeX \ref{}
    commands.

    """

    if key == 'Cite':
        if REF_PAT.match(val[1][0]['c']):
            id_tag = REF_PAT.match(val[1][0]['c']).groups()[0]
            if id_tag in known_ids:
                if fmt in ['latex','pdf']:
                    return RawInline(fmt, "\\ref{{{}}}".format(id_tag))
                else:
                    return Str(known_ids[id_tag])


def process_images(key, val, fmt, meta):
    """Runs through figures in the document, counting figures of a
    particular type. For LaTeX, adds appropriate code for non-"figure"
    environments and leaves normal figures untouched (\label commands
    are added automatically already). If the wwidth attribute is passed
    to the figure, hardcodes the appropriate LaTeX code for the wrapfig
    package through the wrapfloat environment. For other formats, adds
    preamble to caption with figure type and number.

    """

    if key == 'Image':
        attrs, caption, target = val

        if attrs[1] and caption:
            cls = attrs[1][0] # Class attribute for the image

            if cls in known_classes:
                known_classes[cls] += 1
            else:
                known_classes[cls] = 1

            # Assign figure/scheme/chart/graph number.
            known_ids[attrs[0]] = str(known_classes[cls])

            # Loop through image attributes to locate wrapfig-relevant
            # attributes. If found, set latex_wrap to True and read
            # size and position (optional).
            latex_wrap = False
            latex_wrap_pos = 'r' # Default position
            latex_fig_place = False
            latex_suffix = ""
            for other_atr in attrs[2]:
                if other_atr[0] == 'wwidth':
                    latex_wrap = True
                    latex_size = other_atr[1]
                elif other_atr[0] == 'wpos':
                    latex_wrap_pos = other_atr[1]
                elif other_atr[0] == 'lpos':
                    latex_fig_place = True
                    latex_fig_place_pos = other_atr[1]
                elif other_atr[0] == 'lts':
                    latex_suffix = other_atr[1]

            if fmt in ['latex','pdf']:
                # Only use "\caption" command if caption is not empty.
                if caption != []:
                    caption_text = ([RawInline(fmt, r"\caption{")] + caption
                                   + [RawInline(fmt, r"}")])
                else:
                    caption_text = []

                if latex_wrap:
                    return ([RawInline(fmt, textwrap.dedent(r"""
                        \begin{{wrapfloat}}{{{cls}}}{{{pos}}}{{{size}}}
                        \centering
                        \includegraphics{{{file}}}
                        """.format(
                                cls=cls+latex_suffix,
                                file=target[0],
                                size=latex_size,
                                pos=latex_wrap_pos)))]
                        + caption_text
                        + [RawInline(fmt, textwrap.dedent(r"""
                        \label{{{id_tag}}}
                        \end{{wrapfloat}}
                        """.format(
                                cls=cls+latex_suffix,
                                id_tag=attrs[0])))])
                elif latex_fig_place:
                    return ([RawInline(fmt, textwrap.dedent(r"""
                            \begin{{{cls}}}[{pos}]
                            \centering
                            \includegraphics{{{file}}}""".format(
                                    cls=cls+latex_suffix,
                                    pos=latex_fig_place_pos,
                                    file=target[0])))]
                            + caption_text
                            + [RawInline(fmt, textwrap.dedent(r"""
                            \label{{{id_tag}}}
                            \end{{{cls}}}
                            """.format(
                                    cls=cls+latex_suffix,
                                    id_tag=attrs[0])))])
                else:
                    return ([RawInline(fmt, textwrap.dedent(r"""
                        \begin{{{cls}}}
                        \centering
                        \includegraphics{{{file}}}""".format(
                                cls=cls+latex_suffix,
                                file=target[0])))]
                        + caption_text
                        + [RawInline(fmt, textwrap.dedent(r"""
                        \label{{{id_tag}}}
                        \end{{{cls}}}
                        """.format(
                                cls=cls+latex_suffix,
                                id_tag=attrs[0])))])
            else:
                # Add label to caption for non-LaTeX output.

                # Default labels, suffix, and format
                label = [Strong([Str(cls.capitalize() + " ")])]
                suffix = [Strong([Str(". ")])]

                if 'fig-abbr' in meta:
                    if cls in meta['fig-abbr']['c']:
                        label = meta['fig-abbr']['c'][cls]['c']
                    if 'suffix' in meta['fig-abbr']['c']:
                        suffix = meta['fig-abbr']['c']['suffix']['c']

                # Label takes format of abbreviation.
                if label[0]['t'] == 'Strong':
                    number = [Strong([Str(known_ids[attrs[0]])])]
                elif label[0]['t'] == 'Emph':
                    number = [Emph([Str(known_ids[attrs[0]])])]
                else:
                    number = [Str(known_ids[attrs[0]])]

                new_caption = label + number + suffix + caption

                return Image(attrs, new_caption, target)


def main():
    toJSONFilters([process_images, parse_refs])


if __name__ == '__main__':
    main()
