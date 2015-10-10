# mungler
A tool to mungle up variables, strings, names and identifiers in web-targeted source code. 

To be utilized with (p)html, css and javascript. Can conserve ajax-functionality in php (or possibly other) files: use `--soft filename1 filename2` option to add files which require this. Tries to find variables that come in from frontend via AJAX (and only those). Strings in tese get mungled if an equal identifier has been found previously.

Developement is in beta phase. Do not use in production environment altough the end result is non-destructive. 

The output files should appear in a subdirectory named "mungled" in your present working dir. Prints key-value-pairs to tdout which contains original identifiers and their new nominators.

### Usage:
`python javascriptMungler.py [filenames] [options [arguments]]`
The following assumptions are made:
- .js-files do not contain strings that are to be presented to the end-user.
- .phtml-files contain js-templates that have their variable-names in asp-style tags.
- .php-files have the identifiers/properties of ajax-requests inside strings. 
- Reserved words are listed in the script. Currently covers standard ECMAScript (v6), some common browser-related calls, jQuery, Backbone and Underscore. Defining custom word-lists is not yet possible.
- Pipe output to a textfile if a sourcemap is needed (ie. for partial updates later on).

### Options:
`-n, --reserved [files]`Reads a list of reserved words from a file

`-i, --skipped [files]` List of files to be skipped. Defaults currently to *vendor* , which is meant to leave included third party code untouched (ie. source/js/vendor/, backend/vendor/). Can be full pathnames or names of single directories. Uses absolute pathnames when given. If a single filename is given, it is ignored in every encounter.

`-m, --map [mapfile]` Use a mapfile of identifiers from a previous run. Good for gradually adding / updating single files to a larger project.

> ie. `singlepage.html -m mapfileOfBigProject.txt` mungles a singlepage.html file in accordance to a bigger project which has been mungled earlier. Uses the same identifier-names as in the previous project.  **Not fully implemented**

`-s, --soft [files]` Do not search for new identifiers from given files. Instead, searches only from strings, and only for instances found earlier and mungles those and only those. This is for backend files to find identifiers in ajax-requests.

> ie. `jsclient.js -s serverpage.php` Mungles the js-file first. The identifiers in serverpage.php are not touched, except the ones which appear in strings and have been found in jsclient.js.

`-R, --recursive` Scans paths recursively. 

`-r, --reverse, --reversemap [mapfile]` Revert changes. Needs a mapfile which is generated as the default output. **Not fully implemented**

`-n, --reserved [files]` Add reserved words from an external file. The format used is quoted strings (ie. "string", "string", "string"). Given identifiers will not get mungled. You can send in any kinds of files, actually.

`-w, --identifiers [identifiers]` Add reserved words from the command line. These will not get mungled.

### Changelog:

#### 0.3.1
Functionality:
- Added `--reverse` to revert changes.
- Added `--reserved` to input reserved words from external file(s).
Code structure:
- Code follows (mostly) good conventions and is in english from now on.
- There are comments which are up to date.
- Overall robustness and readability

#### 0.3
- Reformatted codebase structure (classes, maintainability in general)
- Changed to english

#### 0.2
- Initial beta release

### History:
The tool was created for a certain web site -project. It is now flexible enough to squeeze out working versions of other similar projects as well. Please, do not use in production environment :)
