exports.index = function index(req, res) {
  res.sendFile('index.html', {root: __dirname + '/../../public/'});
};
