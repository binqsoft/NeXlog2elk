var path = require('path')
var utils = require('./utils')
var webpack = require('webpack')
var config = require('../config')
var merge = require('webpack-merge')
var baseWebpackConfig = require('./webpack.base.conf')
var HtmlWebpackPlugin = require('html-webpack-plugin')
var HtmlWebpackHarddiskPlugin = require('html-webpack-harddisk-plugin')
var FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin')

var devWebpackConfig = merge(baseWebpackConfig, {
  output: {
    publicPath: `http://0.0.0.0:${config.dev.port}${config.dev.assetsPublicPath}`
  },
  module: {
    rules: utils.styleLoaders({sourceMap: config.dev.cssSourceMap})
  },
  // cheap-module-eval-source-map is faster for development
  devtool: '#cheap-module-eval-source-map',
  plugins: [
    new webpack.DefinePlugin({
      'process.env': config.dev.env
    }),
    // https://github.com/glenjamin/webpack-hot-middleware#installation--usage
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(),
    // https://github.com/ampedandwired/html-webpack-plugin
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: 'index.html',
      inject: true,
      alwaysWriteToDisk: true
    }),
    new HtmlWebpackHarddiskPlugin({
      outputPath: path.resolve(path.dirname(path.dirname(__dirname)), 'templates')
    }),
    new FriendlyErrorsPlugin()
  ]
})


// add hot-reload related code to entry chunks
Object.keys(devWebpackConfig.entry).forEach(function (name) {

  devWebpackConfig.entry[name] = [
    `webpack-hot-middleware/client?path=http://0.0.0.0:${config.dev.port}/__webpack_hmr`
  ].concat(baseWebpackConfig.entry[name])
})


module.exports = devWebpackConfig
