var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

// const VueLoaderPlugin = require('vue-loader/lib/plugin')
const { VueLoaderPlugin } = require('vue-loader')

module.exports = {
  context: __dirname,
  mode: 'development',

  entry: {
    'case-status': './assets/js/case-status',
    'case': './assets/js/case',
  }, // entry point of our app. assets/js/index.js should require other js modules and dependencies it needs

  output: {
      path: path.resolve('./assets/bundles/'),
      // filename: 'bundle.js'
      filename: "[name].js",
  },

  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.(scss|css)$/,
        use: [
            "vue-style-loader",
            "css-loader",
            "sass-loader"
        ]
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      },
    ]
  },
  resolve: {
   alias: {
    // vue$: "vue/dist/vue.esm.js"
    // 'vue': '@vue/runtime-dom'
    'Vue': 'vue/dist/vue.esm-bundler.js',
   },
    // modules: ['node_modules', 'bower_components'],
    extensions: [".*", ".js", ".vue", ".json"]
  },
  plugins: [
    // new BundleTracker({filename: './webpack-stats.json'}),
    new VueLoaderPlugin(),
  ],
}