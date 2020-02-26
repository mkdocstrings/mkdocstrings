# FAQ

## Getting started

### Installation

To create a documentation install __mkdocstrings__ and the libraries it depends on.  

```bash
# Required
python3.6 -m pip install mkdocstrings
python3.6 -m pip install mkdocs==1.0.4

# Only if you want to use the material theme
python3.6 -m pip install mkdocs-material
```

### In code documentation

If you want mkdocstrings to document your code you have to use the right docstring format. In general the google docstring format is the right one. If you have any more questions you go [here](./README.md#docstrings-format).  

### Configuring the docs

Like in mkdocs you configure your docs in the *mkdocs.yml*.  
All the files, for example the *index.md* refere to a file in the *docs/* folder in your repo.  
If the *index.md* should be the same as the *README.md* you can create a symlink with  
`ln -rs ../README.md index.md`  

```yml
# mkdocs.yml

site_name: "Your site name"
site_description: "Some description"
site_url: "Your site"
repo_url: "Git repo url"
repo_name: "pawamoy/mkdocstrings"

nav:
  - Overview: "index.md"
  - Reference:
      - Documenter: "reference/documenter.md"

theme:
  name: "material"

# Extra css can be added in a extra file
extra_css:
  - custom.css

plugins:
  - search
  - mkdocstrings:
      watch:
        - src/your-source-code-folder
```

To add your documented source to you documentation you have to add the reference to your source code in a markdown file in the docs folder.  

```md
# docs/reference/documenter.md

# Python import path to the file 
::: python-module-name.file-name
```

Add some custom css

```css
// docs/custom.css

// Just some example css
body{
    background: red
}

```

### Creating the docs

Run the following command in the terminal: 

__Serve:__

```bash
# This adds the src folder to the python path so the python module can be found and serves the mkdocs
PYTHONPATH=src mkdocs serve
```

__Build:__

```bash
PYTHONPATH=src mkdocs build
```

## Wrapper functions

If you are using wrapper functions and want to document the wrapped function the source code and args of the wrapper function will be displayed in the  source code preview.  

![source code](https://user-images.githubusercontent.com/46561026/75286190-5662db00-5818-11ea-9881-f38f3067faf6.png)

![docs](https://user-images.githubusercontent.com/46561026/75286236-75fa0380-5818-11ea-907f-4f1889236854.png)

The solution is to use the functools python provides (see this [StackOverflow Post](https://stackoverflow.com/questions/30799700/function-name-of-wrapped-function)).
