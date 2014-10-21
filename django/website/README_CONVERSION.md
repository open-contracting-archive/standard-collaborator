Conversion
==========

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

POSSIBLE ENHANCEMENT: In this structure, if there is only `01_index.md` in the
original directory then we don't show it and the URL structure could have
`intro/` rather than `intro/index/`.

If you load the root for a tag `/r/<tag>/` you will get redirected so that
`en/` is added to the end.

From `/r/<tag>/en/` you will redirected to the equivalent of `01_xxx/01_yyy`
in the scheme above.  The path will be stored in the database for that tag when
the HTML is generated.

QUESTION: do we actually want to have some sort of index.html at `/r/<tag>/en/` ?
Should the `01_xxx/01_yyy.md` be converted into index.html at the root?  Or
should we respond to the URL `/r/<tag>/en/` by serving up `01_xxx/01_yyy.md` ?
