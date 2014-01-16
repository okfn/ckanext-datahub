//npm install grunt grunt-cli grunt-contrib-uglify grunt-contrib-imagemin grunt-contrib-copy grunt-contrib-watch grunt-contrib-cssmin grunt-contrib-less
module.exports = function(grunt) {
  var pkg = grunt.file.readJSON('package.json');

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-imagemin');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-less');

  grunt.file.setBase('.');

  // Project configuration.
  grunt.initConfig({
    pkg: pkg,
    cssmin: {
      combine: {
        files: {
          'ckanext/datahub/public/assets/styles/core.css':
            [
              '../ckan/ckan/public/css/boilerplate.css',
              '../ckan/ckan/public/css/bootstrap.min.css',
              '../ckan/ckan/public/base/css/main.css',
              '../ckan/ckan/public/scripts/vendor/jqueryui/1.8.14/css/jquery-ui.custom.css',
              '../ckan/ckan/public/css/chosen.css',
              '../ckan/ckan/public/css/forms.css',
              '../ckan/ckan/public/css/style.css'
            ],
          'ckanext/datahub/public/assets/styles/datahub.css': [
              'ckanext/datahub/fanstatic/styles/less/datahub.css',
          ]
        }
      }
    },
    less: {
      options: {
        yuicompress: true
      },
      build: {
        src: 'ckanext/datahub/fanstatic/styles/less/datahub.less',
        dest: 'ckanext/datahub/fanstatic/styles/less/datahub.css'
      }
    },
    imagemin: {
      dynamic: {
        options: {
          optimizationLevel: 3
        },
        files: [{
          expand: true,                  // Enable dynamic expansion
          cwd: 'ckanext/datahub/fanstatic/images/',                   // Src matches are relative to this path
          src: ['**/*.{png,jpg,gif}'],   // Actual patterns to match
          dest: 'ckanext/datahub/public/assets/images/'                  // Destination path prefix
        }]
      }
    }
  });

  // Default task(s).
  grunt.registerTask('default', ['less', 'cssmin','imagemin']);
};