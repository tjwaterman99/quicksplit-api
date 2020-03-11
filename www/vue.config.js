var path = require('path');

module.exports = {
	runtimeCompiler: true,
	configureWebpack: {
    resolve: {
      alias: {
        "components": path.resolve(__dirname, 'src/components'),
				"@scss": path.resolve(__dirname, 'src/assets/scss')
      }
    }
  }
}
