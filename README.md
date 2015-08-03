# mungler
A tool to mungle up variables, id-fields and most nominators in source code. 

To be utilized with (p)html, css and javascript. Can conserve ajax-functionality in php (or possibly other) files: use `--soft filename1 filename2` option to add files which require this.

Developement is still in early beta. Do not use in production environment altough the end result is non-destructive. 

Your mungled files should appear in a subdirectory named "mungled" in your present working dir.



### USAGE:
`python javascriptMungler.py [filenames] [options [arguments]]`

###Options:
`-R, --recursive` Scans recursively when given a path. If no files have been given, scans from current path.  
`-i, --skipped [files]` List of files to be skipped. Defaults currently to *vendor*, which leaves third party sources untouched.  
`-r, --reverse, --reversemap [mapfile]` Revert changes. Needs a mapfile which is generated as the default output. Needs a map file**Not fully implemented**  
`-m, --map [mapfile]` Use a mapfile from a previous run. Good for gradually adding / updating files.
ie. `singlepage.html -m mapfileOfBigProject.txt` mungles a singlepage.html file in accordance to a bigger project which has been mungled earlier. Remember to capture the output to a textfile to facilitate sourcemapping.  
`-s, --soft [files]` Do not search for new variables from given files. 
ie. `jsclient.js -s serverpage.php` Mungles the js-file first. The variables and other names in serverpage.php are not touched, except the ones which appear to be ajax-parameters used in jsclient.js.

