var servers = {};

exports.updateServers = function (req, res) {
  var server = req.body;
  servers[server.hostname] = server;
  res.status(200).json({message: "Success", data: servers});
};

exports.getServers = function (req, res) {
  res.status(200).json(servers);
}
