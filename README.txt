test2 README

- check 
http://backstage.soundcloud.com/2012/06/building-the-next-soundcloud/
http://backstage.soundcloud.com/2012/08/evolution-of-soundclouds-architecture/

!- Fixed! Add tooltips on home, query and result pages

!- Fixed! Sort by gene symbol in query result window

!- Fixed! Disable selection of checkboxes of the entries displayed after query if they are not in the largest connected component

?- Seems OK! check what is going on with queries on other species (copy species data to weizmann): probably there are no entries with unique uniprots in other species
    - make uniprotaccession, description, geneid from swisprot unique
    - make genesymbol, description from hgnc unique
    - make uniprotaccession from trembl cross-reference, genesymbol from trembl unique
    - make uniprotaccession of interaction databases cross-reference
    - make description of PIG cross-reference

?- Skipped! check if multiple tabs is possible due to registry.sessions["species"]: not expecting to have problems (only mighy cause some confusion in status page if two status pages requested at the same tim

?- Quick fix! exception handling for Add genes (no match for query): keeping the way it is with a more meaningful error message to be displayed on home page

!- Quick fix! need to check job ids of all (in worm nd finishs before): quick fix by checking both nd & ns.

!- Fixed! In guild scores file, equivalant entries field sometimes does not exist.

- revision
    - home
	!- change template
	!- change example 2 species type
	!- add gene symbol / keyword search
	?- switch to gene id network and circumvent calling biana user entity operations (query directly gene ids of gene symbols or at least for running algorithm)
	?- check speed bottleneck (from gene to ueid)
	!- check simultaneous runs
	!- check "telomere" & "heat sensitivity" on yeast - seems ok
	X- add gene file upload - instead provided gene; gene; ... query option
	!- add demo
	!- add retrieve results
	!- add info on database

    - query
	!- give more detailed summary (x in the network, y w/ gene symbol, z in total)
	X- push no gene symbol / geneid entries to the bottom - this is not the case with the proper database
	!- push non-existant in network to the bottom (as a separate table)
	!- check tags 
	!- remove BIANA id, move gene id as first column, make protein name & equivalent entries as tooltip 
	!- add select/deselect all for the "keep" field
	!- check problem with keywords for getting desc
	!- remove add genes
	X- list genes that are no found in case of uploaded genes
	X- check behavior of Add genes
	!- add/highlight matching description 
	!- add method/parameter
	!- check problem in running on cluster
	?- add download these matching proteins and make equivalent entries available in flat file - available in the next step
	X- detecting or highlighting "not" related cases (ex: Diabetes mellitus type 2 -> ZFP57 from type 1)
	X- summarize large fields (e.g. show 20 more)
	?- add network selection (e.g. adding STRING & HumanNet, user defined networks)

    - result
	!- add extra column (or coloring) whether it was seed or not
	!- add go to page number or first/last
	?- add sort by id/score
	X- give info from uniprot on the fly (ajax infobox) or description as tooltip
	!- add rank and move protein info as uniprot tooltip 
	!- split , in gene names as linebreak
	!- add cytoscape web visualization 
	!- add visualization interaction (selection/display)
	!- add links for cytoscapeweb selected nodes 
	!- add ajax for visualization of top 1 - 5 - 10
	!- check layout problems (try to stabilize floating cytoscapeweb)
	!- switch to ajax for displaying results in table
	!- add (potentially) interactions from DrugBank, SIDER, STITCH, miRNA see http://pubs.rsc.org/en/content/articlehtml/2013/mb/c3mb25382a)
	X- check non-connected seeds, probably better use gene-id network 
	!- add network download in sif format, provide a network with only ueids in the output file
	X- add display of more than 10 nodes in visualization
	X- add selection from table in visualization
	X- add modularization (by top scoring cutoff or MCL-like) and their GO enrichment
	X- fixed size for table (on each page it resizes) - may appear uglier
	!- add filtering drugs in visualization
	!- add downloadable drug file
	- scale drug scores by number of all targets
	- non-human results arrange visualization panel

    - doc/manuscript
	- add performance info (avg. running time)
	- list available species
	- comment of coverage
	- comment on how often the data is updated
	- add drug prioritization info
	- case study for drug

