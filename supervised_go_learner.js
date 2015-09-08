// include WGo

var BOARD_SIZE = 19*19;

var data_from_sgf = function(filename) {
	if (filename === null) {
		filename = "games/Pro10-1964-1.sgf";
	}

	fr = new FileReader();
	fr.readAsText(filename);

	return fr;
	// load up an SGF file
	// initialize a Board object (or player?) from WGO

	// for each move:
		// add prepare_position(current_schema, current_turn) to x
		// add move [or perhaps get_onehot(move)] to y

	// return (x, y)
}

var prepare_position = function(schema, turn, side_length) {
	if (side_length === null) {
		side_length = 19;
	}
	// Essentially, we treat every position as black to play
	var flat = schema.map(function(item) {return item * turn});
	var output = [];
	for (var i = 0; i < side_length; i++) {
		output.push(flat.slice(i*side_length, side_length));
	}

	return output;
}

var get_onehot = function(x, y){
	var output = Array.apply(null, Array(BOARD_SIZE)).map(Number.prototype.valueOf,0);
}

var get_trainer = function(){
	layer_defs = [];
	layer_defs.push({type:'input', out_sx:19, out_sy:19});
	layer_defs.push({type:'conv', sx:5, filters:128, stride:1, pad:0, activation:'relu'});
	layer_defs.push({type:'conv', sx:3, filters:16, stride:1, pad:2, activation:'relu'});

	layer_defs.push({type:'softmax', num_classes:BOARD_SIZE});

	net = new convnetjs.Net();
	net.makeLayers(layer_defs);

	trainer = new convnetjs.SGDTrainer(net, {method:'adadelta', batch_size:32, l2_decay:0.001});
	return trainer;	
}
