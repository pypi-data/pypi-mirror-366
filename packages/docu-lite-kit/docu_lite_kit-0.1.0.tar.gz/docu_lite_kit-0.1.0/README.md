# Docu-lite-kit
Standalone cli/importable components inspired by [docu-lite](https://pypi.org/project/docu-lite/)

The first component here is the ultra-light Python parser:
- Rewritten to be more robust around docstrings
- Packaged to be useable from the command line or imported as a module into other code
- Soon to replace the parser used within docu-lite

Current plans / ideas:
- Add standalone / importable docu-lite-like html rendering components
- Add standalone / importable API delta checkers
  
## Screenshots
<img width="1855" height="988" alt="Capture" src="https://github.com/user-attachments/assets/5a4561c4-08dd-4be8-b6a5-efaaac491a88" />

## 🛠 Installation

Install using pip: open a command window and type

```
pip install docu-lite-kit
```
## 💡 Usage
### Command line:
```
docu-lite-kit.cli [-h] [--out] [--noprint] input.py
```
-  -h = show help
-  --out specifies the output file (JSON format)
-  --noprint = don't print the basic printout to the console 

### Imported as a module:
```
import pybonsai
```

Provides the following three interfaces (see demo_minimal.py):
```
    input_file = r"./demo_minimal.py"
    # parse the doc looking for objects matching a,b,c,d:
    # parser = pybonsai.pbIO(input_file, [ pattern_list =  [a,b,c,d] ])
    # For the pattern list, docstring and body are implied & don't need to be mentioned.
    # The pattern list itself is optional and defaults to ['class', 'def']
    parser = pybonsai.pbIO(input_file)

    # print out the result including the elements a,b,c,d:
    # parser.pbPrint([a,b,c,d])
    # This time 'docstring' and 'body' do need to be explicitly mentioned if wanted in the printout
    # However pattern list is optional and defaults to ['class', 'def', 'docstring']
    # parser.pbPrint( pattern_list = ['def', 'class', 'docstring', 'body'])
    parser.pbPrint(['def', 'class', 'docstring', 'body'])

    # Similar to pbPrint, this dumps the output to a JSON file:
    # parser.pbDumpJSON(JSON_file = 'pybonsai.JSON', pattern_list = ['def', 'class', 'docstring'])
    parser.pbDumpJSON()

```

[PyPI link](https://pypi.org/project/pybonsai/)
