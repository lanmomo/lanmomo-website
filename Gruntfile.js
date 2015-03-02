module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

  grunt.initConfig({
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
    },
    watch: {
      scripts: {
        files: ['Gruntfile.js', 'backend/**/*.js', 'public/**/*.js', '!public/bower_components/**/*.js', 'public/**/*.html', 'public/**/*.css'],
        tasks: ['jshint', 'env:dev']
      }
    },
    express: {
      dev: {
        options: {
          script: 'app.js'
        }
      }
    }
  });

  grunt.registerTask('default', ['env:dev', 'jshint', 'express:dev', 'watch']);
};
