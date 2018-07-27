
$(function(){

    $("#content").html('\
        <div id="cytoscapeweb">\
            Cytoscape web content\
        </div>\
	<div id="cytoscapeweb_note">\
	    <center>(Select any node for details)</center>\
	</div>\
    ');

	// id of Cytoscape Web container div
	var div_id = "cytoscapeweb";
	
	// you could also use other formats (e.g. GraphML) or grab the network data via AJAX
	var network_json = ${network_json};
	
	// initialization options
	var options = {
	    // where you have the Cytoscape Web SWF
	    swfPath: "swf/CytoscapeWeb",
	    // where you have the Flash installer SWF
	    flashInstallerPath: "swf/playerProductInstall"
	};

	// visual style 
	var visual_style = {
	    global: {
		backgroundColor: "#E7F0F0"
	    },
	    nodes: {
		shape: {
		    discreteMapper: {
			attrName: "type",
			entries: [
			    { attrValue: "seed", value: "OCTAGON" },
			    { attrValue: "non_seed", value: "OCTAGON" },
			    { attrValue: "drug", value: "DIAMOND" }
			]
		    } 
		} ,
		borderWidth: 3,
		borderColor: "#ffffff",
		size: {
		    defaultValue: 25,
		    continuousMapper: { attrName: "score", minValue: 25, maxValue: 100 }
		},
		color: {
		    discreteMapper: {
			attrName: "type",
			entries: [
			    { attrValue: "seed", value: "#F0A548" },
			    { attrValue: "non_seed", value: "#BDDDB0" },
			    { attrValue: "drug", value: "#5093FF" }
			]
		    }
		},
		labelHorizontalAnchor: "center",
		labelFontSize: 14,
		labelFontWeight: "bold"
	    },
	    edges: {
		width: 3,
		color: "#0B94B1"
	    }
	};
	
	// init and draw
	var vis = new org.cytoscapeweb.Visualization(div_id, options);

	// callback when Cytoscape Web has finished drawing
	vis.ready(function() {
	    // add a listener for when background is clicked
	    vis.addListener("click", "none", function(event) {
	    	handle_click(event);
	    });
	    // listener for when nodes are selected
	    vis.addListener("select", "nodes", function(event) {
	    	handle_select(event);
	    });

	    function handle_select(event) {
                //var nodes = vis.selected("nodes"); //event.target;
                clear();
                print_sub(0);
            }
	    
	    function handle_click(event) {
		clear();
	    }

	    function clear() {
		document.getElementById("cytoscapeweb_note").innerHTML = "<center>(Select any node for details)</center>";
	    }

            function print_sub(start_idx) { // nodes
                var nodes = vis.selected("nodes");
                if(start_idx < 0) {
                    start_idx = 0
                }
                var fields = new Array("xref", "label", "score", "rank", "type");
                var text = ""
                if(nodes.length == 1) {
                    text += "Selected node:";
                } else if(nodes.length > 10) {
                    text += "Selected " + nodes.length + " nodes (only the first 10 are displayed below):";
                } else {
                    text += "Selected " + nodes.length + " nodes:";
                }
                text += "<center>";
		text += '<table id="cytoscapeweb_user_entity_set"> <tr> <th title="Identifier (UniProt or DrugBank Id)">ID</th> <th title="Gene symbol / drug name">Label</th> <th title="Score calculated for the relevance of this entriy with respect to the provided seeds"> GUILD Score</th> <th title="Rank from the top">Rank</th> <th title="Seed or non-seed"> Type </tr>';
                for (var i=0; i < nodes.length; i++) {
                    if(i<start_idx) {
                        continue;
                    }
                    if(i>start_idx+9) {
                        break;
                    }
                    //document.getElementById("cytoscapeweb_note").innerHTML += '<tr>' + nodes[i].data["label"] + '</tr>'; 
                    var inner_text="oddy";
                    if(i%2 == 0) {
                        inner_text="eveny";
                    }
                    text += '<tr>'; 
		    for (var k=0; k < fields.length; k++) {  
			var inner_text2 = ""
			if (fields[k] == "xref" && nodes[i].data["type"] != "drug") {
			    var values = nodes[i].data[fields[k]].split(";");
			    for(j=0; j<values.length; j++) {
				inner_text2 = "<a href='http://www.uniprot.org/uniprot/" + values[j] + "'>" + values[j] + "</a>";
			    }
			} else if(fields[k] == "label" && nodes[i].data["type"] == "drug") {
			    inner_text2 = "<a href='http://www.drugbank.ca/drugs/" + nodes[i].data[fields[k]] + "'>" + nodes[i].data[fields[k]] + "</a>";
			} else {
			    inner_text2 = nodes[i].data[fields[k]]
			}
			text += '<td class="' + inner_text + '"> <p> ' + inner_text2 + '</p> </td>';
		    }
		    text += '</tr>'; 
		}
		text += '</table>'; 
                if(nodes.length > 10) {
                    text += '<a href="javascript:print_sub('+(start_idx-10)+');"> &lt; &lt; previous 10 </a> || ';
                    text += '<a href="javascript:print_sub('+(start_idx+10)+');"> next 10 &gt; &gt; </a>';
                }

		text += "</center>";
		document.getElementById("cytoscapeweb_note").innerHTML = text;
	    }
	    }

	    );

	    function toggleFilter(val) {
		if(val) {
		    vis.removeFilter("nodes", true);
		} else {
		    vis.filter("nodes", function(node) { return node.data["type"] != "drug"; }, true);
		}
	    }    

    $("#filter").change(function(evt) {
        toggleFilter($("#filter").is(":checked"));
    });

    vis.draw({ network: network_json, visualStyle: visual_style });
        
});
