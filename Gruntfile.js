//npm install grunt grunt-cli grunt-contrib-uglify grunt-contrib-imagemin grunt-contrib-copy grunt-contrib-watch grunt-contrib-cssmin grunt-contrib-less
module.exports = function(grunt) {
  var pkg = grunt.file.readJSON('package.json');

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-less');

  grunt.file.setBase('.');

  // Project configuration.
  grunt.initConfig({
    pkg: pkg,
    less: {
      options: {
        yuicompress: false
      },
      build: {
        src: 'ckanext/datahub/fanstatic/styles/less/datahub.less',
        dest: 'ckanext/datahub/fanstatic/styles/datahub.css'
      }
    },
    watch: {
		files: "ckanext/datahub/fanstatic/styles/less/*.less",
		tasks: ["less"]
	}
  });

  // Default task(s).
  grunt.registerTask('default', ['less']);
};