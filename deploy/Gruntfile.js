module.exports = function(grunt) {
    grunt.initConfig({
        cacheBust: {
            options: {
                encoding: 'utf8',
                algorithm: 'md5',
                length: 16,
            },
            assets: {
                files: [{
                    expand: true,
                    cwd: '../tmp/',
                    baseDir: '../tmp/',
                    src: ['index.html']
                }]
            }
        }
    });

    require('load-grunt-tasks')(grunt);
};
