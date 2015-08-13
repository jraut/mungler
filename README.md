# mungler
A tool to mungle up variables, id-fields and most nominators in source code. 

To be utilized with (p)html, css and javascript. Can conserve ajax-functionality in php (or possibly other) files: use `--soft filename1 filename2` option to add files which require this.

Developement is still in early beta. Do not use in production environment altough the end result is already non-destructive. Does not account for scoping yet.

The output files should appear in a subdirectory named "mungled" in your present working dir. Stdout prints a mapping that has key-value-pairs of original nominators and their new identities.

### Usage:
`python javascriptMungler.py [filenames] [options [arguments]]`
The following assumptions are made:
- JS-files do not contain strings that are to be presented to the end-user.
- Reserved words are listed in the script. Currently covers standard ECMAScript (v6), some common browser-related calls, jQuery, Backbone and Underscore. Defining custom word-maps is not yet possible.

###Options:
`-R, --recursive` Scans recursively when given a path. If no files have been given, scans from current path.  
`-i, --skipped [files]` List of files to be skipped. Defaults currently to *vendor*, which leaves third party sources untouched.  
`-r, --reverse, --reversemap [mapfile]` Revert changes. Needs a mapfile which is generated as the default output. Needs a map file.  **Not fully implemented**  
`-m, --map [mapfile]` Use a mapfile from a previous run. Good for gradually adding / updating files.
ie. `singlepage.html -m mapfileOfBigProject.txt` mungles a singlepage.html file in accordance to a bigger project which has been mungled earlier. Remember to capture the output to a textfile to facilitate sourcemapping.  
`-s, --soft [files]` Do not search for new variables from given files. 
ie. `jsclient.js -s serverpage.php` Mungles the js-file first. The variables and other names in serverpage.php are not touched, except the ones which appear to be ajax-parameters used in jsclient.js.


###History:
The tool was created for one certain web site. It is now flexible enough to squeeze out working versions of other pages as well. The developement is currently on hold.
