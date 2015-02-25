module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

  //TODO jshint
  grunt.initConfig({
    nodemon: {
      dev: {
        script: 'app.js'
      }
    },
    env: {
      dev: {
        NODE_ENV: 'dev'
      }
    }
  });

  grunt.registerTask('default', ['env:dev', 'nodemon:dev']);
};
