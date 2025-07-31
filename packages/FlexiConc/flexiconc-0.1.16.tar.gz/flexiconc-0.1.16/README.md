# RC21

The Reading Concordances in the 21st Century (RC21) project focuses on developing tool-independent methodologies for reading concordances, advancing corpus linguistics by designing user-driven algorithms and exploring innovative applications of textual data analysis in the digital humanities. As part of the RC21 project, we are developing FlexiConc.

## Prerequisites

- Python >= 3.9

- suitable virtualenv or conda environment recommended

- lots of Python packages **TODO** complete list, preferably as `requirements.txt` file (Philipp uses Pipenv, but that doesn't work for us Anaconda people)

- Redis datastore server, as described here: https://redis.io/docs/getting-started/installation/
  - hopefully sufficient to run a temporary server from user account
  - on macOS: `brew services run redis`

## FlexiConc configuration

Copy `flexiconc_config_default.ini` to `flexiconc_config.ini`, then set `CWB_REGISTRY_DIR` to your CWB local registry dir.

**TODO** Is this really necessary? CWB should be set up to automatically use the global registry, so not specifying a registry dir at all should work out of the box on most installations.


## Flexiconc-WebApp

Run the FlexiConc Web app with

``` sh
cd Flexiconc-WebApp
flask --app flask_app.py run
```

The Flexiconc-WebApp should normally run on http://127.0.0.1:5000

## FlexiConc
FlexiConc implements various algorithms to support the four concordance reading strategies identified within the RC21 project in form of `flexiconc` Python package.

FlexiConc is not a corpus query tool, but rather works with concordances retrieved from other tools. The main functionalities of FlexiConc are implemented within the Concordance class, which is declared in `concordance.py`.

### Concordance Class

The `Concordance` class provides a structured and intuitive approach to work with linguistic concordances, focusing on representing the operations as a tree, ensuring traceability, and reproducibility of the results.

#### Key Attributes

####  `data`
- **Type**: `pandas.DataFrame`
- **Description**: Holds the concordance data retrieved from corpus queries and augmented and resorted through subsequent operations.

Columns:

* ``match`` — corpus position of the first token matching the query
* ``matchend`` — corpus position of the last token matching the query
* ``context`` — corpus position of the first token of the context
* ``contextend`` — corpus position of the last token of the context
* ``dataframe`` — Pandas dataframe containing the whole concordance line (see below)
* structural attributes (if applicable)
* ``id`` — number of concordance line (starting with 0)
* columns with information generated during concordance processing

A concordance line is represented as a Pandas dataframe:
* ``cpos`` — corpus position of a token
* ``offset`` — distance from the closest token matching the query to the current token
* ``word``, eventually ``lemma`` and ``tag``
* ``space`` — if present, indicates whether there should be a space after token or not in the running text.


#### `operations`
- **Type**: `anytree.Node`
- **Description**: Represents the **operation tree** (see below). Each node in this tree signifies an operation performed on the concordances, enabling users to track and visualize the sequence and hierarchy of applied operations.

#### `operations_count`
- **Type**: `int`
- **Description**: Maintains a count of operations performed on the concordances. It is used to assign unique identifiers to new nodes in the operation tree.

#### `active_node`
- **Type**: `int`
- **Description**: Indicates the currently active node in the operation tree. Operations are added as children to the active node, allowing users to control where in the tree new operations are added. **TODO**: make it possible to change the active node in the web app.

#### Operation Tree

Concordance manipulations are treated as a **tree of operations**, which enables users to have a clear visual representation of the sequence and dependencies of the operations performed on the data, including unsuccessful attempts. Each concordance operation can belong to one out of five types (`query`, `sort`, `rank`, `select`, `cluster`) and is represented as a node in the tree, wherein:

- The **root node** represents the initial retrieval of the concordance and is always of type `query`.
- **Child nodes** represent operations performed on the data, forming branches that illustrate different sequences of operations.

**TODO** Visualization of a given node in the Operations Tree would involve:

- tracing the path from the root to the node and applying the last Sorting/Ranking operation
- applying a conjunction of all Selecting operation on this path
- *think about clustering*
 

#### Example of the Operations Tree Structure

```
operation0 | query | retrieve_from_cwb | {'registry_dir': '/home/apiperski/Documents/CWB/registry/', 'corpus_name': 'DICKENS', 'query': '[word="stomach"]', 'p_show': ['word', 'lemma', 'pos'], 's_show': ['text_id']}
└── operation1 | sort | sort | {'sort_by': [{'type': 'p', 'attr': 'word', 'offset': 1}, {'type': 's', 'attr': 'text_id'}], 'language': 'en_GB'}
    ├── operation2 | rank | rank_by_search_term | {'search_term': 'PP\\$', 'p': 'pos', 'l': -5, 'u': 5, 'positive': True, 'case_sensitive': False}
    │   └── operation3 | select | select_by_search_term | {'search_term': '^[a-e]', 'p': 'word', 'l': -2, 'u': -2, 'positive': True, 'case_sensitive': False}
    │       └── operation6 | cluster | cluster_lexical_links_and_bonds | {'p': 'word', 'case_sensitive': False, 'l': -5, 'u': 5, 'ignore_same_text_links': True, 'threshold': 1}
    └── operation4 | rank | rank_by_number_of_rare_words | {'language': 'en', 'threshold': 2000, 'p': 'word', 'l': -5, 'u': 5}
        └── operation5 | cluster | cluster_pos_tree | {'p': 'pos', 'min_cluster_size': 5, 'max_levels': 3, 'l': -5, 'u': 5, 'examples': 3}
```

#### Data Retrieval

Data for an instance of the Concordance class can be retrieved from different sources:

- **CWB (Corpus Workbench)** with `retrieve_from_cwb()`.
- **TODO** **CLiC** with `retrieve_from_clic()`.

#### Key Methods

`sort(sort_by=[], language='en_GB')`

Sorts the lines based on provided criteria and language-specific sorting rules.

`rank_by_search_term(...)`

Ranks the lines by the occurrence of a specified search term in the specified context window.

`rank_by_number_of_rare_words(...)`

Ranks lines based on the number of rare words, according to language-specific frequency lists.

`select_by_search_term(...)`

Selects lines (not) containing a specified search term.

`cluster_pos_tree(...)`

Generates a part-of-speech tree clustering of the lines.

`cluster_lexical_links_and_bonds(...)`

Forms clusters of lines based on lexical links and bonds.

**TODO** More detailed descriptions of algorithms to be made available in docstring in the respective `.py` files in `/operations` and then as package documentation. Currently only sorting and ranking have been provided with decent docstrings.

---

# THIS IS OLD. DON'T TRUST ANYTHING BELOW THIS LINE
**sort-and-cluster.ipynb**
A Jupyter Notebook to perform corpus queries, display search results, sort and cluster them, and store them as ``xlsx`` in the ``concordances`` folder.

**concordance.py**
Define functions to get concordances from CWB and SketchEngine using functions ``cwb`` and ``sketchEngine`` and to make them compatible with the ``cwb-ccc`` data model.

A concordance is a Pandas dataframe with:

* ``match`` — corpus position of the first token matching the query
* ``matchend`` — corpus position of the last token matching the query
* ``context`` — corpus position of the first token of the context
* ``contextend`` — corpus position of the last token of the context
* ``dataframe`` — Pandas dataframe containing the whole concordance line (see below)
* structure attributes (if applicable)
* ``id`` — number of concordance line (starting with 0)
* columns used as keys for sorting and columns showing clustering (added when processing the concordance)

A concordance line is represented as a Pandas dataframe:
* ``cpos`` — corpus position of a token
* ``offset`` — distance from the closest token matching the query to the current token
* ``word``, eventually ``lemma`` and ``tag``
* ``space`` — if present, indicates whether there should be a space after token or not in the running text.

``formatConcordanceLine`` is a function to output concordance line in a human-readable way.

**simpleMostTypicalExamples.ipynb**: load a concordance from SketchEngine/BNC and sort it to get a number of typical examples of different types at the top

    make a frequency list of lemmas for KWIC-1 and KWIC+1

    for each example: basic_score = rel_freq(KWIC-1) * rel_freq(KWIC+1)
  
    for each example, recalculated on each iteration: adjusted_score = basic_score * ((1 - rel_freq(KWIC-1) in selected) * (1 - rel_freq(KWIC+1) in selected)))\*\*desired_variability
  
    select the example with maximum score
    
    repeat until the desired number of examples is reached

**dppy-spacy.ipynb**: a sandbox for playing with DPP (Determinantal Point Process). As of now, it only works with word embeddings rather than concordance lines.
