module.exports = function(grunt) {

  require('load-grunt-tasks')(grunt);

  grunt.initConfig({
    env: {
      dev: {
        NODE_ENV: 'dev'
      }
    },
    nodemon: {
      dev: {
        script: 'app.js'
      }
    },
    jshint: {
      all: ['app.js', 'Gruntfile.js', 'backend/**/*.js', 'public/**/*.js'],
      options: {
        ignores: ['public/bower_components/**/*.js'],
        jshintrc: true
      }
    },
    watch: {
      scripts: {
        files: ['app.js', 'Gruntfile.js', 'backend/**/*.js', 'public/**/*.js', '!public/bower_components/**/*.js', 'public/**/*.html', 'public/**/*.css'],
        tasks: ['jshint']
      }
    }
  });

  grunt.registerTask('serve', ['env:dev', 'nodemon']);
  grunt.registerTask('lint-watch', ['watch']);
  grunt.registerTask('lint', ['jshint']);
};
