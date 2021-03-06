Conversion
==========

Directory and URL Structure
---------------------------

We convert from a commit of the standards repo into HTML fragments.  We assume
the docs in the standards repository are in `standards/docs/` (from the root of
the repository).  The directory structure inside that directory is assumed to
be something like:

    en/
        01_intro/
            01_index.md
        02_main/
            01_purpose.md
            02_background.md
            ...
        03_definitions/
            01_vocabulary.md
        ...
    es/
        01_intro/
            01_index.md
        02_principal/
            01_proposito.md
            02_fondo.md
            ...

This is strictly `<lang>/<num>_<dirname>/<num>_<filename>.md` - we only expect
the markdown files at the one level of the directory structure.

From that we will construct an HTML tree like:

    en/
        intro/
            index.html
        main/
            purpose.html
            background.html
            ...
        definitions/
            vocabulary.html
    es/
        ...

We will also construct a standard menu to prepend to each file - the tabs view.
These will be saved in the above HTML files The links will line up with the URL
structure below.

The above files will then map onto a URL structure of:

    /r/<tag>/
            en/
                intro/index/
                main/purpose/
                main/background/
                main/...
                definitions/vocabulary/
            es/
                ...

If you load the root for a tag `/r/<tag>/` you will get redirected so that
`en/` is added to the end.

From `/r/<tag>/en/` you will redirected to the equivalent of `01_xxx/01_yyy`
in the scheme above.  The path is generated by looking at the exported files.

Markdown Processing
-------------------

For a start, raw HTML can be in the Markdown and that will be passed through
unchanged.

We use the "table of contents" plugin, so you put `[TOC]` in the markdown file
and it generates a table of contents there (as nested `<ul>`).  The python then
extracts that element and puts it in a separate div.

We also can include json and CSV files from the standard repo.  To include json
files, include a div with a `class` of `include-json` and a `data-src` attribute
that contains the path to the file from the root of the standard repo.  For
example:

    <div class="include-json" data-src="standard/example/example.json"></div>

The json will be embedded inside the div, surrounded by `<pre>` and `<code>`
tags.  The json will be syntax highlighted.

To include a CSV file, include a div with a `class` of `include-csv` and a
`data-src` attribute that contains the path to the file from the root of the
standard repo.  You can also include a `data-table-class` attribute containing
the HTML classes you want to be added to the `<table>` element.  For example:

    <div class="include-csv" data-src="standard/example/example.csv"
     data-table-class="table table-striped"></div>

The CSV will be converted into an HTML table with the classes applied.  The
classes in this example are [bootstrap table classes](http://getbootstrap.com/css/#tables).
