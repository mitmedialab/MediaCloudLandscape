sigma.prototype.degreeToSize = function(direction) {
  // this.iterNodes(function(node){
  //   node.size = node.degree;

  // }).draw();
  // console.log('here');
  var initialSize = 1;
  var nodes = this.graph.nodes();
  
  // second create size for every node
  for(var i = 0; i < nodes.length; i++) {
    var degree = this.graph.degree(nodes[i].id, direction);
    nodes[i].size = initialSize * Math.sqrt(degree);
  }
  
  this.refresh();
};