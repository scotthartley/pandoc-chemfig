"""Pandoc filter that provides rudimentary support for three things:
Allows different types of figures (schemes, charts, graphs) to be used
(esp. in LaTeX), implements cross-referencing for said figures (as a
highly simplified version of the support in pandoc-crossref), and
supports the wrapfig LaTeX package to wrap text around figures in pdf
(and LaTeX) output.

"""

from pandocfilters import toJSONFilters, Str, Plain, elt, Image, \
    Strong, Emph, RawInline, Para
import re, textwrap, os

# Figure constructor not included in pandocfilters
Figure = elt('Figure', 3)

# Reference regex pattern used to extract id_tag (for cross-referencing)
REF_PAT = re.compile(r'\[?@([^\s\]]*)\]?')

# Types of chemistry figures supported by LaTeX (e.g., with achemso)
ALT_LATEX_FIGS = ['scheme', 'chart', 'graph']
CITE_KEY = 'ref'

# Dictionaries to hold id tags and count figure classes.
known_ids = {}
known_classes = {}


def to_clip(text):
    """Hack for debugging. Will copy text to clipboard so that it can be
    viewed without interfering with filter.
    """
    cmd = 'echo ' + str(text) + ' | pbcopy'
    os.system(cmd)


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
    if key == 'Figure':
        # Extract key parts of Figure.
        fig_attrs = val[0]
        fig_caption = val[1]
        if fig_attrs[0]:
            image_id = fig_attrs[0]

        # Image is a subset of the figure.
        image = val[2][0]['c'][0]
        image_attrs = image['c'][0]
        image_class = image_attrs[1][0]
        image_caption = image['c'][1]
        image_target = image['c'][2]

        if image_class and fig_caption:
            # Go through key/value pairs and extract into dictionary.
            keys = {}
            for key_pair in image['c'][0][2]:
                keys[key_pair[0]] = key_pair[1]

            # Increment counter for figure types.
            if image_class in known_classes:
                known_classes[image_class] += 1
            else:
                known_classes[image_class] = 1

            # Assign figure/scheme/chart/graph number.
            known_ids[image_id] = str(known_classes[image_class])

            if fmt in ['latex','pdf']:
                # Locate wrapfig-relevant attributes. If found, set
                # latex_wrap to True and read size and position (optional).
                latex_wrap = False
                latex_wrap_pos = 'r' # Default position
                latex_fig_place = False
                latex_suffix = ""
                if 'wwidth' in keys:
                    latex_wrap = True
                    latex_size = keys['wwidth']
                if 'wpos' in keys:
                    latex_wrap_pos = keys['wpos']
                if 'lpos' in keys:
                    latex_fix_place = True
                    latex_fig_place_pos = keys['lpos']
                if 'lts' in keys:
                    latex_suffix = keys['lts']

                # Only use "\caption" command if caption is not empty.
                if fig_caption != []:
                    caption_text = ([RawInline(fmt, r"\caption{")]
                                   + fig_caption[1][0]['c']
                                   + [RawInline(fmt, r"}")])
                else:
                    caption_text = []

                if latex_wrap:
                    raw_text = ([RawInline(fmt, textwrap.dedent(r"""
                        \begin{{wrapfloat}}{{{image_class}}}{{{pos}}}{{{size}}}
                        \centering
                        \includegraphics{{{file}}}
                        """.format(
                                image_class=image_class+latex_suffix,
                                file=image_target[0],
                                size=latex_size,
                                pos=latex_wrap_pos)))]
                        + caption_text
                        + [RawInline(fmt, textwrap.dedent(r"""
                        \label{{{id_tag}}}
                        \end{{wrapfloat}}
                        """.format(
                                image_class=image_class+latex_suffix,
                                id_tag=image_id)))])
                elif latex_fig_place:
                    raw_text = ([RawInline(fmt, textwrap.dedent(r"""
                            \begin{{{image_class}}}[{pos}]
                            \centering
                            \includegraphics{{{file}}}""".format(
                                    image_class=image_class+latex_suffix,
                                    pos=latex_fig_place_pos,
                                    file=image_target[0])))]
                            + caption_text
                            + [RawInline(fmt, textwrap.dedent(r"""
                            \label{{{id_tag}}}
                            \end{{{image_class}}}
                            """.format(
                                    image_class=image_class+latex_suffix,
                                    id_tag=image_id)))])
                else:
                    raw_text = ([RawInline(fmt, textwrap.dedent(r"""
                        \begin{{{image_class}}}
                        \centering
                        \includegraphics{{{file}}}""".format(
                                image_class=image_class+latex_suffix,
                                file=image_target[0])))]
                        + caption_text
                        + [RawInline(fmt, textwrap.dedent(r"""
                        \label{{{id_tag}}}
                        \end{{{image_class}}}
                        """.format(
                                image_class=image_class+latex_suffix,
                                id_tag=image_id)))])
                return Para(raw_text)
            else:
                # Add label to caption for non-LaTeX output.

                # Default labels, suffix, and format
                label = [Strong([Str(image_class.capitalize() + " ")])]
                suffix = [Strong([Str(". ")])]

                if 'fig-abbr' in meta:
                    if image_class in meta['fig-abbr']['c']:
                        label = meta['fig-abbr']['c'][image_class]['c']
                    if 'suffix' in meta['fig-abbr']['c']:
                        suffix = meta['fig-abbr']['c']['suffix']['c']

                # Label takes format of abbreviation.
                if label[0]['t'] == 'Strong':
                    number = [Strong([Str(known_ids[image_id])])]
                elif label[0]['t'] == 'Emph':
                    number = [Emph([Str(known_ids[image_id])])]
                else:
                    number = [Str(known_ids[image_id])]

                new_caption = label + number + suffix + image_caption
                new_image = Image(image_attrs, new_caption, image_target)
                new_figure = Figure(fig_attrs, [None, [Plain(new_caption)]],
                                    [Plain([new_image])])

                return new_figure


def main():
    toJSONFilters([process_images, parse_refs])


if __name__ == '__main__':
    main()
