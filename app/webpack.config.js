var path = require("path")
var webpack = require('webpack')

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
    'Vue': 'vue/dist/vue.esm-bundler.js',
   },
    extensions: [".*", ".js", ".vue", ".json"]
  },
  plugins: [
    new VueLoaderPlugin(),
  ],
}