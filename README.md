# passwd parser
Parse the UNIX passwd and group files and combine the data into a single JSON
output.

### Usage
python passwd_parser.py [-h] [-p PASSWD] [-g GROUP] [-s] [-c] [-o OUTFILE]

```optional arguments:
  -h, --help            show this help message and exit
  
  -p PASSWD, --passwd PASSWD
                        Path to the passwd file. Defaults to /etc/passwd if
                        not provided.
                        
  -g GROUP, --group GROUP
                        Path to the group file. Defaults to /etc/group if not
                        provided.
                        
  -s, --sorted          Sort keys of the JSON string alphabetically.
  
  -c, --compact         Print the JSON string in a compact form. The default
                        setting is to pretty-print the JSON.
                        
  -o OUTFILE, --outfile OUTFILE
                        Specifies a file path to which the JSON string should
                        be written. If omitted or an error occurs, the
                        output is printed to STDOUT.
```
