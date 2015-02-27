module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

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
    },
    jshint: {
      all: ['Gruntfile.js', 'backend/**/*.js', 'public/**/*.js'],
      options: {
        ignores: ['public/bower_components/**/*.js'],
        jshintrc: true
      }
    }
  });

  grunt.registerTask('default', ['env:dev', 'jshint', 'nodemon:dev']);
};
