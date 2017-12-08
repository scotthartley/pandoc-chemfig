# pandoc-chemfig: A pandoc filter for alternate figure types, cross-referencing, and text-wrapping

pandoc-chemfig is a [pandoc][] filter written in Python 3. It does three things to facilitate scientific writing (particularly in chemistry): It enables alternate figure types (Schemes, Charts, and Graphs in addition to Figures); it implements a simple form of cross-referencing to keep track of said figures; and it takes advantage of the LaTeX [wrapfig][] package to turn on text wrapping in LaTeX/pdf output.

For LaTeX output, pandoc-chemfig makes use of the native commands (e.g., to add labels to captions and for cross-referencing). For all other output formats, the filter takes care of the caption labels and numbering itself.

## Installation

For LaTeX/pdf output, the alternate figure environments must be somehow defined, probably by loading a package such as [chemscheme][] or [achemso][]. Similarly, the [wrapfig][] package must be installed and loaded if this feature is going to be used. 

## Usage

Unlike my previous attempts at similar functionality ([pandoc-wrapfig][], [pandoc-figref][]), pandoc-chemfig produces cleaner pandoc markdown. Image types and position info are specified as image attributes. For example:

```
![Scheme caption.](path/to/scheme.pdf){#sch-label .scheme wwidth=0in wpos=l}
```

Inserts a new "scheme" (`.scheme`). Assuming this is the second scheme in the document, the caption will show up as "**Scheme 2.** Scheme caption." in non-LaTeX output and as defined by the template in LaTeX output. Its number can be referenced in the text with `@sch-label`. In LaTeX/pdf output, it will use the wrapfig package and pass along the `wwidth` and `wpos` attributes; in this case, the figure will float on the left (`wpos=l`) with the width set according to the inherent width of the figure (`wwidth=0in`).

The script ignores images with no caption text. If these need to be included, an escaped space (`![\ ](path/to/fig){#label .figure}`) can be used.

In addition to enabling text wrapping, standard LaTeX figure placement can be specified using the `lpos` attribute. For example, setting `lpos=H` for a figure will result in the LaTeX code `\begin{figure}[H]`.

The default label formatting in non-LaTeX output can be overridden by passing the `fig-abbr` variable as metadata. For example, including the following:

```
fig-abbr:
    figure: "**Fig.**\\ "
    scheme: "**Sch.**\\ "
    suffix: "\\ |\\ "
```

will yield captions of the form "**Sch. 1** | Caption." Note that the number takes the format of the label (bold, italics, or nothing). Spaces need to be escaped with the double backslashes. Changes to the label in LaTeX/pdf output must be done through the template (or header-includes metadata).

The (rudimentary) cross-referencing syntax hijacks pandoc's citation markup and is intended to mix nicely with other cross-referencing filters (e.g., [pandoc-eqnos][], [pandoc-tablenos][]).

[pandoc]: http://pandoc.org
[wrapfig]: https://www.ctan.org/pkg/wrapfig?lang=en
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos
[chemscheme]: https://www.ctan.org/pkg/chemscheme?lang=en
[achemso]: https://www.ctan.org/pkg/achemso?lang=en
[pandoc-wrapfig]: https://github.com/scotthartley/pandoc-wrapfig
[pandoc-figref]: https://github.com/scotthartley/pandoc-figref
