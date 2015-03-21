exports.index = function(req, res) {
  res.sendFile('index.html', {root: __dirname + '/../../public/'});
};
